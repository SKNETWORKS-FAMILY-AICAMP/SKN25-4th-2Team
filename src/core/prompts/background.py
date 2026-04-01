"""배경 생성 프롬프트."""

from langchain_core.prompts import ChatPromptTemplate

BACKGROUND_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 자동 생성 이슈 문서의 배경 섹션을 작성합니다. "
        "기사에 나온 맥락을 우선 사용하고, 필요한 일반 지식은 명확히 구분합니다.",
    ),
    (
        "human",
        "아래는 같은 이슈에 속하는 뉴스 기사들입니다.\n\n"
        "{articles}\n\n"
        "이 이슈를 이해하기 위한 배경 섹션을 작성해주세요.\n"
        "- 기사에 명시된 배경과 전사를 우선 정리합니다.\n"
        "- 기사 밖의 일반 지식을 보강할 때는 해당 문장 앞에 [일반 배경 정보]를 붙입니다.\n"
        "- 단정적 추정은 피하고 설명형 문체를 유지합니다.",
    ),
])
