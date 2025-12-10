"""
HTTP Request Log Parser

HTTP request dump 형식의 로그를 파싱하여 API 호출 정보 추출
"""

import re
from typing import Dict, List, Optional

from common.models import ApiCall, HttpMethod

from .base import BaseLogParser, ParserError


class HttpRequestParser(BaseLogParser):
    """
    HTTP Request 로그 파서

    실제 HTTP request dump (예: tcpdump, wireshark, HTTP client logs)를 파싱합니다.

    지원하는 형식:
    ```
    GET /api/users HTTP/1.1
    Host: api.example.com
    Authorization: Bearer token123
    Content-Type: application/json

    {"name": "John"}
    ```
    """

    # HTTP request line 패턴: "METHOD /path HTTP/version"
    REQUEST_LINE_PATTERN = re.compile(
        r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+([^\s]+)\s+HTTP/[\d\.]+",
        re.IGNORECASE,
    )

    # Header 패턴: "Key: Value"
    HEADER_PATTERN = re.compile(r"^([A-Za-z\-]+):\s*(.+)$")

    def can_parse(self, log_text: str) -> bool:
        """
        HTTP request 로그인지 확인

        Args:
            log_text: 로그 텍스트

        Returns:
            파싱 가능 여부
        """
        if not log_text or not log_text.strip():
            return False

        # 첫 번째 라인이 HTTP request line인지 확인
        first_line = log_text.strip().split("\n")[0].strip()
        return self.REQUEST_LINE_PATTERN.match(first_line) is not None

    def parse(self, log_text: str, source_file: Optional[str] = None) -> List[ApiCall]:
        """
        HTTP request 로그 파싱

        Args:
            log_text: 로그 텍스트
            source_file: 로그 소스 파일명

        Returns:
            추출된 API 호출 목록

        Raises:
            ParserError: 파싱 실패 시
        """
        api_calls = []

        try:
            # 여러 HTTP request가 있을 수 있으므로 분리
            requests = self._split_requests(log_text)

            for idx, request_text in enumerate(requests, start=1):
                api_call = self._parse_single_request(request_text, source_file, idx)
                if api_call:
                    api_calls.append(api_call)

        except Exception as e:
            raise ParserError(f"HTTP request 파싱 중 에러 발생: {e}")

        return api_calls

    def _split_requests(self, log_text: str) -> List[str]:
        """
        여러 HTTP request를 개별적으로 분리

        Args:
            log_text: 전체 로그 텍스트

        Returns:
            개별 request 텍스트 목록
        """
        requests = []
        current_request = []
        lines = log_text.split("\n")

        for line in lines:
            # 새로운 HTTP request line을 만나면
            if self.REQUEST_LINE_PATTERN.match(line.strip()):
                # 이전 request 저장
                if current_request:
                    requests.append("\n".join(current_request))
                # 새 request 시작
                current_request = [line]
            else:
                # 현재 request에 라인 추가
                if current_request:
                    current_request.append(line)

        # 마지막 request 저장
        if current_request:
            requests.append("\n".join(current_request))

        return requests

    def _parse_single_request(
        self, request_text: str, source_file: Optional[str] = None, request_number: Optional[int] = None
    ) -> Optional[ApiCall]:
        """
        단일 HTTP request 파싱

        Args:
            request_text: HTTP request 텍스트
            source_file: 소스 파일명
            request_number: request 번호

        Returns:
            ApiCall 객체 또는 None
        """
        lines = request_text.strip().split("\n")

        if not lines:
            return None

        # 1. Request line 파싱
        request_line = lines[0].strip()
        match = self.REQUEST_LINE_PATTERN.match(request_line)

        if not match:
            return None

        method_str = match.group(1).upper()
        url = match.group(2)

        # HTTP 메서드 검증
        try:
            method = HttpMethod(method_str)
        except ValueError:
            return None

        # URL 파싱
        base_url, path, query_params = self._parse_url(url)

        # 2. Headers 파싱
        headers = {}
        body_start_idx = None

        for idx, line in enumerate(lines[1:], start=1):
            line = line.strip()

            # 빈 라인이 나오면 헤더 끝, body 시작
            if not line:
                body_start_idx = idx + 1
                break

            # Header 파싱
            header_match = self.HEADER_PATTERN.match(line)
            if header_match:
                key = header_match.group(1)
                value = header_match.group(2).strip()
                headers[key] = value

        # Host 헤더에서 base_url 추출 (URL에 없는 경우)
        if not base_url and "Host" in headers:
            # HTTP/HTTPS 결정 (기본 HTTPS)
            protocol = "https"
            if "http://" in url or (headers.get("X-Forwarded-Proto", "").lower() == "http"):
                protocol = "http"
            base_url = f"{protocol}://{headers['Host']}"

        # 3. Body 파싱
        body = None
        if body_start_idx and body_start_idx < len(lines):
            body_lines = lines[body_start_idx:]
            body_text = "\n".join(body_lines).strip()

            if body_text:
                # Content-Type에 따라 파싱
                content_type = headers.get("Content-Type", "")

                if "application/json" in content_type:
                    # JSON 파싱 시도
                    try:
                        import json

                        body = json.loads(body_text)
                    except json.JSONDecodeError:
                        body = body_text
                elif "application/x-www-form-urlencoded" in content_type:
                    # Form data 파싱
                    body = {}
                    for param in body_text.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            body[key] = value
                else:
                    # 그 외는 문자열로
                    body = body_text

        # 소스 정보
        source = source_file
        if request_number:
            source = (
                f"{source_file}:request-{request_number}"
                if source_file
                else f"request {request_number}"
            )

        return ApiCall(
            method=method,
            path=path,
            base_url=base_url,
            query_params=query_params or {},
            headers=headers,
            body=body,
            source=source,
            raw_log=request_text,
        )

    def _parse_url(self, url: str) -> tuple[Optional[str], str, Optional[Dict[str, str]]]:
        """
        URL을 base_url, path, query_params로 분리

        Args:
            url: 전체 URL 또는 경로

        Returns:
            (base_url, path, query_params) 튜플
        """
        # URL에서 쿼리 파라미터 분리
        if "?" in url:
            url_part, query_part = url.split("?", 1)
            query_params = {}
            for param in query_part.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    query_params[key] = value
                else:
                    query_params[param] = ""
        else:
            url_part = url
            query_params = None

        # base_url과 path 분리
        if url_part.startswith(("http://", "https://")):
            match = re.match(r"(https?://[^/]+)(/.*)$", url_part)
            if match:
                base_url = match.group(1)
                path = match.group(2)
            else:
                base_url = url_part
                path = "/"
        else:
            # 상대 경로 (Host 헤더에서 base_url 추출 필요)
            base_url = None
            path = url_part if url_part.startswith("/") else f"/{url_part}"

        return base_url, path, query_params
