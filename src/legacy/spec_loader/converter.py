"""
APISpec를 Document로 변환하는 컨버터
"""

from common.models import APISpec, Document, DocumentCollection


class SpecToDocumentConverter:
    """APISpec을 Document 컬렉션으로 변환"""

    def __init__(self, collection_name: str | None = None):
        """
        Args:
            collection_name: 컬렉션 이름 (기본값: spec의 title 사용)
        """
        self.collection_name = collection_name

    def convert(self, api_spec: APISpec) -> DocumentCollection:
        """
        APISpec을 DocumentCollection으로 변환

        Args:
            api_spec: 변환할 API spec

        Returns:
            Document 컬렉션
        """
        collection_name = self.collection_name or api_spec.title

        collection = DocumentCollection(name=collection_name)

        for endpoint in api_spec.endpoints:
            document = self._endpoint_to_document(endpoint, api_spec)
            collection.add_document(document)

        return collection

    def _endpoint_to_document(self, endpoint, api_spec: APISpec) -> Document:
        """
        APIEndpoint를 Document로 변환

        Args:
            endpoint: API endpoint
            api_spec: 전체 API spec (메타데이터용)

        Returns:
            Document 객체
        """
        # 고유 ID 생성
        doc_id = endpoint.get_unique_id()

        # 검색용 텍스트 표현
        text_representation = endpoint.get_text_representation()

        # 추가 메타데이터
        extra_metadata = {
            "api_title": api_spec.title,
            "api_version": api_spec.version,
            "operation_id": endpoint.operation_id,
            "deprecated": endpoint.deprecated,
        }

        # Document 생성
        document = Document.from_api_endpoint(
            endpoint_id=doc_id,
            text_representation=text_representation,
            method=endpoint.method.value,
            path=endpoint.path,
            tags=endpoint.tags,
            summary=endpoint.summary,
            description=endpoint.description,
            **extra_metadata,
        )

        return document
