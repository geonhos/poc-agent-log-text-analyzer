"""
Phase 3: Import 검증 (의존성 없이 테스트)
"""

import sys
from pathlib import Path

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_imports():
    """모듈 import 테스트"""
    print("=" * 60)
    print("Phase 3: Import 검증")
    print("=" * 60)

    passed = []
    failed = []

    # 1. Embeddings 모듈
    print("\n테스트 1: Embeddings 모듈 import")
    try:
        # ollama_embedder, openai_embedder 파일 구문 검사
        for filename in ["base.py", "ollama_embedder.py", "openai_embedder.py"]:
            embedder_file = project_root / "src" / "legacy" / "embeddings" / filename
            with open(embedder_file, "r", encoding="utf-8") as f:
                code = f.read()
                compile(code, str(embedder_file), "exec")
            print(f"  ✓ {filename} 구문 검사 통과")
        passed.append("Embeddings module syntax")
    except SyntaxError as e:
        print(f"  ✗ 구문 에러: {e}")
        failed.append("Embeddings module syntax")
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        failed.append("Embeddings module")

    # 2. Vector Store 모듈
    print("\n테스트 2: Vector Store 모듈 import")
    try:
        chroma_file = project_root / "src" / "legacy" / "vector_store" / "chroma_store.py"
        with open(chroma_file, "r", encoding="utf-8") as f:
            code = f.read()
            compile(code, str(chroma_file), "exec")
        print("  ✓ chroma_store.py 구문 검사 통과")
        passed.append("Vector Store module syntax")
    except SyntaxError as e:
        print(f"  ✗ 구문 에러: {e}")
        failed.append("Vector Store module syntax")
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        failed.append("Vector Store module")

    # 3. Pipeline 모듈
    print("\n테스트 3: Pipeline 모듈 import")
    try:
        pipeline_file = project_root / "src" / "legacy" / "pipeline" / "spec_indexer.py"
        with open(pipeline_file, "r", encoding="utf-8") as f:
            code = f.read()
            compile(code, str(pipeline_file), "exec")
        print("  ✓ spec_indexer.py 구문 검사 통과")
        passed.append("Pipeline module syntax")
    except SyntaxError as e:
        print(f"  ✗ 구문 에러: {e}")
        failed.append("Pipeline module syntax")
    except Exception as e:
        print(f"  ✗ 에러: {e}")
        failed.append("Pipeline module")

    # 4. 파일 구조 검사
    print("\n테스트 4: 파일 구조 검사")
    required_files = [
        "src/legacy/embeddings/__init__.py",
        "src/legacy/embeddings/base.py",
        "src/legacy/embeddings/ollama_embedder.py",
        "src/legacy/embeddings/openai_embedder.py",
        "src/legacy/vector_store/__init__.py",
        "src/legacy/vector_store/chroma_store.py",
        "src/legacy/pipeline/__init__.py",
        "src/legacy/pipeline/spec_indexer.py",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} 없음")
            all_exist = False

    if all_exist:
        passed.append("File structure")
    else:
        failed.append("File structure")

    # 5. 코드 품질 검사
    print("\n테스트 5: 코드 품질 검사")
    quality_checks = []

    # Embedder 클래스들 존재 확인
    base_content = (project_root / "src" / "legacy" / "embeddings" / "base.py").read_text()
    ollama_content = (project_root / "src" / "legacy" / "embeddings" / "ollama_embedder.py").read_text()
    openai_content = (project_root / "src" / "legacy" / "embeddings" / "openai_embedder.py").read_text()

    if "class BaseEmbedder" in base_content:
        print("  ✓ BaseEmbedder 클래스 정의 확인")
        quality_checks.append(True)
    else:
        print("  ✗ BaseEmbedder 클래스 없음")
        quality_checks.append(False)

    if "class OllamaEmbedder" in ollama_content:
        print("  ✓ OllamaEmbedder 클래스 정의 확인")
        quality_checks.append(True)
    else:
        print("  ✗ OllamaEmbedder 클래스 없음")
        quality_checks.append(False)

    if "class OpenAIEmbedder" in openai_content:
        print("  ✓ OpenAIEmbedder 클래스 정의 확인")
        quality_checks.append(True)
    else:
        print("  ✗ OpenAIEmbedder 클래스 없음")
        quality_checks.append(False)

    # ChromaVectorStore 클래스 존재 확인
    chroma_content = (project_root / "src" / "legacy" / "vector_store" / "chroma_store.py").read_text()
    if "class ChromaVectorStore" in chroma_content:
        print("  ✓ ChromaVectorStore 클래스 정의 확인")
        quality_checks.append(True)
    else:
        print("  ✗ ChromaVectorStore 클래스 없음")
        quality_checks.append(False)

    # SpecIndexer 클래스 존재 확인
    indexer_content = (project_root / "src" / "legacy" / "pipeline" / "spec_indexer.py").read_text()
    if "class SpecIndexer" in indexer_content:
        print("  ✓ SpecIndexer 클래스 정의 확인")
        quality_checks.append(True)
    else:
        print("  ✗ SpecIndexer 클래스 없음")
        quality_checks.append(False)

    if all(quality_checks):
        passed.append("Code quality")
    else:
        failed.append("Code quality")

    # 결과 출력
    print("\n" + "=" * 60)
    print(f"결과: {len(passed)}개 성공, {len(failed)}개 실패")
    print("=" * 60)

    if failed:
        print("\n실패한 테스트:")
        for item in failed:
            print(f"  - {item}")

    print("\n주의: 실제 동작 테스트는 openai와 chromadb 패키지 설치 후 가능합니다")
    print("설치 명령: poetry install")

    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(test_imports())
