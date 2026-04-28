from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect

from .services import (
    AuthenticationRequiredError,
    PaperNotFoundError,
    build_paper_detail_payload,
    build_paper_list_payload,
)


def paper_list(request: HttpRequest) -> HttpResponse:
    return _render_react_shell()


def paper_list_alias(request: HttpRequest) -> HttpResponse:
    redirect_to = "/"
    if request.META.get("QUERY_STRING"):
        redirect_to = f"{redirect_to}?{request.META['QUERY_STRING']}"
    return redirect(redirect_to)


def paper_list_data(request: HttpRequest) -> JsonResponse:
    try:
        payload = build_paper_list_payload(
            query=request.GET.get("q", ""),
            sort=request.GET.get("sort", "latest"),
            mode=request.GET.get("mode", "search"),
            page=request.GET.get("page", 1),
            user=request.user,
        )
    except Exception as exc:
        return JsonResponse({"error": f"데이터베이스 연결 실패: {exc}"}, status=500)

    return JsonResponse(payload)


def paper_detail(request: HttpRequest, arxiv_id: str) -> HttpResponse:
    if not getattr(request.user, "is_authenticated", False):
        return redirect(f"/login/?next=/papers/{arxiv_id}/")
    return _render_react_shell()


def paper_detail_data(request: HttpRequest, arxiv_id: str) -> JsonResponse:
    try:
        return JsonResponse(build_paper_detail_payload(arxiv_id, user=request.user))
    except AuthenticationRequiredError as exc:
        return JsonResponse({"error": str(exc)}, status=401)
    except PaperNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    except Exception as exc:
        return JsonResponse({"error": f"데이터베이스 연결 실패: {exc}"}, status=500)


def paper_agent(request: HttpRequest) -> HttpResponse:
    return _render_react_shell()


def login_page(request: HttpRequest) -> HttpResponse:
    return _render_react_shell()


def _render_react_shell() -> HttpResponse:
    entry_path = Path(settings.FRONTEND_DIST_DIR) / "index.html"
    if not entry_path.exists():
        return HttpResponse(
            "React build output이 없습니다. frontend에서 npm run build를 먼저 실행하세요.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    return HttpResponse(
        entry_path.read_text(encoding="utf-8"),
        content_type="text/html; charset=utf-8",
    )
