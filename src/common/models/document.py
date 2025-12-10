"""
Document 모델

벡터 검색에 사용될 문서 표현
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    벡터 검색용 문서 모델

    API spec의 각 endpoint를 하나의 Document로 표현
    """

    # 문서 식별자
    id: str = Field(..., description="문서 고유 ID")

    # 문서 내용
    content: str = Field(..., description="문서 텍스트 내용 (검색에 사용)")

    # 메타데이터
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="문서 메타데이터 (필터링 및 추가 정보)"
    )

    # 임베딩 (선택사항, 생성 후 추가됨)
    embedding: Optional[list[float]] = Field(None, description="벡터 임베딩")

    def __init__(self, **data):
        super().__init__(**data)
        # metadata에 기본값 설정
        if "source" not in self.metadata:
            self.metadata["source"] = "api_spec"

    @classmethod
    def from_api_endpoint(
        cls,
        endpoint_id: str,
        text_representation: str,
        method: str,
        path: str,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
        **extra_metadata,
    ) -> "Document":
        """
        APIEndpoint로부터 Document 생성

        Args:
            endpoint_id: 엔드포인트 ID
            text_representation: 텍스트 표현
            method: HTTP 메서드
            path: API 경로
            tags: 태그 목록
            summary: 요약
            description: 설명
            **extra_metadata: 추가 메타데이터

        Returns:
            Document 객체
        """
        metadata = {
            "source": "api_spec",
            "type": "endpoint",
            "method": method,
            "path": path,
            "tags": tags or [],
            "summary": summary,
            "description": description,
            **extra_metadata,
        }

        return cls(id=endpoint_id, content=text_representation, metadata=metadata)

    def to_dict(self) -> Dict[str, Any]:
        """
        Document를 dict로 변환 (ChromaDB 저장용)

        Returns:
            딕셔너리 형태의 문서
        """
        result = {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
        }
        if self.embedding is not None:
            result["embedding"] = self.embedding
        return result

    def get_display_text(self) -> str:
        """
        사용자에게 표시할 텍스트

        Returns:
            표시용 텍스트
        """
        method = self.metadata.get("method", "")
        path = self.metadata.get("path", "")
        summary = self.metadata.get("summary", "")

        parts = [f"{method} {path}"]
        if summary:
            parts.append(f"- {summary}")

        return " ".join(parts)


class DocumentCollection(BaseModel):
    """Document 컬렉션"""

    name: str = Field(..., description="컬렉션 이름")
    documents: list[Document] = Field(default_factory=list, description="문서 목록")

    def add_document(self, document: Document) -> None:
        """문서 추가"""
        self.documents.append(document)

    def get_document_by_id(self, doc_id: str) -> Optional[Document]:
        """ID로 문서 찾기"""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None

    def count(self) -> int:
        """문서 개수"""
        return len(self.documents)

    def get_all_ids(self) -> list[str]:
        """모든 문서 ID 목록"""
        return [doc.id for doc in self.documents]
