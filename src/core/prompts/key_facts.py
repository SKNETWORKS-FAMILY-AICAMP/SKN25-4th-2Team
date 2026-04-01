"""핵심 사실 추출 프롬프트."""

from langchain_core.prompts import ChatPromptTemplate

KEY_FACTS_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 자동 생성 이슈 문서의 핵심 사실 목록을 작성합니다. "
        "여러 기사에서 공통으로 확인되는 사실만 고릅니다.",
    ),
    (
        "human",
        "아래는 같은 이슈에 속하는 뉴스 기사들입니다.\n\n"
        "{articles}\n\n"
        "핵심 사실 섹션에 들어갈 항목을 작성해주세요.\n"
        "- 2개 이상의 기사가 공통으로 다루는 사실만 포함합니다.\n"
        "- 각 항목은 한 문장으로 씁니다.\n"
        "- 불릿 목록 형태로 출력합니다.\n"
        "- 해석, 관점, 추정은 제외합니다.",
    ),
])
