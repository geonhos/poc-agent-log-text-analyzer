"""
ChromaDB Vector Store

ChromaDB를 사용한 벡터 저장 및 유사도 검색
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

from common.models import Document, DocumentCollection


class VectorStoreError(Exception):
    """Vector Store 에러"""

    pass


class ChromaVectorStore:
    """ChromaDB 기반 벡터 저장소"""

    def __init__(
        self,
        collection_name: str = "api_specs",
        persist_directory: Optional[str] = None,
        reset: bool = False,
    ):
        """
        Args:
            collection_name: Collection 이름
            persist_directory: 데이터 저장 디렉토리 (None이면 메모리 모드)
            reset: True면 기존 collection 삭제 후 재생성
        """
        self.collection_name = collection_name

        # ChromaDB 클라이언트 초기화
        if persist_directory:
            persist_path = Path(persist_directory)
            persist_path.mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=Settings(anonymized_telemetry=False),
            )
        else:
            # 메모리 모드
            self.client = chromadb.Client(
                settings=Settings(anonymized_telemetry=False),
            )

        # Collection 가져오기 또는 생성
        if reset:
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass  # Collection이 없으면 무시

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # 코사인 유사도 사용
        )

    def add_document(self, document: Document) -> None:
        """
        단일 Document 추가

        Args:
            document: 추가할 Document (embedding 필수)

        Raises:
            VectorStoreError: Document에 embedding이 없거나 추가 실패 시
        """
        if not document.embedding:
            raise VectorStoreError(f"Document {document.id}에 embedding이 없습니다")

        try:
            self.collection.add(
                ids=[document.id],
                embeddings=[document.embedding],
                documents=[document.content],
                metadatas=[document.metadata],
            )
        except Exception as e:
            raise VectorStoreError(f"Document 추가 실패: {e}")

    def add_documents(self, documents: List[Document]) -> None:
        """
        여러 Document 추가

        Args:
            documents: 추가할 Document 목록 (모든 document에 embedding 필수)

        Raises:
            VectorStoreError: Document에 embedding이 없거나 추가 실패 시
        """
        if not documents:
            return

        # embedding 검증
        for doc in documents:
            if not doc.embedding:
                raise VectorStoreError(f"Document {doc.id}에 embedding이 없습니다")

        try:
            # ChromaDB는 metadata에 list, dict를 지원하지 않으므로 변환 필요
            sanitized_metadatas = [self._sanitize_metadata(doc.metadata) for doc in documents]

            self.collection.add(
                ids=[doc.id for doc in documents],
                embeddings=[doc.embedding for doc in documents],
                documents=[doc.content for doc in documents],
                metadatas=sanitized_metadatas,
            )
        except Exception as e:
            raise VectorStoreError(f"Documents 추가 실패: {e}")

    def add_collection(self, doc_collection: DocumentCollection) -> None:
        """
        DocumentCollection 전체 추가

        Args:
            doc_collection: 추가할 DocumentCollection

        Raises:
            VectorStoreError: 추가 실패 시
        """
        self.add_documents(doc_collection.documents)

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        벡터 유사도 검색

        Args:
            query_embedding: 검색할 쿼리 벡터
            n_results: 반환할 결과 개수
            where: 메타데이터 필터 (예: {"method": "GET"})

        Returns:
            검색 결과 목록. 각 결과는 다음 필드를 포함:
            - id: Document ID
            - content: Document 내용
            - metadata: Document 메타데이터
            - distance: 유사도 거리 (낮을수록 유사)

        Raises:
            VectorStoreError: 검색 실패 시
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
            )

            # 결과 포맷팅
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append(
                        {
                            "id": results["ids"][0][i],
                            "content": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i],
                        }
                    )

            return formatted_results
        except Exception as e:
            raise VectorStoreError(f"검색 실패: {e}")

    def search_by_text(
        self,
        query_text: str,
        embedder,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        텍스트로 검색 (임베딩 자동 생성)

        Args:
            query_text: 검색할 텍스트
            embedder: DocumentEmbedder 인스턴스
            n_results: 반환할 결과 개수
            where: 메타데이터 필터

        Returns:
            검색 결과 목록

        Raises:
            VectorStoreError: 검색 실패 시
        """
        # 텍스트를 임베딩으로 변환
        query_embedding = embedder.embed_text(query_text)

        # 검색
        return self.search(query_embedding, n_results, where)

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 Document 조회

        Args:
            doc_id: Document ID

        Returns:
            Document 정보 또는 None

        Raises:
            VectorStoreError: 조회 실패 시
        """
        try:
            results = self.collection.get(ids=[doc_id])

            if results["ids"]:
                return {
                    "id": results["ids"][0],
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0],
                    "embedding": results["embeddings"][0] if results["embeddings"] else None,
                }
            return None
        except Exception as e:
            raise VectorStoreError(f"Document 조회 실패: {e}")

    def count(self) -> int:
        """
        저장된 Document 개수

        Returns:
            Document 개수
        """
        return self.collection.count()

    def delete_document(self, doc_id: str) -> None:
        """
        Document 삭제

        Args:
            doc_id: 삭제할 Document ID

        Raises:
            VectorStoreError: 삭제 실패 시
        """
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            raise VectorStoreError(f"Document 삭제 실패: {e}")

    def clear(self) -> None:
        """
        모든 Document 삭제

        Raises:
            VectorStoreError: 삭제 실패 시
        """
        try:
            # Collection 삭제 후 재생성
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            raise VectorStoreError(f"Collection 초기화 실패: {e}")

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        ChromaDB 호환 metadata로 변환

        ChromaDB는 str, int, float, bool만 지원하므로
        list, dict 등은 JSON 문자열로 변환

        Args:
            metadata: 원본 metadata

        Returns:
            ChromaDB 호환 metadata
        """
        import json

        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                # None은 빈 문자열로 변환
                sanitized[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                # 기본 타입은 그대로 사용
                sanitized[key] = value
            elif isinstance(value, list):
                # 리스트는 JSON 문자열로 변환 (또는 쉼표로 구분)
                if value and isinstance(value[0], str):
                    # 문자열 리스트는 쉼표로 구분
                    sanitized[key] = ",".join(value)
                else:
                    # 다른 타입의 리스트는 JSON으로
                    sanitized[key] = json.dumps(value)
            elif isinstance(value, dict):
                # 딕셔너리는 JSON 문자열로 변환
                sanitized[key] = json.dumps(value)
            else:
                # 기타 타입은 문자열로 변환
                sanitized[key] = str(value)

        return sanitized
