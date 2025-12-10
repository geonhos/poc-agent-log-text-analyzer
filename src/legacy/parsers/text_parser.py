"""
Plain Text Log Parser

일반 텍스트 형식의 로그를 파싱하여 API 호출 정보 추출
"""

import re
from typing import Dict, List, Optional

from common.models import ApiCall, HttpMethod

from .base import BaseLogParser, ParserError


class TextLogParser(BaseLogParser):
    """
    Plain Text 로그 파서

    일반 텍스트 로그에서 정규표현식을 사용하여 API 호출 정보를 추출합니다.

    지원하는 패턴:
    - "GET /users/123"
    - "POST /api/users with body {...}"
    - "Request: GET /users"
    - "API call: DELETE /users/123"
    - "[2024-01-01] GET /users - 200 OK"
    """

    # HTTP 메서드 패턴
    HTTP_METHODS = "|".join([m.value for m in HttpMethod])

    # 기본 패턴들
    PATTERNS = [
        # Pattern 1: "METHOD /path"
        re.compile(
            rf"\b({HTTP_METHODS})\s+([/\w\-\.]+(?:\?[\w=&\-\.]+)?)",
            re.IGNORECASE,
        ),
        # Pattern 2: "METHOD: /path" or "method: /path"
        re.compile(
            rf"(?:method|request|api[\s_]?call):\s*({HTTP_METHODS})\s+([/\w\-\.]+(?:\?[\w=&\-\.]+)?)",
            re.IGNORECASE,
        ),
        # Pattern 3: "HTTP/1.1 METHOD /path"
        re.compile(
            rf"HTTP/[\d\.]+\s+({HTTP_METHODS})\s+([/\w\-\.]+(?:\?[\w=&\-\.]+)?)",
            re.IGNORECASE,
        ),
        # Pattern 4: "curl -X METHOD http://..."
        re.compile(
            rf"curl\s+(?:-X\s+)?({HTTP_METHODS})\s+(https?://[\w\-\./:?=&]+)",
            re.IGNORECASE,
        ),
    ]

    # 추가 정보 패턴
    BODY_PATTERN = re.compile(
        r"(?:with\s+)?(?:body|data|payload)[\s:=]+['\"]?({[^}]+}|\[[^\]]+\])",
        re.IGNORECASE,
    )
    HEADER_PATTERN = re.compile(
        r"(?:header|headers)[\s:=]+['\"]?([^'\"]+)",
        re.IGNORECASE,
    )
    STATUS_PATTERN = re.compile(
        r"(?:status|response)[\s:=]+(\d{3})",
        re.IGNORECASE,
    )
    TIMESTAMP_PATTERN = re.compile(
        r"\[?(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\]?",
    )

    def can_parse(self, log_text: str) -> bool:
        """
        Plain text 로그인지 확인

        Args:
            log_text: 로그 텍스트

        Returns:
            파싱 가능 여부
        """
        if not log_text or not log_text.strip():
            return False

        # HTTP 메서드가 포함되어 있는지 확인
        for pattern in self.PATTERNS:
            if pattern.search(log_text):
                return True

        return False

    def parse(self, log_text: str, source_file: Optional[str] = None) -> List[ApiCall]:
        """
        Plain text 로그 파싱

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
            for line_number, line in enumerate(log_text.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue

                api_call = self._parse_line(line, source_file, line_number)
                if api_call:
                    api_calls.append(api_call)

        except Exception as e:
            raise ParserError(f"로그 파싱 중 에러 발생: {e}")

        return api_calls

    def _parse_line(
        self, line: str, source_file: Optional[str] = None, line_number: Optional[int] = None
    ) -> Optional[ApiCall]:
        """
        단일 라인 파싱

        Args:
            line: 로그 라인
            source_file: 소스 파일명
            line_number: 라인 번호

        Returns:
            ApiCall 객체 또는 None
        """
        # 각 패턴으로 시도
        for pattern in self.PATTERNS:
            match = pattern.search(line)
            if match:
                method_str = match.group(1).upper()
                url = match.group(2)

                # HTTP 메서드 검증
                try:
                    method = HttpMethod(method_str)
                except ValueError:
                    continue

                # URL 파싱
                base_url, path, query_params = self._parse_url(url)

                # 추가 정보 추출
                body = self._extract_body(line)
                headers = self._extract_headers(line)
                status_code = self._extract_status(line)
                timestamp = self._extract_timestamp(line)

                # 소스 정보
                source = source_file
                if line_number:
                    source = f"{source_file}:{line_number}" if source_file else f"line {line_number}"

                return ApiCall(
                    method=method,
                    path=path,
                    base_url=base_url,
                    query_params=query_params or {},
                    headers=headers,
                    body=body,
                    status_code=status_code,
                    timestamp=timestamp,
                    source=source,
                    raw_log=line,
                )

        return None

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
            base_url = None
            path = url_part if url_part.startswith("/") else f"/{url_part}"

        return base_url, path, query_params

    def _extract_body(self, line: str) -> Optional[Dict | str]:
        """
        라인에서 request body 추출

        Args:
            line: 로그 라인

        Returns:
            body 내용 또는 None
        """
        match = self.BODY_PATTERN.search(line)
        if match:
            body_str = match.group(1)
            # JSON 파싱 시도
            try:
                import json

                return json.loads(body_str)
            except (json.JSONDecodeError, ValueError):
                # JSON이 아니면 문자열로 반환
                return body_str
        return None

    def _extract_headers(self, line: str) -> Dict[str, str]:
        """
        라인에서 headers 추출

        Args:
            line: 로그 라인

        Returns:
            headers 딕셔너리
        """
        headers = {}
        match = self.HEADER_PATTERN.search(line)
        if match:
            headers_str = match.group(1)
            # "key: value" 형식 파싱
            for header in headers_str.split(","):
                if ":" in header:
                    key, value = header.split(":", 1)
                    headers[key.strip()] = value.strip()
        return headers

    def _extract_status(self, line: str) -> Optional[int]:
        """
        라인에서 status code 추출

        Args:
            line: 로그 라인

        Returns:
            status code 또는 None
        """
        match = self.STATUS_PATTERN.search(line)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return None

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """
        라인에서 timestamp 추출

        Args:
            line: 로그 라인

        Returns:
            timestamp 문자열 또는 None
        """
        match = self.TIMESTAMP_PATTERN.search(line)
        if match:
            return match.group(1)
        return None
