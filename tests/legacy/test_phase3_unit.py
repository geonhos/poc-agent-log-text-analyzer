"""
Phase 3: 단위 테스트 (의존성 없이 검증)
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_ollama_embedder_interface():
    """OllamaEmbedder 인터페이스 테스트"""
    print("테스트 1: OllamaEmbedder 인터페이스")

    try:
        # httpx를 mock
        with patch("legacy.embeddings.ollama_embedder.httpx") as mock_httpx:
            # Mock client 설정
            mock_client = MagicMock()
            mock_httpx.Client.return_value = mock_client

            # GET /api/tags 응답 mock
            mock_tags_response = MagicMock()
            mock_tags_response.json.return_value = {
                "models": [{"name": "nomic-embed-text"}]
            }
            mock_client.get.return_value = mock_tags_response

            # POST /api/embeddings 응답 mock
            mock_embed_response = MagicMock()
            mock_embed_response.json.return_value = {
                "embedding": [0.1] * 768
            }
            mock_client.post.return_value = mock_embed_response

            from legacy.embeddings.ollama_embedder import OllamaEmbedder

            # Embedder 생성
            embedder = OllamaEmbedder(model="nomic-embed-text")

            # 텍스트 임베딩
            text = "GET /users - List all users"
            embedding = embedder.embed_text(text)

            assert isinstance(embedding, list), "Embedding이 list가 아님"
            assert len(embedding) == 768, f"Embedding 차원이 다름: {len(embedding)}"

            print(f"  ✓ OllamaEmbedder 인스턴스 생성 성공")
            print(f"  ✓ embed_text 메서드 호출 성공")
            print(f"  ✓ Embedding 차원: {len(embedding)}")

            # 배치 임베딩
            texts = ["text1", "text2", "text3"]
            embeddings = embedder.embed_texts(texts)

            assert len(embeddings) == 3, f"Embeddings 개수가 다름: {len(embeddings)}"
            print(f"  ✓ embed_texts 메서드 호출 성공")

            # 차원 확인
            dim = embedder.get_embedding_dimension()
            assert dim == 768, f"차원이 다름: {dim}"
            print(f"  ✓ get_embedding_dimension 메서드 호출 성공")

            return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_embedder_interface():
    """OpenAIEmbedder 인터페이스 테스트"""
    print("\n테스트 2: OpenAIEmbedder 인터페이스")

    try:
        from legacy.embeddings.openai_embedder import OpenAIEmbedder, HAS_OPENAI

        if not HAS_OPENAI:
            print("  ⚠ openai 패키지 없음 - 에러 처리 테스트")
            # openai 없을 때 에러 발생하는지 확인
            try:
                embedder = OpenAIEmbedder(api_key="test")
                print("  ✗ 에러가 발생하지 않음")
                return False
            except Exception as e:
                if "openai 패키지" in str(e):
                    print(f"  ✓ 올바른 에러 메시지: {e}")
                    return True
                else:
                    print(f"  ✗ 예상과 다른 에러: {e}")
                    return False

        print("  ✓ OpenAIEmbedder 클래스 import 성공")
        return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store_interface():
    """ChromaVectorStore 인터페이스 테스트"""
    print("\n테스트 3: ChromaVectorStore 인터페이스")

    try:
        # chromadb를 mock
        with patch("legacy.vector_store.chroma_store.chromadb") as mock_chromadb:
            # Mock client와 collection 설정
            mock_client = MagicMock()
            mock_collection = MagicMock()

            mock_chromadb.Client.return_value = mock_client
            mock_client.get_or_create_collection.return_value = mock_collection

            # Collection 메서드 mock
            mock_collection.count.return_value = 0
            mock_collection.add.return_value = None
            mock_collection.query.return_value = {
                "ids": [["doc1"]],
                "documents": [["test content"]],
                "metadatas": [[{"method": "GET"}]],
                "distances": [[0.5]],
            }

            from legacy.vector_store import ChromaVectorStore
            from common.models import Document

            # Vector Store 생성
            vector_store = ChromaVectorStore(collection_name="test")

            print(f"  ✓ ChromaVectorStore 인스턴스 생성 성공")

            # Document 추가 테스트
            doc = Document(
                id="test_doc",
                content="test content",
                metadata={"method": "GET"},
                embedding=[0.1] * 768,
            )

            vector_store.add_document(doc)
            print(f"  ✓ add_document 메서드 호출 성공")

            # 검색 테스트
            results = vector_store.search(query_embedding=[0.1] * 768, n_results=1)
            assert len(results) == 1, f"검색 결과 개수가 다름: {len(results)}"
            print(f"  ✓ search 메서드 호출 성공")

            return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_interface():
    """SpecIndexer 인터페이스 테스트"""
    print("\n테스트 4: SpecIndexer 인터페이스")

    try:
        # 모든 의존성을 mock
        with patch("legacy.embeddings.ollama_embedder.httpx"), \
             patch("legacy.vector_store.chroma_store.chromadb"):

            from legacy.embeddings import create_embedder
            from legacy.vector_store import ChromaVectorStore
            from legacy.pipeline import SpecIndexer

            # create_embedder 함수 테스트
            print("  ✓ create_embedder 함수 import 성공")

            # SpecIndexer 클래스 import 테스트
            print("  ✓ SpecIndexer 클래스 import 성공")

            return True
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Phase 3: 단위 테스트 (Mock 사용)")
    print("=" * 60)

    tests = [
        test_ollama_embedder_interface,
        test_openai_embedder_interface,
        test_vector_store_interface,
        test_pipeline_interface,
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
        except Exception as e:
            print(f"\n✗ 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"결과: {passed}개 성공, {failed}개 실패")
    print("=" * 60)

    if failed == 0:
        print("\n✅ 모든 단위 테스트 통과")
        print("주의: 실제 Ollama/ChromaDB 연동 테스트는 별도로 필요합니다")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
