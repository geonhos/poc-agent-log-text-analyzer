"""
Spec Loader 간단한 검증 스크립트 (pytest 없이 실행)
"""

import sys
from pathlib import Path

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from common.models import APISpec, DocumentCollection
from legacy.spec_loader import OpenAPISpecLoader, SpecLoaderError, SpecToDocumentConverter


def test_load_yaml_file():
    """YAML 파일 로드 테스트"""
    print("테스트 1: YAML 파일 로드")

    spec_path = project_root / "data" / "specs" / "sample_users_api.yaml"
    loader = OpenAPISpecLoader(validate=False)

    spec = loader.load_from_file(spec_path)

    assert isinstance(spec, APISpec), "APISpec 객체가 아님"
    assert spec.title == "Users API", f"Title이 다름: {spec.title}"
    assert spec.version == "1.0.0", f"Version이 다름: {spec.version}"
    assert spec.openapi_version == "3.0.0", f"OpenAPI version이 다름: {spec.openapi_version}"

    print(f"  ✓ Title: {spec.title}")
    print(f"  ✓ Version: {spec.version}")
    print(f"  ✓ OpenAPI: {spec.openapi_version}")
    print(f"  ✓ Base URL: {spec.base_url}")
    print(f"  ✓ Endpoints: {len(spec.endpoints)}개")


def test_extract_endpoints():
    """Endpoint 추출 테스트"""
    print("\n테스트 2: Endpoint 추출")

    spec_path = project_root / "data" / "specs" / "sample_users_api.yaml"
    loader = OpenAPISpecLoader(validate=False)
    spec = loader.load_from_file(spec_path)

    assert len(spec.endpoints) == 5, f"Endpoint 개수가 다름: {len(spec.endpoints)}"

    # GET /users 확인
    get_users = spec.get_endpoint("GET", "/users")
    assert get_users is not None, "GET /users를 찾을 수 없음"
    assert get_users.summary == "List all users", f"Summary가 다름: {get_users.summary}"

    print(f"  ✓ 전체 Endpoint 개수: {len(spec.endpoints)}")
    print(f"  ✓ GET /users: {get_users.summary}")
    print(f"  ✓ Tags: {get_users.tags}")


def test_extract_parameters():
    """Parameters 추출 테스트"""
    print("\n테스트 3: Parameters 추출")

    spec_path = project_root / "data" / "specs" / "sample_users_api.yaml"
    loader = OpenAPISpecLoader(validate=False)
    spec = loader.load_from_file(spec_path)

    get_users = spec.get_endpoint("GET", "/users")
    assert len(get_users.parameters) == 2, f"파라미터 개수가 다름: {len(get_users.parameters)}"

    for param in get_users.parameters:
        print(f"  ✓ {param.name} ({param.location.value}): required={param.required}")


def test_convert_to_documents():
    """Document 변환 테스트"""
    print("\n테스트 4: Document 변환")

    spec_path = project_root / "data" / "specs" / "sample_users_api.yaml"
    loader = OpenAPISpecLoader(validate=False)
    spec = loader.load_from_file(spec_path)

    converter = SpecToDocumentConverter()
    collection = converter.convert(spec)

    assert isinstance(collection, DocumentCollection), "DocumentCollection이 아님"
    assert collection.count() == 5, f"Document 개수가 다름: {collection.count()}"

    print(f"  ✓ Collection name: {collection.name}")
    print(f"  ✓ Document 개수: {collection.count()}")

    # 첫 번째 document 확인
    if collection.documents:
        doc = collection.documents[0]
        print(f"  ✓ 첫 번째 Document ID: {doc.id}")
        print(f"  ✓ Method: {doc.metadata.get('method')}")
        print(f"  ✓ Path: {doc.metadata.get('path')}")
        print(f"  ✓ Content 길이: {len(doc.content)}자")


def test_document_text_representation():
    """Document 텍스트 표현 테스트"""
    print("\n테스트 5: Document 텍스트 표현")

    spec_path = project_root / "data" / "specs" / "sample_users_api.yaml"
    loader = OpenAPISpecLoader(validate=False)
    spec = loader.load_from_file(spec_path)

    converter = SpecToDocumentConverter()
    collection = converter.convert(spec)

    # GET /users document 찾기
    get_users_doc = None
    for doc in collection.documents:
        if doc.metadata.get("method") == "GET" and doc.metadata.get("path") == "/users":
            get_users_doc = doc
            break

    assert get_users_doc is not None, "GET /users document를 찾을 수 없음"
    assert "GET /users" in get_users_doc.content, "텍스트에 'GET /users'가 없음"
    assert "List all users" in get_users_doc.content, "텍스트에 summary가 없음"

    print("  ✓ GET /users Document content:")
    print("  " + "\n  ".join(get_users_doc.content.split("\n")[:5]))  # 처음 5줄만 출력


def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Phase 2: Spec Loader 검증 테스트")
    print("=" * 60)

    tests = [
        test_load_yaml_file,
        test_extract_endpoints,
        test_extract_parameters,
        test_convert_to_documents,
        test_document_text_representation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ 테스트 실패: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ 에러 발생: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"결과: {passed}개 성공, {failed}개 실패")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
