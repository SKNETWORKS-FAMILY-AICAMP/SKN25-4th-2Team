"""개요 생성 프롬프트."""

from langchain_core.prompts import ChatPromptTemplate

OVERVIEW_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 자동 생성 이슈 문서의 문서 작성 도우미입니다. "
        "여러 기사를 읽고 사실 중심의 개요를 작성합니다.",
    ),
    (
        "human",
        "아래는 같은 이슈에 속하는 뉴스 기사들입니다.\n\n"
        "{articles}\n\n"
        "이 이슈 문서의 개요를 3~5문장으로 작성해주세요.\n"
        "- 사용자가 이 섹션만 읽어도 무슨 일이 있었는지 이해할 수 있어야 합니다.\n"
        "- 구체적인 수치, 기관, 인물은 기사에 있을 때만 포함합니다.\n"
        "- 추측, 의견, 전망은 제외합니다.",
    ),
])
