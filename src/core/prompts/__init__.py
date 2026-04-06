"""토픽 분석 프롬프트 템플릿을 모아 노출하는 모듈"""

from .key_findings import KEY_FINDINGS_PROMPT
from .overview import OVERVIEW_PROMPT
from .paper_key_findings import PAPER_KEY_FINDINGS_PROMPT
from .paper_overview import PAPER_OVERVIEW_PROMPT

__all__ = [
    "KEY_FINDINGS_PROMPT",
    "OVERVIEW_PROMPT",
    "PAPER_KEY_FINDINGS_PROMPT",
    "PAPER_OVERVIEW_PROMPT",
]
