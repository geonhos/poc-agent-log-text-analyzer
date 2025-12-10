"""
API Call 모델

로그에서 추출한 API 호출 정보를 표현
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HttpMethod(str, Enum):
    """HTTP 메서드"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ApiCall(BaseModel):
    """
    로그에서 추출한 API 호출 정보

    로그 파서가 추출한 HTTP 요청 정보를 구조화된 형태로 표현
    """

    # 기본 정보
    method: HttpMethod = Field(..., description="HTTP 메서드")
    path: str = Field(..., description="API 경로 (예: /users/123)")

    # URL 구성 요소
    base_url: Optional[str] = Field(None, description="베이스 URL (예: https://api.example.com)")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="쿼리 파라미터")

    # 요청 정보
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP 헤더")
    body: Optional[Any] = Field(None, description="요청 바디 (JSON, form data 등)")

    # 응답 정보 (옵션)
    status_code: Optional[int] = Field(None, description="HTTP 상태 코드")
    response_body: Optional[Any] = Field(None, description="응답 바디")

    # 메타데이터
    timestamp: Optional[str] = Field(None, description="요청 시각")
    source: Optional[str] = Field(None, description="로그 소스 (파일명, 라인번호 등)")
    raw_log: Optional[str] = Field(None, description="원본 로그 텍스트")

    def get_full_url(self) -> str:
        """
        전체 URL 생성

        Returns:
            전체 URL 문자열
        """
        url = self.path

        # base_url이 있으면 결합
        if self.base_url:
            url = f"{self.base_url.rstrip('/')}/{self.path.lstrip('/')}"

        # 쿼리 파라미터 추가
        if self.query_params:
            params_str = "&".join(f"{k}={v}" for k, v in self.query_params.items())
            url = f"{url}?{params_str}"

        return url

    def get_summary(self) -> str:
        """
        요청 요약 텍스트

        Returns:
            "{METHOD} {PATH}" 형식의 요약
        """
        return f"{self.method.value} {self.path}"

    def to_curl_command(self) -> str:
        """
        Curl 명령어로 변환 (기본 버전)

        Returns:
            기본 curl 명령어
        """
        parts = ["curl", "-X", self.method.value]

        # 헤더 추가
        for key, value in self.headers.items():
            parts.extend(["-H", f'"{key}: {value}"'])

        # 바디 추가
        if self.body is not None:
            import json
            body_str = json.dumps(self.body) if isinstance(self.body, dict) else str(self.body)
            parts.extend(["-d", f"'{body_str}'"])

        # URL 추가
        parts.append(f'"{self.get_full_url()}"')

        return " ".join(parts)


class LogEntry(BaseModel):
    """
    개별 로그 엔트리

    파싱 전의 원시 로그 데이터
    """

    raw_text: str = Field(..., description="원본 로그 텍스트")
    line_number: Optional[int] = Field(None, description="로그 파일 내 라인 번호")
    timestamp: Optional[str] = Field(None, description="로그 타임스탬프")
    level: Optional[str] = Field(None, description="로그 레벨 (INFO, ERROR 등)")
    source_file: Optional[str] = Field(None, description="로그 소스 파일명")

    def __str__(self) -> str:
        return f"LogEntry(line={self.line_number}, text={self.raw_text[:50]}...)"
