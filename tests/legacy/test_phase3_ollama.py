"""
Phase 3: Ollama Embeddings 테스트
"""

import sys
from pathlib import Path

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from legacy.embeddings import create_embedder
from legacy.pipeline import SpecIndexer
from legacy.vector_store import ChromaVectorStore


def test_ollama_embedder():
    """Ollama Embedder 테스트"""
    print("테스트 1: Ollama Embedder")

    try:
        # Ollama embedder 생성
        embedder = create_embedder("ollama", model="nomic-embed-text")

        # 간단한 텍스트 임베딩 생성
        text = "GET /users - List all users"
        embedding = embedder.embed_text(text)

        assert isinstance(embedding, list), "Embedding이 list가 아님"
        assert len(embedding) > 0, "Embedding이 비어있음"
        assert all(isinstance(x, float) for x in embedding), "Embedding 요소가 float이 아님"

        print(f"  ✓ Ollama 임베딩 생성 성공")
        print(f"  ✓ 차원: {len(embedding)}")
        print(f"  ✓ 첫 5개 값: {embedding[:5]}")

        return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        print(f"  ℹ Ollama가 실행 중인지 확인하세요: ollama serve")
        return False


def test_ollama_pipeline():
    """Ollama를 사용한 전체 파이프라인 테스트"""
    print("\n테스트 2: Ollama 통합 파이프라인")

    try:
        # Ollama embedder 생성
        embedder = create_embedder("ollama", model="nomic-embed-text")

        # Vector Store 생성
        vector_store = ChromaVectorStore(
            collection_name="test_ollama_pipeline",
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
    print("Phase 3: Ollama Embeddings 테스트")
    print("=" * 60)
    print("\n주의: 이 테스트는 Ollama가 실행 중이어야 합니다")
    print("시작: ollama serve")
    print("=" * 60)

    tests = [
        test_ollama_embedder,
        test_ollama_pipeline,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
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
    print(f"결과: {passed}개 성공, {failed}개 실패")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
