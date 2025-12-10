"""
Base Embedder

Embedding provider 추상 인터페이스
"""

from abc import ABC, abstractmethod
from typing import List

from common.models import Document, DocumentCollection


class EmbeddingError(Exception):
    """Embedding 생성 에러"""

    pass


class BaseEmbedder(ABC):
    """Embedder 추상 클래스"""

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        임베딩 벡터의 차원 반환

        Returns:
            임베딩 차원
        """
        pass

    def embed_document(self, document: Document) -> Document:
        """
        Document에 임베딩 추가

        Args:
            document: 임베딩을 추가할 Document

        Returns:
            임베딩이 추가된 Document

        Raises:
            EmbeddingError: 임베딩 생성 실패 시
        """
        embedding = self.embed_text(document.content)
        document.embedding = embedding
        return document

    def embed_collection(self, collection: DocumentCollection) -> DocumentCollection:
        """
        DocumentCollection의 모든 Document에 임베딩 추가

        Args:
            collection: DocumentCollection

        Returns:
            임베딩이 추가된 DocumentCollection

        Raises:
            EmbeddingError: 임베딩 생성 실패 시
        """
        # 모든 document의 content 추출
        texts = [doc.content for doc in collection.documents]

        # 배치로 임베딩 생성
        embeddings = self.embed_texts(texts)

        # 각 document에 임베딩 할당
        for doc, embedding in zip(collection.documents, embeddings):
            doc.embedding = embedding

        return collection
