"""
JSON Log Parser

JSON 형식의 로그를 파싱하여 API 호출 정보 추출
"""

import json
import re
from typing import Any, Dict, List, Optional

from common.models import ApiCall, HttpMethod

from .base import BaseLogParser, ParserError


class JsonLogParser(BaseLogParser):
    """
    JSON 로그 파서

    JSON 형식의 로그에서 API 호출 정보를 추출합니다.

    지원하는 로그 형식:
    1. 단일 JSON 객체
    2. JSON Lines (JSONL) - 각 라인이 JSON 객체
    3. JSON 배열
    """

    # JSON 로그에서 찾을 필드명 (우선순위 순)
    METHOD_FIELDS = ["method", "http_method", "request_method", "verb"]
    PATH_FIELDS = ["path", "url", "endpoint", "uri", "request_path", "request_url"]
    HEADERS_FIELDS = ["headers", "request_headers", "http_headers"]
    BODY_FIELDS = ["body", "request_body", "data", "payload"]
    QUERY_FIELDS = ["query", "query_params", "query_string", "params"]
    STATUS_FIELDS = ["status", "status_code", "response_status", "http_status"]
    RESPONSE_FIELDS = ["response", "response_body", "response_data"]
    TIMESTAMP_FIELDS = ["timestamp", "time", "datetime", "created_at", "@timestamp"]

    def can_parse(self, log_text: str) -> bool:
        """
        JSON 로그인지 확인

        Args:
            log_text: 로그 텍스트

        Returns:
            JSON 파싱 가능 여부
        """
        log_text = log_text.strip()

        # 빈 텍스트
        if not log_text:
            return False

        # JSON 객체 또는 배열로 시작하는지 확인
        if log_text.startswith("{") or log_text.startswith("["):
            try:
                json.loads(log_text)
                return True
            except json.JSONDecodeError:
                pass

        # JSONL 형식인지 확인 (첫 번째 라인이 JSON인지)
        first_line = log_text.split("\n")[0].strip()
        if first_line.startswith("{"):
            try:
                json.loads(first_line)
                return True
            except json.JSONDecodeError:
                pass

        return False

    def parse(self, log_text: str, source_file: Optional[str] = None) -> List[ApiCall]:
        """
        JSON 로그 파싱

        Args:
            log_text: 로그 텍스트
            source_file: 로그 소스 파일명

        Returns:
            추출된 API 호출 목록

        Raises:
            ParserError: 파싱 실패 시
        """
        log_text = log_text.strip()

        if not log_text:
            return []

        api_calls = []

        try:
            # 전체를 JSON으로 파싱 시도 (단일 객체 또는 배열)
            if log_text.startswith("{") or log_text.startswith("["):
                try:
                    data = json.loads(log_text)

                    if isinstance(data, dict):
                        # 단일 객체
                        api_call = self._extract_from_json(data, source_file)
                        if api_call:
                            api_calls.append(api_call)
                        return api_calls

                    elif isinstance(data, list):
                        # JSON 배열
                        for idx, item in enumerate(data):
                            if isinstance(item, dict):
                                api_call = self._extract_from_json(item, source_file, line_number=idx + 1)
                                if api_call:
                                    api_calls.append(api_call)
                        return api_calls

                except json.JSONDecodeError:
                    # 전체 파싱 실패 -> JSONL 형식일 가능성
                    pass

            # JSONL 형식 (각 라인이 JSON) - 전체 파싱 실패 시 또는 시작이 { 인 경우
            for line_number, line in enumerate(log_text.splitlines(), start=1):
                line = line.strip()
                if not line or not line.startswith("{"):
                    continue

                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        api_call = self._extract_from_json(
                            data, source_file, line_number=line_number
                        )
                        if api_call:
                            api_calls.append(api_call)
                except json.JSONDecodeError:
                    # 개별 라인 파싱 실패는 무시하고 계속
                    continue

        except Exception as e:
            raise ParserError(f"로그 파싱 중 에러 발생: {e}")

        return api_calls

    def _extract_from_json(
        self, data: Dict[str, Any], source_file: Optional[str] = None, line_number: Optional[int] = None
    ) -> Optional[ApiCall]:
        """
        JSON 객체에서 API 호출 정보 추출

        Args:
            data: JSON 데이터
            source_file: 소스 파일명
            line_number: 라인 번호

        Returns:
            ApiCall 객체 또는 None
        """
        # HTTP 메서드 추출
        method = self._find_field_value(data, self.METHOD_FIELDS)
        if not method:
            return None

        # 경로 추출
        path = self._find_field_value(data, self.PATH_FIELDS)
        if not path:
            return None

        # HTTP 메서드 검증 및 정규화
        try:
            method = method.upper()
            http_method = HttpMethod(method)
        except (ValueError, AttributeError):
            # 지원하지 않는 메서드는 건너뛰기
            return None

        # 경로에서 base_url과 path 분리
        base_url, clean_path, query_params = self._parse_url(path)

        # 추가 쿼리 파라미터 추출
        if not query_params:
            query_params_raw = self._find_field_value(data, self.QUERY_FIELDS)
            if query_params_raw and isinstance(query_params_raw, dict):
                query_params = query_params_raw

        # 헤더 추출
        headers = self._find_field_value(data, self.HEADERS_FIELDS) or {}
        if not isinstance(headers, dict):
            headers = {}

        # 바디 추출
        body = self._find_field_value(data, self.BODY_FIELDS)

        # 응답 정보 추출
        status_code = self._find_field_value(data, self.STATUS_FIELDS)
        response_body = self._find_field_value(data, self.RESPONSE_FIELDS)

        # 타임스탬프 추출
        timestamp = self._find_field_value(data, self.TIMESTAMP_FIELDS)
        if timestamp and not isinstance(timestamp, str):
            timestamp = str(timestamp)

        # 소스 정보 생성
        source = source_file
        if line_number:
            source = f"{source_file}:{line_number}" if source_file else f"line {line_number}"

        return ApiCall(
            method=http_method,
            path=clean_path,
            base_url=base_url,
            query_params=query_params or {},
            headers=headers,
            body=body,
            status_code=status_code,
            response_body=response_body,
            timestamp=timestamp,
            source=source,
            raw_log=json.dumps(data),
        )

    def _find_field_value(self, data: Dict[str, Any], field_names: List[str]) -> Optional[Any]:
        """
        여러 필드명 중 하나를 찾아서 값 반환

        Args:
            data: JSON 데이터
            field_names: 찾을 필드명 목록 (우선순위 순)

        Returns:
            필드 값 또는 None
        """
        for field_name in field_names:
            # 대소문자 구분 없이 검색
            for key, value in data.items():
                if key.lower() == field_name.lower():
                    return value
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
            url_part = url
            query_params = None

        # base_url과 path 분리
        # http:// 또는 https://로 시작하면 base_url 추출
        if url_part.startswith(("http://", "https://")):
            match = re.match(r"(https?://[^/]+)(/.*)$", url_part)
            if match:
                base_url = match.group(1)
                path = match.group(2)
            else:
                # 경로가 없는 경우 (예: https://api.example.com)
                base_url = url_part
                path = "/"
        else:
            # 상대 경로
            base_url = None
            path = url_part if url_part.startswith("/") else f"/{url_part}"

        return base_url, path, query_params
