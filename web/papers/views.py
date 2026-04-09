import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from src.shared.settings import get_settings

_repo = None


def _get_repo():
    global _repo
    if _repo is None:
        from src.integrations.paper_repository import PaperRepository
        _repo = PaperRepository()
    return _repo


# ── list 페이지 ──────────────────────────────────────────────────────────────

def paper_list(request):
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'latest')
    page = int(request.GET.get('page', 1))

    try:
        repo = _get_repo()
        papers = repo.list_recent_papers(limit=1500)
    except Exception as e:
        return render(request, 'papers/list.html', {
            'error': f'데이터베이스 연결 실패: {e}',
            'page_obj': None,
            'query': query,
            'sort': sort,
        })

    if query:
        q = query.lower()
        papers = [
            p for p in papers
            if q in (p['title'] or '').lower()
            or q in (p['abstract'] or '').lower()
        ]

    if sort == 'upvotes':
        papers.sort(key=lambda p: p.get('upvotes') or 0, reverse=True)

    paginator = Paginator(papers, 21)
    page_obj = paginator.get_page(page)

    return render(request, 'papers/list.html', {
        'page_obj': page_obj,
        'query': query,
        'sort': sort,
    })


# ── detail 페이지 (메타데이터만 즉시 렌더링) ────────────────────────────────

def paper_detail(request, arxiv_id):
    try:
        repo = _get_repo()
        paper = repo.get_paper(arxiv_id)
        if not paper:
            return render(request, 'papers/detail.html', {'error': '논문을 찾을 수 없습니다.'})
        paper = dict(paper)
    except Exception as e:
        return render(request, 'papers/detail.html', {'error': f'데이터베이스 연결 실패: {e}'})

    has_api_key = bool(os.environ.get('OPENAI_API_KEY'))

    return render(request, 'papers/detail.html', {
        'paper': paper,
        'has_api_key': has_api_key,
    })


# ── AJAX: AI overview + key findings ────────────────────────────────────────

def paper_analyze(request, arxiv_id):
    if not bool(os.environ.get('OPENAI_API_KEY')):
        return JsonResponse({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}, status=400)

    try:
        repo = _get_repo()
        paper = repo.get_paper(arxiv_id)
        if not paper:
            return JsonResponse({'error': '논문을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'DB 오류: {e}'}, status=500)

    current_model = get_settings().openai_model

    # 캐시 조회 — 같은 모델로 생성된 overview가 있으면 즉시 반환
    try:
        cached = repo.get_paper_ai_summary(arxiv_id)
        if cached and cached.get('overview') and cached.get('overview_model') == current_model:
            return JsonResponse({
                'overview': cached['overview'],
                'key_findings': cached.get('key_findings') or [],
                'cached': True,
            })
    except Exception:
        pass  # 캐시 조회 실패 시 cache miss로 처리

    # cache miss → LLM 호출
    try:
        fulltext = repo.get_paper_fulltext(arxiv_id) or {}
        chunks = repo.list_paper_chunks(arxiv_id, limit=20)

        paper = dict(paper)
        paper['text'] = fulltext.get('text') or ''
        paper['sections'] = fulltext.get('sections') or []
        paper['chunks'] = chunks
    except Exception as e:
        return JsonResponse({'error': f'DB 오류: {e}'}, status=500)

    try:
        from src.core import analyze_paper_detail
        summary_doc = analyze_paper_detail(paper)
        overview = summary_doc.overview if summary_doc else None
        key_findings = summary_doc.key_findings if summary_doc else []

        if overview:
            repo.upsert_overview(arxiv_id, overview, key_findings, current_model)

        return JsonResponse({
            'overview': overview,
            'key_findings': key_findings,
            'cached': False,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ── AJAX: 상세 요약 생성 ────────────────────────────────────────────────────

def paper_summary(request, arxiv_id):
    if not bool(os.environ.get('OPENAI_API_KEY')):
        return JsonResponse({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}, status=400)

    try:
        repo = _get_repo()
        paper = repo.get_paper(arxiv_id)
        if not paper:
            return JsonResponse({'error': '논문을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'DB 오류: {e}'}, status=500)

    current_model = get_settings().openai_model

    # 캐시 조회 — 같은 모델로 생성된 상세요약이 있으면 즉시 반환
    try:
        cached = repo.get_paper_ai_summary(arxiv_id)
        if cached and cached.get('detailed_summary') and cached.get('summary_model') == current_model:
            return JsonResponse({
                'summary': cached['detailed_summary'],
                'cached': True,
            })
    except Exception:
        pass  # 캐시 조회 실패 시 cache miss로 처리

    # cache miss → LLM 호출
    try:
        fulltext = repo.get_paper_fulltext(arxiv_id) or {}
        paper = dict(paper)
        paper['text'] = fulltext.get('text') or ''
        paper['sections'] = fulltext.get('sections') or []
    except Exception as e:
        return JsonResponse({'error': f'DB 오류: {e}'}, status=500)

    try:
        from src.core.translation_chains import build_summary
        summary_text = paper.get('text') or '\n\n'.join(
            f"[{s['title']}]\n{s['text']}" for s in paper.get('sections', [])
        )
        result = build_summary(
            title=paper['title'],
            authors=paper['authors'],
            text=summary_text,
            sections=paper.get('sections'),
        )
        if result:
            repo.upsert_detailed_summary(arxiv_id, result, current_model)

        return JsonResponse({'summary': result, 'cached': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ── AJAX: 채팅 ───────────────────────────────────────────────────────────────

@require_POST
def paper_chat(request, arxiv_id):
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
        chat_history = body.get('history', [])
    except Exception:
        return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

    if not user_message:
        return JsonResponse({'error': '메시지를 입력하세요.'}, status=400)

    try:
        repo = _get_repo()
        paper = repo.get_paper(arxiv_id)
        if not paper:
            return JsonResponse({'error': '논문을 찾을 수 없습니다.'}, status=404)
        chunks = repo.list_paper_chunks(arxiv_id, limit=20)
    except Exception as e:
        return JsonResponse({'error': f'DB 오류: {e}'}, status=500)

    try:
        from src.core.agent.chatbot import stream_answer_question
        history_tuples = [
            (m['role'], m['content'])
            for m in chat_history
            if m.get('role') in ('user', 'assistant')
        ]
        answer_stream = stream_answer_question(
            user_message,
            context_papers=chunks,
            chat_history=history_tuples,
        )
        answer = ''.join(answer_stream)
    except Exception as e:
        return JsonResponse({'error': f'답변 생성 실패: {e}'}, status=500)

    return JsonResponse({'answer': answer})
