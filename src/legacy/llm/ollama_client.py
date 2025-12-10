"""
Ollama LLM Client

로컬 Ollama를 사용하는 LLM 클라이언트
"""

import json
from typing import Dict, List, Optional

import requests

from .base import BaseLLM, LLMError, LLMResponse


class OllamaLLM(BaseLLM):
    """
    Ollama LLM 클라이언트

    로컬에서 실행 중인 Ollama 서버와 통신합니다.
    """

    def __init__(
        self,
        model: str = "llama2:7b-chat-q4_0",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        **kwargs,
    ):
        """
        Args:
            model: Ollama 모델명
            base_url: Ollama 서버 URL
            timeout: 요청 타임아웃 (초)
            **kwargs: 추가 설정
        """
        super().__init__(model, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        텍스트 생성

        Args:
            prompt: 입력 프롬프트
            system: 시스템 메시지
            temperature: 온도 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터

        Returns:
            LLMResponse 객체

        Raises:
            LLMError: 생성 실패 시
        """
        try:
            url = f"{self.base_url}/api/generate"

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            }

            if system:
                payload["system"] = system

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            # 추가 옵션 병합
            if kwargs:
                payload["options"].update(kwargs)

            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            return LLMResponse(
                content=result.get("response", ""),
                model=self.model,
                usage={
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0)
                    + result.get("eval_count", 0),
                },
                raw_response=result,
            )

        except requests.exceptions.RequestException as e:
            raise LLMError(f"Ollama API 요청 실패: {e}")
        except Exception as e:
            raise LLMError(f"텍스트 생성 중 에러 발생: {e}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        채팅 형식 대화

        Args:
            messages: 메시지 목록 [{"role": "user|assistant|system", "content": "..."}]
            temperature: 온도
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터

        Returns:
            LLMResponse 객체

        Raises:
            LLMError: 생성 실패 시
        """
        try:
            url = f"{self.base_url}/api/chat"

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            # 추가 옵션 병합
            if kwargs:
                payload["options"].update(kwargs)

            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            # 응답 메시지 추출
            message = result.get("message", {})
            content = message.get("content", "")

            return LLMResponse(
                content=content,
                model=self.model,
                usage={
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0)
                    + result.get("eval_count", 0),
                },
                raw_response=result,
            )

        except requests.exceptions.RequestException as e:
            raise LLMError(f"Ollama API 요청 실패: {e}")
        except Exception as e:
            raise LLMError(f"채팅 생성 중 에러 발생: {e}")

    def check_connection(self) -> bool:
        """
        Ollama 서버 연결 확인

        Returns:
            연결 성공 여부
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """
        사용 가능한 모델 목록 조회

        Returns:
            모델명 목록

        Raises:
            LLMError: 조회 실패 시
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()

            result = response.json()
            models = result.get("models", [])

            return [model.get("name", "") for model in models if model.get("name")]

        except Exception as e:
            raise LLMError(f"모델 목록 조회 실패: {e}")
