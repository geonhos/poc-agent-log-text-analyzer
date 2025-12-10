"""
Base LLM

LLM 클라이언트의 기본 인터페이스
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class LLMError(Exception):
    """LLM 실행 중 에러"""

    pass


@dataclass
class LLMResponse:
    """
    LLM 응답

    Attributes:
        content: 응답 텍스트
        model: 사용된 모델명
        usage: 토큰 사용량 정보
        raw_response: 원본 응답 (디버깅용)
    """

    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLM(ABC):
    """
    LLM 기본 클래스

    모든 LLM 클라이언트는 이 클래스를 상속받아 구현합니다.
    """

    def __init__(self, model: str, **kwargs):
        """
        Args:
            model: 모델명
            **kwargs: 추가 설정
        """
        self.model = model
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        텍스트 생성

        Args:
            prompt: 입력 프롬프트
            system: 시스템 메시지
            temperature: 온도 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터

        Returns:
            LLMResponse 객체

        Raises:
            LLMError: 생성 실패 시
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        채팅 형식 대화

        Args:
            messages: 메시지 목록 [{"role": "user", "content": "..."}]
            temperature: 온도
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터

        Returns:
            LLMResponse 객체

        Raises:
            LLMError: 생성 실패 시
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(model={self.model})>"
