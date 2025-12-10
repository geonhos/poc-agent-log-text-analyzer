"""
OpenAI Embedder

OpenAI API를 사용한 임베딩 생성
"""

import os
from typing import List, Optional

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None  # type: ignore

from .base import BaseEmbedder, EmbeddingError


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI API 기반 임베딩 생성기"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        batch_size: int = 100,
    ):
        """
        Args:
            api_key: OpenAI API 키 (None이면 환경변수에서 읽음)
            model: 임베딩 모델명
            batch_size: 배치 처리 크기
        """
        if not HAS_OPENAI:
            raise EmbeddingError("openai 패키지가 설치되지 않았습니다. 'pip install openai' 실행")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EmbeddingError("OpenAI API key가 설정되지 않았습니다")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.batch_size = batch_size

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
            response = self.client.embeddings.create(
                input=text,
                model=self.model,
            )
            return response.data[0].embedding
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

            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model,
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                raise EmbeddingError(f"배치 임베딩 생성 실패: {e}")

        return embeddings

    def get_embedding_dimension(self) -> int:
        """
        현재 모델의 임베딩 차원 반환

        Returns:
            임베딩 벡터의 차원
        """
        # text-embedding-3-small: 1536 차원
        # text-embedding-3-large: 3072 차원
        # text-embedding-ada-002: 1536 차원
        if "large" in self.model:
            return 3072
        else:
            return 1536
