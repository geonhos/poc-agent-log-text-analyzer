"""
API Spec 관련 데이터 모델

OpenAPI/Swagger spec의 정보를 표현하는 Pydantic 모델들
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HTTPMethod(str, Enum):
    """HTTP 메서드"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"


class ParameterLocation(str, Enum):
    """파라미터 위치"""

    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"


class ParameterSchema(BaseModel):
    """파라미터 스키마 정보"""

    type: str
    format: Optional[str] = None
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    pattern: Optional[str] = None
    items: Optional[Dict[str, Any]] = None  # array type의 경우


class Parameter(BaseModel):
    """API 파라미터 정보"""

    name: str
    location: ParameterLocation = Field(..., description="파라미터 위치 (query, path, header, cookie)")
    required: bool = False
    description: Optional[str] = None
    schema_info: Optional[ParameterSchema] = Field(None, alias="schema")
    example: Optional[Any] = None
    deprecated: bool = False

    class Config:
        populate_by_name = True


class RequestBody(BaseModel):
    """Request Body 정보"""

    description: Optional[str] = None
    required: bool = False
    content_type: str = Field(default="application/json", description="Content-Type")
    schema_info: Optional[Dict[str, Any]] = Field(None, description="Request body schema")
    examples: Optional[Dict[str, Any]] = None


class Response(BaseModel):
    """Response 정보"""

    status_code: str
    description: Optional[str] = None
    content_type: Optional[str] = "application/json"
    schema_info: Optional[Dict[str, Any]] = Field(None, description="Response schema")
    examples: Optional[Dict[str, Any]] = None


class APIEndpoint(BaseModel):
    """API Endpoint 정보"""

    path: str = Field(..., description="API path (e.g., /api/users/{id})")
    method: HTTPMethod = Field(..., description="HTTP method")
    operation_id: Optional[str] = Field(None, description="Operation ID")
    summary: Optional[str] = Field(None, description="간단한 설명")
    description: Optional[str] = Field(None, description="상세 설명")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    parameters: List[Parameter] = Field(default_factory=list, description="파라미터 목록")
    request_body: Optional[RequestBody] = Field(None, description="Request body 정보")
    responses: List[Response] = Field(default_factory=list, description="Response 목록")
    deprecated: bool = Field(default=False, description="Deprecated 여부")
    security: Optional[List[Dict[str, List[str]]]] = Field(None, description="보안 요구사항")

    def get_text_representation(self) -> str:
        """
        검색 최적화를 위한 텍스트 표현 생성

        Returns:
            검색에 사용될 텍스트 표현
        """
        parts = [
            f"{self.method.value} {self.path}",
        ]

        if self.summary:
            parts.append(f"Summary: {self.summary}")

        if self.description:
            parts.append(f"Description: {self.description}")

        if self.tags:
            parts.append(f"Tags: {', '.join(self.tags)}")

        if self.parameters:
            param_desc = []
            for param in self.parameters:
                param_str = f"{param.name} ({param.location.value})"
                if param.required:
                    param_str += " [required]"
                if param.description:
                    param_str += f": {param.description}"
                param_desc.append(param_str)
            parts.append(f"Parameters: {'; '.join(param_desc)}")

        if self.request_body:
            if self.request_body.description:
                parts.append(f"Request Body: {self.request_body.description}")

        return "\n".join(parts)

    def get_unique_id(self) -> str:
        """
        엔드포인트의 고유 ID 생성

        Returns:
            고유 ID (method_path 형식)
        """
        # path에서 특수문자 제거
        clean_path = self.path.replace("/", "_").replace("{", "").replace("}", "")
        return f"{self.method.value.lower()}{clean_path}"


class APISpec(BaseModel):
    """API Specification 전체 정보"""

    title: str = Field(..., description="API 제목")
    version: str = Field(..., description="API 버전")
    description: Optional[str] = Field(None, description="API 설명")
    base_url: Optional[str] = Field(None, description="Base URL")
    endpoints: List[APIEndpoint] = Field(default_factory=list, description="엔드포인트 목록")

    # OpenAPI/Swagger 메타정보
    openapi_version: Optional[str] = Field(None, description="OpenAPI 버전 (3.x)")
    swagger_version: Optional[str] = Field(None, description="Swagger 버전 (2.x)")

    def get_endpoint(self, method: str, path: str) -> Optional[APIEndpoint]:
        """
        특정 메서드와 경로로 엔드포인트 찾기

        Args:
            method: HTTP 메서드
            path: API 경로

        Returns:
            찾은 엔드포인트 또는 None
        """
        method_upper = method.upper()
        for endpoint in self.endpoints:
            if endpoint.method.value == method_upper and endpoint.path == path:
                return endpoint
        return None

    def get_endpoints_by_tag(self, tag: str) -> List[APIEndpoint]:
        """
        태그로 엔드포인트 필터링

        Args:
            tag: 태그 이름

        Returns:
            태그를 가진 엔드포인트 목록
        """
        return [endpoint for endpoint in self.endpoints if tag in endpoint.tags]

    def count_endpoints(self) -> int:
        """엔드포인트 개수 반환"""
        return len(self.endpoints)
