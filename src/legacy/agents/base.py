"""
Base Agent

모든 Agent의 기본 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AgentError(Exception):
    """Agent 실행 중 에러"""

    pass


class BaseAgent(ABC):
    """
    Agent 기본 클래스

    모든 Agent는 이 클래스를 상속받아 구현합니다.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Args:
            name: Agent 이름 (기본값: 클래스명)
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Agent 실행

        Args:
            input_data: 입력 데이터
            context: 실행 컨텍스트 (선택적)

        Returns:
            실행 결과

        Raises:
            AgentError: Agent 실행 중 에러 발생 시
        """
        pass

    def _validate_input(self, input_data: Any) -> None:
        """
        입력 데이터 검증

        Args:
            input_data: 입력 데이터

        Raises:
            AgentError: 입력 데이터가 유효하지 않을 때
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.name}>"
