"""
LLM-based Log Analyzer Agent

LLM을 사용하여 복잡한 로그를 분석하는 Agent
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

from common.models import ApiCall, HttpMethod
from legacy.llm import LLMError, OllamaLLM
from legacy.llm.prompt_template import LogAnalysisPrompts

from .base import AgentError, BaseAgent


class LLMLogAnalyzerAgent(BaseAgent):
    """
    LLM 기반 로그 분석 Agent

    복잡하거나 구조화되지 않은 로그를 LLM을 통해 분석합니다.
    규칙 기반 파서가 실패할 때 사용됩니다.
    """

    def __init__(
        self,
        llm: Optional[OllamaLLM] = None,
        model: str = "llama2:7b-chat-q4_0",
        name: Optional[str] = None,
    ):
        """
        Args:
            llm: LLM 인스턴스 (없으면 기본 Ollama 사용)
            model: LLM 모델명
            name: Agent 이름
        """
        super().__init__(name)
        self.llm = llm or OllamaLLM(model=model)
        self.prompt_template = LogAnalysisPrompts.EXTRACT_API_CALLS

    def execute(
        self, input_data: Union[str, List[str]], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LLM을 사용하여 로그 분석

        Args:
            input_data: 로그 텍스트 또는 로그 텍스트 목록
            context: 실행 컨텍스트
                - temperature: LLM 온도 (기본값: 0.1)
                - max_tokens: 최대 토큰 수
                - source_name: 로그 소스 이름

        Returns:
            {
                "api_calls": List[ApiCall],
                "total_count": int,
                "raw_llm_response": str,
                "source": str,
                "llm_used": bool,
            }

        Raises:
            AgentError: 분석 실패 시
        """
        context = context or {}

        try:
            # 입력 데이터 처리
            if isinstance(input_data, list):
                log_text = "\n".join(input_data)
            else:
                log_text = input_data

            # LLM으로 분석
            api_calls = self._analyze_with_llm(log_text, context)

            # 소스 정보
            source = context.get("source_name", "llm_analysis")

            return {
                "api_calls": api_calls,
                "total_count": len(api_calls),
                "raw_llm_response": getattr(self, "_last_response", ""),
                "source": source,
                "llm_used": True,
            }

        except Exception as e:
            raise AgentError(f"LLM 로그 분석 중 에러 발생: {e}")

    def _analyze_with_llm(
        self, log_text: str, context: Dict[str, Any]
    ) -> List[ApiCall]:
        """
        LLM을 사용하여 로그 분석

        Args:
            log_text: 로그 텍스트
            context: 실행 컨텍스트

        Returns:
            추출된 API 호출 목록
        """
        try:
            # 프롬프트 생성
            prompt = self.prompt_template.format(log_text=log_text)

            # LLM 호출
            temperature = context.get("temperature", 0.1)
            max_tokens = context.get("max_tokens", 2000)

            response = self.llm.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # 응답 저장 (디버깅용)
            self._last_response = response.content

            # JSON 파싱
            api_calls = self._parse_llm_response(response.content)

            return api_calls

        except LLMError as e:
            raise AgentError(f"LLM 호출 실패: {e}")
        except Exception as e:
            raise AgentError(f"LLM 응답 처리 실패: {e}")

    def _parse_llm_response(self, response_text: str) -> List[ApiCall]:
        """
        LLM 응답에서 API 호출 정보 파싱

        Args:
            response_text: LLM 응답 텍스트

        Returns:
            ApiCall 목록
        """
        # JSON 추출 (코드 블록 또는 일반 텍스트에서)
        json_text = self._extract_json(response_text)

        if not json_text:
            return []

        try:
            # JSON 파싱
            data = json.loads(json_text)

            # 리스트가 아니면 리스트로 감싸기
            if not isinstance(data, list):
                data = [data]

            # ApiCall 객체로 변환
            api_calls = []
            for item in data:
                try:
                    api_call = self._dict_to_api_call(item)
                    if api_call:
                        api_calls.append(api_call)
                except Exception:
                    # 개별 항목 파싱 실패는 무시
                    continue

            return api_calls

        except json.JSONDecodeError as e:
            # 파싱 실패 시 빈 리스트 반환 (LLM이 JSON을 생성하지 못할 수 있음)
            print(f"Warning: JSON 파싱 실패 - {e}")
            print(f"Response text: {json_text[:200]}...")
            return []

    def _extract_json(self, text: str) -> Optional[str]:
        """
        텍스트에서 JSON 추출

        Args:
            text: 입력 텍스트

        Returns:
            JSON 문자열 또는 None
        """
        # 코드 블록에서 JSON 추출
        code_block_pattern = r"```(?:json)?\s*(\[[\s\S]*?\]|\{[\s\S]*?\})\s*```"
        match = re.search(code_block_pattern, text)
        if match:
            json_text = match.group(1)
            # Trailing commas 제거
            json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
            return json_text

        # JSON 배열 찾기 (가장 일반적)
        json_array_pattern = r"\[[\s\S]*\]"
        match = re.search(json_array_pattern, text)
        if match:
            json_text = match.group(0)
            # Trailing commas 제거
            json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
            # 불완전한 JSON 처리 - 마지막 항목이 잘렸을 수 있음
            # 마지막 }나 ]로 끝나지 않으면 추가
            json_text = json_text.strip()
            if json_text and not json_text.endswith(']'):
                # 마지막 객체가 불완전하면 제거
                last_complete = json_text.rfind('}')
                if last_complete > 0:
                    json_text = json_text[:last_complete+1] + ']'
            return json_text

        # JSON 객체 찾기
        json_obj_pattern = r"\{[\s\S]*?\}"
        match = re.search(json_obj_pattern, text)
        if match:
            json_text = match.group(0)
            # Trailing commas 제거
            json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
            return json_text

        return None

    def _dict_to_api_call(self, data: Dict[str, Any]) -> Optional[ApiCall]:
        """
        딕셔너리를 ApiCall 객체로 변환

        Args:
            data: API 호출 정보 딕셔너리

        Returns:
            ApiCall 객체 또는 None
        """
        # 필수 필드 확인
        method = data.get("method")
        path = data.get("path") or data.get("url")

        if not method or not path:
            return None

        # HTTP 메서드 검증
        try:
            http_method = HttpMethod(method.upper())
        except ValueError:
            return None

        # URL 파싱
        base_url = None
        if path.startswith("http://") or path.startswith("https://"):
            # 전체 URL인 경우 base_url과 path 분리
            from urllib.parse import urlparse

            parsed = urlparse(path)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            path = parsed.path or "/"

        return ApiCall(
            method=http_method,
            path=path,
            base_url=base_url,
            headers=data.get("headers") or {},
            body=data.get("body"),
            query_params=data.get("query_params") or data.get("query") or {},
            status_code=data.get("status_code") or data.get("status"),
            response_body=data.get("response_body") or data.get("response"),
            timestamp=data.get("timestamp"),
            source="llm_analysis",
        )

    def get_summary(self, result: Dict[str, Any]) -> str:
        """
        분석 결과 요약

        Args:
            result: execute() 결과

        Returns:
            요약 텍스트
        """
        total = result["total_count"]
        source = result["source"]

        summary_lines = [
            f"=== LLM 로그 분석 결과 ===",
            f"소스: {source}",
            f"총 {total}개 API 호출 추출 (LLM 사용)",
            f"모델: {self.llm.model}",
        ]

        return "\n".join(summary_lines)
