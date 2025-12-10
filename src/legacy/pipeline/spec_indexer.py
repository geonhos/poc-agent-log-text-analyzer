"""
Spec Indexer

API Spec 파일을 로드하여 Vector Store에 인덱싱하는 통합 파이프라인
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from common.models import APISpec, DocumentCollection
from legacy.embeddings import DocumentEmbedder
from legacy.spec_loader import OpenAPISpecLoader, SpecToDocumentConverter
from legacy.vector_store import ChromaVectorStore


class SpecIndexer:
    """API Spec 인덱싱 파이프라인"""

    def __init__(
        self,
        embedder: DocumentEmbedder,
        vector_store: ChromaVectorStore,
        spec_loader: Optional[OpenAPISpecLoader] = None,
        converter: Optional[SpecToDocumentConverter] = None,
    ):
        """
        Args:
            embedder: DocumentEmbedder 인스턴스
            vector_store: ChromaVectorStore 인스턴스
            spec_loader: OpenAPISpecLoader (None이면 기본값 생성)
            converter: SpecToDocumentConverter (None이면 기본값 생성)
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.spec_loader = spec_loader or OpenAPISpecLoader(validate=False)
        self.converter = converter or SpecToDocumentConverter()

    def index_spec_file(self, spec_file_path: Union[str, Path]) -> DocumentCollection:
        """
        단일 Spec 파일 인덱싱

        Args:
            spec_file_path: Spec 파일 경로

        Returns:
            인덱싱된 DocumentCollection

        Raises:
            Exception: 인덱싱 실패 시
        """
        # 1. Spec 파일 로드
        print(f"Loading spec file: {spec_file_path}")
        api_spec = self.spec_loader.load_from_file(spec_file_path)
        print(f"  ✓ Loaded: {api_spec.title} v{api_spec.version}")
        print(f"  ✓ Endpoints: {len(api_spec.endpoints)}")

        # 2. Document로 변환
        print("Converting to documents...")
        doc_collection = self.converter.convert(api_spec)
        print(f"  ✓ Documents: {doc_collection.count()}")

        # 3. Embedding 생성
        print("Generating embeddings...")
        doc_collection = self.embedder.embed_collection(doc_collection)
        print(f"  ✓ Embeddings generated: {doc_collection.count()}")

        # 4. Vector Store에 저장
        print("Storing in vector database...")
        self.vector_store.add_collection(doc_collection)
        print(f"  ✓ Stored: {doc_collection.count()} documents")

        return doc_collection

    def index_spec_files(self, spec_file_paths: List[Union[str, Path]]) -> List[DocumentCollection]:
        """
        여러 Spec 파일 인덱싱

        Args:
            spec_file_paths: Spec 파일 경로 목록

        Returns:
            인덱싱된 DocumentCollection 목록

        Raises:
            Exception: 인덱싱 실패 시
        """
        collections = []

        for i, spec_file_path in enumerate(spec_file_paths, 1):
            print(f"\n[{i}/{len(spec_file_paths)}] Processing {spec_file_path}")
            try:
                collection = self.index_spec_file(spec_file_path)
                collections.append(collection)
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                raise

        return collections

    def search(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        텍스트로 검색

        Args:
            query_text: 검색 쿼리 텍스트
            n_results: 반환할 결과 개수
            filter_metadata: 메타데이터 필터 (예: {"method": "GET"})

        Returns:
            검색 결과 목록

        Raises:
            Exception: 검색 실패 시
        """
        print(f"Searching for: '{query_text}'")

        # 텍스트를 임베딩으로 변환하여 검색
        results = self.vector_store.search_by_text(
            query_text=query_text,
            embedder=self.embedder,
            n_results=n_results,
            where=filter_metadata,
        )

        print(f"  ✓ Found {len(results)} results")

        return results

    def get_stats(self) -> Dict[str, int]:
        """
        인덱스 통계 정보

        Returns:
            통계 정보 (document 개수 등)
        """
        return {
            "total_documents": self.vector_store.count(),
        }
