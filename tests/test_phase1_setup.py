"""
Phase 1 설정 검증 테스트

프로젝트 구조, 환경 설정, 기본 import 등을 테스트합니다.
"""

import os
import sys
from pathlib import Path


def test_project_structure():
    """프로젝트 디렉토리 구조가 올바른지 검증"""
    project_root = Path(__file__).parent.parent

    # 필수 디렉토리 확인
    required_dirs = [
        "src/legacy",
        "src/legacy/parsers",
        "src/legacy/spec_loader",
        "src/legacy/embeddings",
        "src/legacy/vector_store",
        "src/legacy/matcher",
        "src/legacy/llm",
        "src/legacy/validator",
        "src/legacy/curl_generator",
        "src/legacy/cache",
        "src/legacy/cli",
        "src/common",
        "src/common/models",
        "src/common/config",
        "src/common/utils",
        "src/langchain_version",
        "src/llamaindex_version",
        "tests",
        "docs",
        "data",
        "benchmarks",
    ]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"디렉토리가 존재하지 않음: {dir_path}"
        assert full_path.is_dir(), f"디렉토리가 아님: {dir_path}"


def test_init_files():
    """__init__.py 파일들이 존재하는지 확인"""
    project_root = Path(__file__).parent.parent

    # __init__.py가 있어야 하는 디렉토리
    init_required_dirs = [
        "src",
        "src/legacy",
        "src/legacy/parsers",
        "src/legacy/spec_loader",
        "src/legacy/embeddings",
        "src/legacy/vector_store",
        "src/legacy/matcher",
        "src/legacy/llm",
        "src/legacy/validator",
        "src/legacy/curl_generator",
        "src/legacy/cache",
        "src/legacy/cli",
        "src/common",
        "src/common/models",
        "src/common/config",
        "src/common/utils",
    ]

    for dir_path in init_required_dirs:
        init_file = project_root / dir_path / "__init__.py"
        assert init_file.exists(), f"__init__.py가 없음: {dir_path}"


def test_config_files():
    """설정 파일들이 존재하는지 확인"""
    project_root = Path(__file__).parent.parent

    required_files = [
        "pyproject.toml",
        ".gitignore",
        ".env.example",
        ".flake8",
        "Makefile",
        "README.md",
        "TASKS.md",
    ]

    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"파일이 존재하지 않음: {file_path}"
        assert full_path.is_file(), f"파일이 아님: {file_path}"


def test_pyproject_toml():
    """pyproject.toml의 기본 구조 확인"""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    with open(pyproject_path) as f:
        content = f.read()

    # 필수 섹션 확인
    assert "[tool.poetry]" in content, "[tool.poetry] 섹션 없음"
    assert "[tool.poetry.dependencies]" in content, "[tool.poetry.dependencies] 섹션 없음"
    assert "[tool.poetry.group.dev.dependencies]" in content, "dev dependencies 섹션 없음"

    # 핵심 의존성 확인
    assert "anthropic" in content, "anthropic 의존성 없음"
    assert "chromadb" in content, "chromadb 의존성 없음"
    assert "openai" in content, "openai 의존성 없음"
    assert "pydantic" in content, "pydantic 의존성 없음"
    assert "click" in content, "click 의존성 없음"

    # 개발 도구 확인
    assert "black" in content, "black 없음"
    assert "mypy" in content, "mypy 없음"
    assert "pytest" in content, "pytest 없음"


def test_env_example():
    """.env.example 파일 검증"""
    project_root = Path(__file__).parent.parent
    env_example_path = project_root / ".env.example"

    with open(env_example_path) as f:
        content = f.read()

    # 필수 환경 변수 확인
    required_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "CHROMA_DB_PATH",
        "CLAUDE_MODEL",
        "EMBEDDING_MODEL",
    ]

    for var in required_vars:
        assert var in content, f"환경 변수 없음: {var}"


def test_gitignore():
    """.gitignore 파일 검증"""
    project_root = Path(__file__).parent.parent
    gitignore_path = project_root / ".gitignore"

    with open(gitignore_path) as f:
        content = f.read()

    # 필수 패턴 확인
    required_patterns = [
        ".env",
        "__pycache__",
        "*.py[cod]",  # *.pyc, *.pyo, *.pyd를 커버
        ".venv",
        ".mypy_cache",
        "chroma_db",
    ]

    for pattern in required_patterns:
        assert pattern in content, f".gitignore에 패턴 없음: {pattern}"


def test_makefile():
    """Makefile 검증"""
    project_root = Path(__file__).parent.parent
    makefile_path = project_root / "Makefile"

    with open(makefile_path) as f:
        content = f.read()

    # 필수 타겟 확인
    required_targets = [
        "install",
        "format",
        "lint",
        "type-check",
        "test",
        "clean",
    ]

    for target in required_targets:
        assert f"{target}:" in content, f"Makefile 타겟 없음: {target}"


def test_basic_imports():
    """기본 Python 모듈 import 테스트"""
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"

    # sys.path에 src 추가
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # 기본 import 테스트
    try:
        import legacy
        import common
        import langchain_version
        import llamaindex_version
    except ImportError as e:
        assert False, f"모듈 import 실패: {e}"


if __name__ == "__main__":
    # 간단한 테스트 러너
    import traceback

    tests = [
        test_project_structure,
        test_init_files,
        test_config_files,
        test_pyproject_toml,
        test_env_example,
        test_gitignore,
        test_makefile,
        test_basic_imports,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n총 {passed + failed}개 테스트 중 {passed}개 성공, {failed}개 실패")
    sys.exit(0 if failed == 0 else 1)
