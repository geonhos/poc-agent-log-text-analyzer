"""
OpenAPI/Swagger Spec 파일 로더

JSON 및 YAML 형식의 OpenAPI/Swagger spec 파일을 읽고 파싱합니다.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union

import yaml

# OpenAPI validator는 선택사항
try:
    from openapi_spec_validator import validate_spec
    from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
    HAS_VALIDATOR = True
except ImportError:
    HAS_VALIDATOR = False
    OpenAPIValidationError = Exception  # Fallback

from common.models import APIEndpoint, APISpec, HTTPMethod, Parameter, ParameterLocation, RequestBody, Response


class SpecLoaderError(Exception):
    """Spec 로더 에러"""

    pass


class OpenAPISpecLoader:
    """OpenAPI/Swagger Spec 로더"""

    def __init__(self, validate: bool = True):
        """
        Args:
            validate: spec 검증 여부
        """
        self.validate_on_load = validate

    def load_from_file(self, file_path: Union[str, Path]) -> APISpec:
        """
        파일에서 spec 로드

        Args:
            file_path: spec 파일 경로

        Returns:
            파싱된 APISpec 객체

        Raises:
            SpecLoaderError: 파일 로드 또는 파싱 실패 시
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise SpecLoaderError(f"파일이 존재하지 않음: {file_path}")

        # 파일 확장자에 따라 로더 선택
        suffix = file_path.suffix.lower()

        try:
            if suffix in [".json"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    spec_dict = json.load(f)
            elif suffix in [".yaml", ".yml"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    spec_dict = yaml.safe_load(f)
            else:
                raise SpecLoaderError(f"지원하지 않는 파일 형식: {suffix}")

            return self.load_from_dict(spec_dict)

        except json.JSONDecodeError as e:
            raise SpecLoaderError(f"JSON 파싱 실패: {e}")
        except yaml.YAMLError as e:
            raise SpecLoaderError(f"YAML 파싱 실패: {e}")
        except Exception as e:
            raise SpecLoaderError(f"Spec 로드 실패: {e}")

    def load_from_dict(self, spec_dict: Dict[str, Any]) -> APISpec:
        """
        딕셔너리에서 spec 로드

        Args:
            spec_dict: spec 딕셔너리

        Returns:
            파싱된 APISpec 객체

        Raises:
            SpecLoaderError: 파싱 실패 시
        """
        # Spec 검증 (선택사항)
        if self.validate_on_load:
            if not HAS_VALIDATOR:
                print("경고: openapi-spec-validator가 설치되지 않아 검증을 건너뜁니다")
            else:
                try:
                    validate_spec(spec_dict)
                except OpenAPIValidationError as e:
                    # 검증 실패해도 계속 진행 (경고만 출력)
                    print(f"경고: Spec 검증 실패 - {e}")

        # OpenAPI 버전 확인
        openapi_version = spec_dict.get("openapi")
        swagger_version = spec_dict.get("swagger")

        if not openapi_version and not swagger_version:
            raise SpecLoaderError("OpenAPI 또는 Swagger 버전 정보가 없음")

        # 기본 정보 추출
        info = spec_dict.get("info", {})
        title = info.get("title", "Unknown API")
        version = info.get("version", "1.0.0")
        description = info.get("description")

        # Base URL 추출
        base_url = self._extract_base_url(spec_dict)

        # Endpoint 추출
        endpoints = self._extract_endpoints(spec_dict)

        return APISpec(
            title=title,
            version=version,
            description=description,
            base_url=base_url,
            endpoints=endpoints,
            openapi_version=openapi_version,
            swagger_version=swagger_version,
        )

    def _extract_base_url(self, spec_dict: Dict[str, Any]) -> str | None:
        """Base URL 추출"""
        # OpenAPI 3.x
        if "servers" in spec_dict and spec_dict["servers"]:
            return spec_dict["servers"][0].get("url")

        # Swagger 2.x
        if "host" in spec_dict:
            scheme = spec_dict.get("schemes", ["https"])[0]
            host = spec_dict["host"]
            base_path = spec_dict.get("basePath", "")
            return f"{scheme}://{host}{base_path}"

        return None

    def _extract_endpoints(self, spec_dict: Dict[str, Any]) -> list[APIEndpoint]:
        """모든 endpoint 추출"""
        endpoints = []
        paths = spec_dict.get("paths", {})

        for path, path_item in paths.items():
            # 각 HTTP 메서드에 대해 처리
            for method in ["get", "post", "put", "delete", "patch", "head", "options", "trace"]:
                if method not in path_item:
                    continue

                operation = path_item[method]
                endpoint = self._parse_operation(path, method, operation, spec_dict)
                endpoints.append(endpoint)

        return endpoints

    def _parse_operation(
        self, path: str, method: str, operation: Dict[str, Any], spec_dict: Dict[str, Any]
    ) -> APIEndpoint:
        """개별 operation 파싱"""
        # 기본 정보
        operation_id = operation.get("operationId")
        summary = operation.get("summary")
        description = operation.get("description")
        tags = operation.get("tags", [])
        deprecated = operation.get("deprecated", False)
        security = operation.get("security")

        # Parameters 추출
        parameters = self._extract_parameters(operation, path)

        # Request Body 추출 (OpenAPI 3.x)
        request_body = self._extract_request_body(operation)

        # Responses 추출
        responses = self._extract_responses(operation)

        return APIEndpoint(
            path=path,
            method=HTTPMethod(method.upper()),
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            deprecated=deprecated,
            security=security,
        )

    def _extract_parameters(self, operation: Dict[str, Any], path: str) -> list[Parameter]:
        """Parameters 추출"""
        parameters = []
        param_list = operation.get("parameters", [])

        for param in param_list:
            # $ref 처리는 생략 (간단한 구현)
            if "$ref" in param:
                continue

            name = param.get("name")
            location_str = param.get("in", "query")
            required = param.get("required", False)
            description = param.get("description")
            deprecated = param.get("deprecated", False)

            # schema 정보 추출
            schema_info = param.get("schema", param)  # OpenAPI 3.x vs Swagger 2.x

            # ParameterLocation enum 변환
            try:
                location = ParameterLocation(location_str)
            except ValueError:
                location = ParameterLocation.QUERY

            parameters.append(
                Parameter(
                    name=name,
                    location=location,
                    required=required,
                    description=description,
                    schema=schema_info,
                    deprecated=deprecated,
                )
            )

        return parameters

    def _extract_request_body(self, operation: Dict[str, Any]) -> RequestBody | None:
        """Request Body 추출 (OpenAPI 3.x)"""
        request_body_spec = operation.get("requestBody")
        if not request_body_spec:
            return None

        description = request_body_spec.get("description")
        required = request_body_spec.get("required", False)

        content = request_body_spec.get("content", {})
        if not content:
            return None

        # 첫 번째 content type 사용
        content_type = list(content.keys())[0]
        media_type = content[content_type]

        schema_info = media_type.get("schema")
        examples = media_type.get("examples")

        return RequestBody(
            description=description,
            required=required,
            content_type=content_type,
            schema_info=schema_info,
            examples=examples,
        )

    def _extract_responses(self, operation: Dict[str, Any]) -> list[Response]:
        """Responses 추출"""
        responses = []
        responses_spec = operation.get("responses", {})

        for status_code, response_spec in responses_spec.items():
            description = response_spec.get("description")

            # Content 추출 (OpenAPI 3.x)
            content = response_spec.get("content", {})
            if content:
                content_type = list(content.keys())[0]
                media_type = content[content_type]
                schema_info = media_type.get("schema")
                examples = media_type.get("examples")
            else:
                # Swagger 2.x
                content_type = "application/json"
                schema_info = response_spec.get("schema")
                examples = response_spec.get("examples")

            responses.append(
                Response(
                    status_code=status_code,
                    description=description,
                    content_type=content_type,
                    schema_info=schema_info,
                    examples=examples,
                )
            )

        return responses
