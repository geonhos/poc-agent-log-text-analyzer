"""
Log Analyzer Agent

로그 파일 또는 텍스트를 분석하여 API 호출 정보를 추출하는 Agent
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from common.models import ApiCall
from legacy.parsers import ApiCallExtractor

from .base import AgentError, BaseAgent


class LogAnalyzerAgent(BaseAgent):
    """
    로그 분석 Agent

    다양한 형식의 로그를 분석하여 API 호출 정보를 자동으로 추출합니다.

    지원하는 입력:
    - 로그 파일 경로 (str)
    - 로그 텍스트 (str)
    - 로그 텍스트 목록 (List[str])
    """

    def __init__(self, name: Optional[str] = None):
        """
        Args:
            name: Agent 이름
        """
        super().__init__(name)
        self.extractor = ApiCallExtractor()

    def execute(
        self, input_data: Union[str, List[str]], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        로그 분석 실행

        Args:
            input_data: 로그 파일 경로, 로그 텍스트, 또는 로그 텍스트 목록
            context: 실행 컨텍스트
                - is_file: 입력이 파일 경로인지 여부 (기본값: 자동 감지)
                - source_name: 로그 소스 이름 (기본값: None)

        Returns:
            {
                "api_calls": List[ApiCall],  # 추출된 API 호출 목록
                "total_count": int,          # 총 API 호출 개수
                "formats": Dict[str, int],   # 형식별 개수
                "source": str,               # 입력 소스
            }

        Raises:
            AgentError: 로그 분석 실패 시
        """
        context = context or {}

        try:
            # 입력 데이터 유형 판별
            api_calls = self._extract_api_calls(input_data, context)

            # 형식별 통계
            formats = self._count_by_format(api_calls)

            # 소스 정보
            source = context.get("source_name")
            if not source:
                if isinstance(input_data, str) and self._is_file_path(input_data):
                    source = input_data
                else:
                    source = "text_input"

            return {
                "api_calls": api_calls,
                "total_count": len(api_calls),
                "formats": formats,
                "source": source,
            }

        except Exception as e:
            raise AgentError(f"로그 분석 중 에러 발생: {e}")

    def _extract_api_calls(
        self, input_data: Union[str, List[str]], context: Dict[str, Any]
    ) -> List[ApiCall]:
        """
        입력 데이터에서 API 호출 추출

        Args:
            input_data: 로그 파일 경로, 로그 텍스트, 또는 로그 텍스트 목록
            context: 실행 컨텍스트

        Returns:
            추출된 API 호출 목록
        """
        # 리스트인 경우 각각 추출하여 병합
        if isinstance(input_data, list):
            all_calls = []
            for idx, log_text in enumerate(input_data):
                try:
                    calls = self.extractor.extract(log_text, source_file=f"entry_{idx}")
                    all_calls.extend(calls)
                except Exception:
                    # 개별 로그 추출 실패는 무시
                    continue
            return all_calls

        # 문자열인 경우
        if isinstance(input_data, str):
            # 파일 경로인지 확인
            is_file = context.get("is_file")
            if is_file is None:
                is_file = self._is_file_path(input_data)

            if is_file:
                # 파일에서 추출
                return self.extractor.extract_from_file(input_data)
            else:
                # 텍스트에서 추출
                return self.extractor.extract(input_data)

        raise AgentError(f"지원하지 않는 입력 타입: {type(input_data)}")

    def _is_file_path(self, text: str) -> bool:
        """
        문자열이 파일 경로인지 확인

        Args:
            text: 확인할 문자열

        Returns:
            파일 경로 여부
        """
        # 너무 긴 텍스트는 파일 경로가 아님
        if len(text) > 500:
            return False

        # 줄바꿈이 있으면 파일 경로가 아님
        if "\n" in text:
            return False

        # 파일이 실제로 존재하는지 확인
        try:
            path = Path(text)
            return path.is_file()
        except (OSError, ValueError):
            return False

    def _count_by_format(self, api_calls: List[ApiCall]) -> Dict[str, int]:
        """
        형식별 API 호출 개수 집계

        Args:
            api_calls: API 호출 목록

        Returns:
            형식별 개수 {"method": count}
        """
        formats: Dict[str, int] = {}
        for call in api_calls:
            method = call.method.value
            formats[method] = formats.get(method, 0) + 1
        return formats

    def get_summary(self, result: Dict[str, Any]) -> str:
        """
        분석 결과 요약 생성

        Args:
            result: execute() 결과

        Returns:
            요약 텍스트
        """
        total = result["total_count"]
        formats = result["formats"]
        source = result["source"]

        summary_lines = [
            f"=== 로그 분석 결과 ===",
            f"소스: {source}",
            f"총 {total}개 API 호출 추출",
            "",
            "HTTP 메서드별:",
        ]

        for method, count in sorted(formats.items()):
            summary_lines.append(f"  - {method}: {count}개")

        return "\n".join(summary_lines)
