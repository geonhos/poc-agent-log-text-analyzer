"""
Agent Workflow

여러 Agent를 연결하여 파이프라인을 구성하는 워크플로우
"""

from typing import Any, Dict, List, Optional, Union

from .api_call_generator import ApiCallGeneratorAgent
from .base import AgentError, BaseAgent
from .log_analyzer import LogAnalyzerAgent


class AgentWorkflow:
    """
    Agent 워크플로우

    여러 Agent를 순차적으로 실행하여 복잡한 작업을 자동화합니다.

    Example:
        # 로그 파일 분석 → curl 생성
        workflow = AgentWorkflow()
        workflow.add_agent(LogAnalyzerAgent())
        workflow.add_agent(ApiCallGeneratorAgent())

        result = workflow.execute("logs/api.log")
    """

    def __init__(self, name: Optional[str] = None):
        """
        Args:
            name: 워크플로우 이름
        """
        self.name = name or "AgentWorkflow"
        self.agents: List[BaseAgent] = []
        self.results: List[Dict[str, Any]] = []

    def add_agent(self, agent: BaseAgent) -> "AgentWorkflow":
        """
        Agent 추가

        Args:
            agent: 추가할 Agent

        Returns:
            self (메서드 체이닝용)
        """
        self.agents.append(agent)
        return self

    def execute(
        self,
        input_data: Any,
        context: Optional[Dict[str, Any]] = None,
        stop_on_error: bool = False,
    ) -> Dict[str, Any]:
        """
        워크플로우 실행

        Args:
            input_data: 초기 입력 데이터
            context: 실행 컨텍스트 (모든 Agent에 전달)
            stop_on_error: 에러 발생 시 중단 여부 (기본값: False)

        Returns:
            {
                "success": bool,
                "agents_executed": int,
                "results": List[Dict],  # 각 Agent의 결과
                "final_output": Any,    # 마지막 Agent의 출력
                "errors": List[str],    # 발생한 에러 목록
            }

        Raises:
            AgentError: stop_on_error=True이고 에러 발생 시
        """
        context = context or {}
        self.results = []
        errors = []

        current_input = input_data

        for idx, agent in enumerate(self.agents):
            try:
                # Agent 실행
                result = agent.execute(current_input, context)

                # 결과 저장
                self.results.append(
                    {"agent": agent.name, "success": True, "result": result, "error": None}
                )

                # 다음 Agent의 입력 결정
                current_input = self._prepare_next_input(agent, result)

            except Exception as e:
                error_msg = f"{agent.name} 실행 실패: {e}"
                errors.append(error_msg)

                self.results.append(
                    {"agent": agent.name, "success": False, "result": None, "error": str(e)}
                )

                if stop_on_error:
                    raise AgentError(error_msg)

                # 에러 발생 시 빈 입력으로 계속
                current_input = None

        success = len(errors) == 0
        final_output = self.results[-1]["result"] if self.results else None

        return {
            "success": success,
            "agents_executed": len(self.results),
            "results": self.results,
            "final_output": final_output,
            "errors": errors,
        }

    def _prepare_next_input(self, agent: BaseAgent, result: Any) -> Any:
        """
        다음 Agent의 입력 데이터 준비

        Args:
            agent: 현재 Agent
            result: 현재 Agent의 결과

        Returns:
            다음 Agent의 입력
        """
        # LogAnalyzerAgent → ApiCallGeneratorAgent
        if isinstance(agent, LogAnalyzerAgent):
            if isinstance(result, dict) and "api_calls" in result:
                return result["api_calls"]

        # 기본적으로 전체 결과 전달
        return result

    def get_summary(self) -> str:
        """
        워크플로우 실행 결과 요약

        Returns:
            요약 텍스트
        """
        if not self.results:
            return "워크플로우가 아직 실행되지 않았습니다."

        lines = [f"=== {self.name} 실행 결과 ===", ""]

        for idx, result in enumerate(self.results, 1):
            agent_name = result["agent"]
            success = result["success"]
            status = "✓" if success else "✗"

            lines.append(f"{idx}. {status} {agent_name}")

            if not success:
                error = result.get("error", "Unknown error")
                lines.append(f"   에러: {error}")

        success_count = sum(1 for r in self.results if r["success"])
        total_count = len(self.results)

        lines.append("")
        lines.append(f"총 {total_count}개 Agent 중 {success_count}개 성공")

        return "\n".join(lines)

    def clear(self) -> None:
        """워크플로우 초기화 (Agent 목록 및 결과 삭제)"""
        self.agents = []
        self.results = []


# 사전 정의된 워크플로우


def create_log_to_curl_workflow(name: str = "Log to Curl") -> AgentWorkflow:
    """
    로그 → curl 변환 워크플로우 생성

    Args:
        name: 워크플로우 이름

    Returns:
        AgentWorkflow 인스턴스
    """
    workflow = AgentWorkflow(name=name)
    workflow.add_agent(LogAnalyzerAgent())
    workflow.add_agent(ApiCallGeneratorAgent())
    return workflow


def create_log_to_postman_workflow(name: str = "Log to Postman") -> AgentWorkflow:
    """
    로그 → Postman collection 변환 워크플로우 생성

    Args:
        name: 워크플로우 이름

    Returns:
        AgentWorkflow 인스턴스
    """
    workflow = AgentWorkflow(name=name)
    workflow.add_agent(LogAnalyzerAgent())
    workflow.add_agent(ApiCallGeneratorAgent())
    return workflow
