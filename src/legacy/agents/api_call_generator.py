"""
API Call Generator Agent

ApiCall 객체를 curl 명령어나 Postman collection으로 변환하는 Agent
"""

import json
from typing import Any, Dict, List, Optional, Union

from common.models import ApiCall

from .base import AgentError, BaseAgent


class ApiCallGeneratorAgent(BaseAgent):
    """
    API 호출 생성 Agent

    ApiCall 객체를 실행 가능한 형태로 변환합니다.

    지원하는 출력 형식:
    - curl: curl 명령어
    - postman: Postman Collection v2.1
    - http: HTTP request dump
    """

    SUPPORTED_FORMATS = ["curl", "postman", "http"]

    def __init__(self, name: Optional[str] = None):
        """
        Args:
            name: Agent 이름
        """
        super().__init__(name)

    def execute(
        self, input_data: Union[ApiCall, List[ApiCall]], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        API 호출 생성 실행

        Args:
            input_data: ApiCall 객체 또는 ApiCall 목록
            context: 실행 컨텍스트
                - format: 출력 형식 ("curl", "postman", "http") (기본값: "curl")
                - name: Collection 이름 (Postman용, 기본값: "API Collection")

        Returns:
            {
                "format": str,           # 출력 형식
                "count": int,           # 생성된 호출 개수
                "outputs": List[str],   # 생성된 출력 목록
                "collection": dict,     # Postman collection (format="postman"일 때만)
            }

        Raises:
            AgentError: API 호출 생성 실패 시
        """
        context = context or {}
        output_format = context.get("format", "curl")

        if output_format not in self.SUPPORTED_FORMATS:
            raise AgentError(
                f"지원하지 않는 출력 형식: {output_format}. "
                f"지원 형식: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        try:
            # 단일 ApiCall을 리스트로 변환
            if isinstance(input_data, ApiCall):
                api_calls = [input_data]
            else:
                api_calls = input_data

            # 형식별 생성
            if output_format == "curl":
                outputs = self._generate_curl(api_calls)
                return {
                    "format": "curl",
                    "count": len(outputs),
                    "outputs": outputs,
                }

            elif output_format == "postman":
                collection = self._generate_postman_collection(
                    api_calls, context.get("name", "API Collection")
                )
                return {
                    "format": "postman",
                    "count": len(api_calls),
                    "outputs": [],
                    "collection": collection,
                }

            elif output_format == "http":
                outputs = self._generate_http(api_calls)
                return {
                    "format": "http",
                    "count": len(outputs),
                    "outputs": outputs,
                }

        except Exception as e:
            raise AgentError(f"API 호출 생성 중 에러 발생: {e}")

    def _generate_curl(self, api_calls: List[ApiCall]) -> List[str]:
        """
        curl 명령어 생성

        Args:
            api_calls: ApiCall 목록

        Returns:
            curl 명령어 목록
        """
        return [call.to_curl_command() for call in api_calls]

    def _generate_http(self, api_calls: List[ApiCall]) -> List[str]:
        """
        HTTP request dump 생성

        Args:
            api_calls: ApiCall 목록

        Returns:
            HTTP request dump 목록
        """
        results = []
        for call in api_calls:
            lines = []

            # Request line
            full_url = call.get_full_url()
            lines.append(f"{call.method.value} {full_url} HTTP/1.1")

            # Headers
            if call.headers:
                for key, value in call.headers.items():
                    lines.append(f"{key}: {value}")

            # Body
            if call.body:
                lines.append("")  # 빈 줄
                if isinstance(call.body, dict):
                    lines.append(json.dumps(call.body, indent=2))
                else:
                    lines.append(str(call.body))

            results.append("\n".join(lines))

        return results

    def _generate_postman_collection(
        self, api_calls: List[ApiCall], collection_name: str
    ) -> Dict[str, Any]:
        """
        Postman Collection v2.1 생성

        Args:
            api_calls: ApiCall 목록
            collection_name: Collection 이름

        Returns:
            Postman Collection 딕셔너리
        """
        items = []

        for idx, call in enumerate(api_calls):
            # Request 이름 생성
            request_name = call.source or f"{call.method.value} {call.path}"

            # URL 구성
            url_parts = {
                "raw": call.get_full_url(),
                "protocol": "https" if call.base_url and "https" in call.base_url else "http",
                "host": [],
                "path": call.path.strip("/").split("/") if call.path else [],
            }

            # base_url에서 host 추출
            if call.base_url:
                host = call.base_url.replace("https://", "").replace("http://", "")
                url_parts["host"] = host.split(".")

            # Query parameters
            if call.query_params:
                url_parts["query"] = [
                    {"key": k, "value": str(v)} for k, v in call.query_params.items()
                ]

            # Headers
            headers = []
            if call.headers:
                headers = [{"key": k, "value": v} for k, v in call.headers.items()]

            # Body
            body = {}
            if call.body:
                if isinstance(call.body, dict):
                    body = {
                        "mode": "raw",
                        "raw": json.dumps(call.body, indent=2),
                        "options": {"raw": {"language": "json"}},
                    }
                else:
                    body = {"mode": "raw", "raw": str(call.body)}

            # Request 객체
            request = {
                "method": call.method.value,
                "header": headers,
                "url": url_parts,
            }

            if body:
                request["body"] = body

            # Item 추가
            items.append({"name": request_name, "request": request})

        # Collection 구성
        collection = {
            "info": {
                "name": collection_name,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": items,
        }

        return collection

    def save_postman_collection(self, collection: Dict[str, Any], file_path: str) -> None:
        """
        Postman Collection을 파일로 저장

        Args:
            collection: Postman Collection 딕셔너리
            file_path: 저장할 파일 경로
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)

    def get_summary(self, result: Dict[str, Any]) -> str:
        """
        생성 결과 요약

        Args:
            result: execute() 결과

        Returns:
            요약 텍스트
        """
        format_name = result["format"]
        count = result["count"]

        summary_lines = [
            f"=== API 호출 생성 결과 ===",
            f"형식: {format_name}",
            f"생성 개수: {count}개",
        ]

        if format_name == "postman":
            collection = result.get("collection", {})
            collection_name = collection.get("info", {}).get("name", "Unknown")
            summary_lines.append(f"Collection 이름: {collection_name}")

        return "\n".join(summary_lines)
