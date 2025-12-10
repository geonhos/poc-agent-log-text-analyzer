"""
Phase 3: Embeddings and Vector Store 간단한 검증 스크립트
"""

import os
import sys
from pathlib import Path

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from legacy.embeddings import DocumentEmbedder
from legacy.pipeline import SpecIndexer
from legacy.vector_store import ChromaVectorStore


def test_embeddings():
    """Embedding 생성 테스트"""
    print("테스트 1: Embedding 생성")

    # API Key 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("  ⚠ OPENAI_API_KEY 환경변수가 설정되지 않았습니다")
        print("  ℹ 이 테스트를 건너뜁니다")
        return False

    try:
        embedder = DocumentEmbedder()

        # 간단한 텍스트 임베딩 생성
        text = "GET /users - List all users"
        embedding = embedder.embed_text(text)

        assert isinstance(embedding, list), "Embedding이 list가 아님"
        assert len(embedding) == 1536, f"Embedding 차원이 다름: {len(embedding)}"
        assert all(isinstance(x, float) for x in embedding), "Embedding 요소가 float이 아님"

        print(f"  ✓ Embedding 생성 성공")
        print(f"  ✓ 차원: {len(embedding)}")
        print(f"  ✓ 첫 5개 값: {embedding[:5]}")

        return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        return False


def test_vector_store():
    """Vector Store 테스트"""
    print("\n테스트 2: Vector Store (ChromaDB)")

    try:
        from common.models import Document

        # 메모리 모드로 Vector Store 생성
        vector_store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=None,  # 메모리 모드
            reset=True,
        )

        # 테스트 Document 생성 (임베딩 포함)
        doc1 = Document(
            id="test_doc_1",
            content="GET /users - List all users",
            metadata={"method": "GET", "path": "/users"},
            embedding=[0.1] * 1536,  # 가짜 임베딩
        )

        doc2 = Document(
            id="test_doc_2",
            content="POST /users - Create a new user",
            metadata={"method": "POST", "path": "/users"},
            embedding=[0.2] * 1536,  # 가짜 임베딩
        )

        # Document 추가
        vector_store.add_documents([doc1, doc2])

        assert vector_store.count() == 2, f"Document 개수가 다름: {vector_store.count()}"

        print(f"  ✓ Vector Store 생성 성공")
        print(f"  ✓ Document 추가: 2개")
        print(f"  ✓ 총 Document 개수: {vector_store.count()}")

        # ID로 조회
        retrieved = vector_store.get_document_by_id("test_doc_1")
        assert retrieved is not None, "Document 조회 실패"
        assert retrieved["id"] == "test_doc_1", "Document ID가 다름"

        print(f"  ✓ Document 조회 성공")

        # 검색 (가짜 쿼리 임베딩)
        results = vector_store.search(
            query_embedding=[0.15] * 1536,
            n_results=2,
        )

        assert len(results) == 2, f"검색 결과 개수가 다름: {len(results)}"

        print(f"  ✓ 유사도 검색 성공")
        print(f"  ✓ 검색 결과: {len(results)}개")

        return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_integration_pipeline():
    """통합 파이프라인 테스트"""
    print("\n테스트 3: 통합 파이프라인")

    # API Key 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("  ⚠ OPENAI_API_KEY 환경변수가 설정되지 않았습니다")
        print("  ℹ 이 테스트를 건너뜁니다")
        return False

    try:
        # 구성요소 초기화
        embedder = DocumentEmbedder()
        vector_store = ChromaVectorStore(
            collection_name="test_pipeline",
            persist_directory=None,
            reset=True,
        )

        # 파이프라인 생성
        indexer = SpecIndexer(
            embedder=embedder,
            vector_store=vector_store,
        )

        # Spec 파일 인덱싱
        spec_path = project_root / "data" / "specs" / "sample_users_api.yaml"
        collection = indexer.index_spec_file(spec_path)

        assert collection.count() == 5, f"Document 개수가 다름: {collection.count()}"
        assert vector_store.count() == 5, f"Vector Store의 Document 개수가 다름"

        print(f"\n  ✓ 파이프라인 실행 성공")
        print(f"  ✓ 인덱싱된 Document: {collection.count()}개")

        # 검색 테스트
        results = indexer.search(
            query_text="사용자 목록 조회",
            n_results=3,
        )

        assert len(results) > 0, "검색 결과가 없음"

        print(f"\n  ✓ 검색 성공: {len(results)}개 결과")
        for i, result in enumerate(results, 1):
            method = result["metadata"].get("method")
            path = result["metadata"].get("path")
            distance = result["distance"]
            print(f"    {i}. {method} {path} (distance: {distance:.4f})")

        return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Phase 3: Embeddings and Vector Store 검증 테스트")
    print("=" * 60)

    tests = [
        test_embeddings,
        test_vector_store,
        test_integration_pipeline,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_func in tests:
        try:
            result = test_func()
            if result is True:
                passed += 1
            elif result is False:
                skipped += 1
            else:
                failed += 1
        except AssertionError as e:
            print(f"\n✗ 테스트 실패: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ 에러 발생: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"결과: {passed}개 성공, {failed}개 실패, {skipped}개 건너뜀")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
