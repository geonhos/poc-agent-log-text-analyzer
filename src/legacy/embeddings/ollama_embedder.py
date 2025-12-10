"""
Ollama Embedder

Ollama를 사용한 로컬 임베딩 생성
"""

import httpx
from typing import List, Optional

from .base import BaseEmbedder, EmbeddingError


class OllamaEmbedder(BaseEmbedder):
    """Ollama 기반 임베딩 생성기"""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
        batch_size: int = 100,
    ):
        """
        Args:
            model: Ollama 모델명 (예: nomic-embed-text, mxbai-embed-large)
            base_url: Ollama 서버 URL
            batch_size: 배치 처리 크기
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.batch_size = batch_size
        self.client = httpx.Client(timeout=300.0)  # 5분 타임아웃

        # 모델이 사용 가능한지 확인
        try:
            self._check_model_available()
        except Exception as e:
            raise EmbeddingError(f"Ollama 모델 확인 실패: {e}")

    def _check_model_available(self):
        """모델이 사용 가능한지 확인"""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])

            available_models = [m["name"] for m in models]

            # 모델이 없으면 pull 시도
            if self.model not in available_models:
                print(f"모델 '{self.model}' 다운로드 중...")
                pull_response = self.client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model},
                    timeout=600.0,  # 10분 타임아웃
                )
                pull_response.raise_for_status()
                print(f"  ✓ 모델 '{self.model}' 다운로드 완료")
        except httpx.HTTPError as e:
            raise EmbeddingError(f"Ollama 서버 연결 실패: {e}")

    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩으로 변환

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터

        Raises:
            EmbeddingError: 임베딩 생성 실패 시
        """
        try:
            response = self.client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )
            response.raise_for_status()
            result = response.json()
            return result["embedding"]
        except Exception as e:
            raise EmbeddingError(f"임베딩 생성 실패: {e}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 배치로 임베딩 변환

        Args:
            texts: 임베딩할 텍스트 목록

        Returns:
            임베딩 벡터 목록

        Raises:
            EmbeddingError: 임베딩 생성 실패 시
        """
        if not texts:
            return []

        embeddings = []

        # 배치 처리
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]

            # Ollama는 단일 텍스트만 지원하므로 순차 처리
            for text in batch:
                try:
                    embedding = self.embed_text(text)
                    embeddings.append(embedding)
                except Exception as e:
                    raise EmbeddingError(f"배치 임베딩 생성 실패: {e}")

        return embeddings

    def get_embedding_dimension(self) -> int:
        """
        현재 모델의 임베딩 차원 반환

        Returns:
            임베딩 벡터의 차원
        """
        # 모델별 기본 차원
        # nomic-embed-text: 768 차원
        # mxbai-embed-large: 1024 차원
        # 실제 차원은 첫 임베딩을 생성해서 확인
        try:
            test_embedding = self.embed_text("test")
            return len(test_embedding)
        except Exception:
            # 기본값 반환
            if "nomic" in self.model:
                return 768
            elif "mxbai" in self.model:
                return 1024
            else:
                return 768  # 기본값

    def __del__(self):
        """클라이언트 정리"""
        if hasattr(self, "client"):
            self.client.close()
