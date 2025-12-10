"""
Spec Loader 테스트
"""

import sys
from pathlib import Path

import pytest

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from common.models import APISpec, DocumentCollection
from legacy.spec_loader import OpenAPISpecLoader, SpecLoaderError, SpecToDocumentConverter


class TestOpenAPISpecLoader:
    """OpenAPISpecLoader 테스트"""

    @pytest.fixture
    def sample_spec_path(self):
        """샘플 spec 파일 경로"""
        return project_root / "data" / "specs" / "sample_users_api.yaml"

    @pytest.fixture
    def loader(self):
        """Spec loader 인스턴스"""
        return OpenAPISpecLoader(validate=False)  # 빠른 테스트를 위해 검증 비활성화

    def test_load_yaml_file(self, loader, sample_spec_path):
        """YAML 파일 로드 테스트"""
        spec = loader.load_from_file(sample_spec_path)

        assert isinstance(spec, APISpec)
        assert spec.title == "Users API"
        assert spec.version == "1.0.0"
        assert spec.openapi_version == "3.0.0"

    def test_extract_endpoints(self, loader, sample_spec_path):
        """Endpoint 추출 테스트"""
        spec = loader.load_from_file(sample_spec_path)

        # 5개의 endpoint가 있어야 함 (GET /users, POST /users, GET /users/{userId}, PUT /users/{userId}, DELETE /users/{userId})
        assert len(spec.endpoints) == 5

        # GET /users 확인
        get_users = spec.get_endpoint("GET", "/users")
        assert get_users is not None
        assert get_users.summary == "List all users"
        assert "users" in get_users.tags

    def test_extract_parameters(self, loader, sample_spec_path):
        """Parameters 추출 테스트"""
        spec = loader.load_from_file(sample_spec_path)

        get_users = spec.get_endpoint("GET", "/users")
        assert len(get_users.parameters) == 2

        # limit 파라미터 확인
        limit_param = next((p for p in get_users.parameters if p.name == "limit"), None)
        assert limit_param is not None
        assert limit_param.required is False
        assert limit_param.location.value == "query"

    def test_extract_request_body(self, loader, sample_spec_path):
        """Request Body 추출 테스트"""
        spec = loader.load_from_file(sample_spec_path)

        post_users = spec.get_endpoint("POST", "/users")
        assert post_users.request_body is not None
        assert post_users.request_body.required is True
        assert post_users.request_body.content_type == "application/json"

    def test_extract_responses(self, loader, sample_spec_path):
        """Responses 추출 테스트"""
        spec = loader.load_from_file(sample_spec_path)

        get_users = spec.get_endpoint("GET", "/users")
        assert len(get_users.responses) > 0

        # 200 응답 확인
        response_200 = next((r for r in get_users.responses if r.status_code == "200"), None)
        assert response_200 is not None
        assert response_200.description == "Successful response"

    def test_path_parameters(self, loader, sample_spec_path):
        """Path 파라미터 테스트"""
        spec = loader.load_from_file(sample_spec_path)

        get_user = spec.get_endpoint("GET", "/users/{userId}")
        assert get_user is not None

        # userId path 파라미터 확인
        user_id_param = next((p for p in get_user.parameters if p.name == "userId"), None)
        assert user_id_param is not None
        assert user_id_param.location.value == "path"
        assert user_id_param.required is True

    def test_file_not_found(self, loader):
        """존재하지 않는 파일 테스트"""
        with pytest.raises(SpecLoaderError):
            loader.load_from_file("nonexistent.yaml")

    def test_base_url_extraction(self, loader, sample_spec_path):
        """Base URL 추출 테스트"""
        spec = loader.load_from_file(sample_spec_path)

        assert spec.base_url == "https://api.example.com/v1"


class TestSpecToDocumentConverter:
    """SpecToDocumentConverter 테스트"""

    @pytest.fixture
    def sample_spec(self):
        """샘플 spec 로드"""
        spec_path = project_root / "data" / "specs" / "sample_users_api.yaml"
        loader = OpenAPISpecLoader(validate=False)
        return loader.load_from_file(spec_path)

    @pytest.fixture
    def converter(self):
        """Converter 인스턴스"""
        return SpecToDocumentConverter()

    def test_convert_to_documents(self, converter, sample_spec):
        """APISpec을 DocumentCollection으로 변환 테스트"""
        collection = converter.convert(sample_spec)

        assert isinstance(collection, DocumentCollection)
        assert collection.name == "Users API"
        assert collection.count() == 5  # 5개의 endpoint

    def test_document_content(self, converter, sample_spec):
        """Document 내용 테스트"""
        collection = converter.convert(sample_spec)

        # 첫 번째 document 확인
        docs = collection.documents
        assert len(docs) > 0

        doc = docs[0]
        assert doc.id is not None
        assert doc.content is not None
        assert "metadata" in doc.model_dump()

    def test_document_metadata(self, converter, sample_spec):
        """Document 메타데이터 테스트"""
        collection = converter.convert(sample_spec)

        doc = collection.documents[0]
        metadata = doc.metadata

        assert "method" in metadata
        assert "path" in metadata
        assert "api_title" in metadata
        assert metadata["api_title"] == "Users API"
        assert "tags" in metadata

    def test_document_text_representation(self, converter, sample_spec):
        """Document 텍스트 표현 테스트"""
        collection = converter.convert(sample_spec)

        # GET /users document 찾기
        get_users_doc = None
        for doc in collection.documents:
            if doc.metadata.get("method") == "GET" and doc.metadata.get("path") == "/users":
                get_users_doc = doc
                break

        assert get_users_doc is not None
        assert "GET /users" in get_users_doc.content
        assert "List all users" in get_users_doc.content  # summary 포함

    def test_document_unique_ids(self, converter, sample_spec):
        """Document ID 고유성 테스트"""
        collection = converter.convert(sample_spec)

        ids = collection.get_all_ids()
        assert len(ids) == len(set(ids))  # 모든 ID가 고유해야 함


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
