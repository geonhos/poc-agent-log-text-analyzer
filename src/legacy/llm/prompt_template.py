"""
Prompt Template

프롬프트 템플릿 관리 및 생성
"""

from string import Template
from typing import Any, Dict, List, Optional


class PromptTemplate:
    """
    프롬프트 템플릿

    변수를 포함한 프롬프트 템플릿을 관리하고 렌더링합니다.

    Example:
        template = PromptTemplate(
            "Analyze this log: ${log_text}\\nExtract API calls."
        )
        prompt = template.format(log_text="GET /users")
    """

    def __init__(self, template: str, few_shot_examples: Optional[List[Dict[str, str]]] = None):
        """
        Args:
            template: 템플릿 문자열 (${variable} 형식 사용)
            few_shot_examples: Few-shot 예제 목록
        """
        self.template = Template(template)
        self.few_shot_examples = few_shot_examples or []

    def format(self, **kwargs) -> str:
        """
        템플릿 렌더링

        Args:
            **kwargs: 템플릿 변수

        Returns:
            렌더링된 프롬프트
        """
        # Few-shot 예제 추가
        if self.few_shot_examples:
            examples_text = self._format_examples()
            kwargs["examples"] = examples_text

        return self.template.safe_substitute(**kwargs)

    def _format_examples(self) -> str:
        """
        Few-shot 예제 포맷팅

        Returns:
            포맷팅된 예제 텍스트
        """
        lines = []
        for idx, example in enumerate(self.few_shot_examples, 1):
            lines.append(f"Example {idx}:")
            lines.append(f"Input: {example.get('input', '')}")
            lines.append(f"Output: {example.get('output', '')}")
            lines.append("")

        return "\n".join(lines)

    def add_example(self, input_text: str, output_text: str) -> None:
        """
        Few-shot 예제 추가

        Args:
            input_text: 입력 예제
            output_text: 출력 예제
        """
        self.few_shot_examples.append({"input": input_text, "output": output_text})

    def __repr__(self) -> str:
        return f"<PromptTemplate(examples={len(self.few_shot_examples)})>"


# 사전 정의된 프롬프트 템플릿


class LogAnalysisPrompts:
    """로그 분석용 프롬프트 템플릿"""

    EXTRACT_API_CALLS = PromptTemplate(
        """You are an expert in analyzing logs and extracting API call information.

${examples}

Analyze the following log text and extract all API calls.

Log text:
${log_text}

Extract the following information for each API call:
1. HTTP method (GET, POST, PUT, DELETE, etc.)
2. Path/URL
3. Headers (if available)
4. Request body (if available)
5. Query parameters (if available)
6. Response status code (if available)

Return the result in JSON format as a list of API calls.

Example output format:
[
  {
    "method": "GET",
    "path": "/api/users",
    "headers": {},
    "body": null,
    "query_params": {},
    "status_code": 200
  }
]

JSON output:""",
        few_shot_examples=[
            {
                "input": 'Log: {"request": "GET /users", "status": 200}',
                "output": '[{"method": "GET", "path": "/users", "status_code": 200}]',
            }
        ],
    )

    ENHANCE_API_CALL = PromptTemplate(
        """You are an expert in API design and REST conventions.

Given a partial API call information, enhance it with:
1. Likely headers (Content-Type, Authorization, etc.)
2. Expected request/response structure
3. Common query parameters
4. Best practices

API Call:
Method: ${method}
Path: ${path}
${additional_info}

Provide enhancement suggestions in JSON format:
{
  "suggested_headers": {},
  "expected_request_body": {},
  "expected_response": {},
  "common_query_params": {},
  "notes": ""
}

JSON output:"""
    )

    VALIDATE_API_CALL = PromptTemplate(
        """You are an API validation expert.

Validate the following API call and identify any issues:

Method: ${method}
Path: ${path}
Headers: ${headers}
Body: ${body}
Query Parameters: ${query_params}

Check for:
1. Correct HTTP method for the operation
2. Valid path structure
3. Required headers present
4. Body structure appropriate for method
5. Security considerations

Provide validation result in JSON format:
{
  "is_valid": true/false,
  "issues": [],
  "warnings": [],
  "suggestions": []
}

JSON output:"""
    )


class CurlGenerationPrompts:
    """curl 생성용 프롬프트 템플릿"""

    GENERATE_CURL = PromptTemplate(
        """Generate a complete, executable curl command for the following API call.

Method: ${method}
URL: ${url}
Headers: ${headers}
Body: ${body}
Query Parameters: ${query_params}

Requirements:
1. Include all necessary headers
2. Properly escape special characters
3. Format JSON body correctly
4. Add common security headers if missing

Output only the curl command, nothing else:"""
    )


class PostmanPrompts:
    """Postman collection 생성용 프롬프트 템플릿"""

    GENERATE_POSTMAN_REQUEST = PromptTemplate(
        """Generate a Postman request object for the following API call.

Method: ${method}
URL: ${url}
Headers: ${headers}
Body: ${body}

Output in Postman Collection v2.1 format (JSON):"""
    )
