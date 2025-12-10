# API Log Text Analyzer

텍스트 또는 로그에서 API 호출 정보를 추출하고, API spec 문서를 기반으로 요청의 정합성을 검사하며 유효한 curl 명령어를 생성하는 자동화 도구

## 📋 주요 기능

1. **텍스트/로그 입력 처리**: 다양한 형식의 로그 및 텍스트 입력 지원
2. **API Spec 문서 검색**: 입력된 정보를 API spec 문서에서 매칭
3. **정합성 검사**: 요청 파라미터, 헤더, 바디의 유효성 검증
4. **Curl 생성**: 검증된 정보를 기반으로 실행 가능한 curl 명령어 생성
5. **피드백 루프**: 사용자 만족도 기반 재검색 및 개선

## 🎯 프로젝트 전략

이 프로젝트는 3가지 버전으로 구현되어 각각의 장단점을 비교합니다:

1. **Legacy 버전** (Phase 1-23): 프레임워크 없이 순수 Python으로 직접 구현
2. **LangChain 버전** (Phase 24): LangChain 프레임워크 활용
3. **LlamaIndex 버전** (Phase 25): LlamaIndex 프레임워크 활용

### 왜 Legacy First?
- LLM 파이프라인의 내부 동작 원리 깊이 이해
- 모든 컴포넌트에 대한 완전한 제어
- 프레임워크의 장단점을 객관적으로 평가할 수 있는 baseline
- 필요에 따라 세밀한 튜닝 가능

## 🏗️ 프로젝트 구조

```
poc-agent-log-text-analyzer/
├── src/
│   ├── legacy/                  # Legacy 구현 (순수 Python)
│   │   ├── parsers/            # 로그/텍스트 파서
│   │   ├── spec_loader/        # API spec 문서 로더
│   │   ├── embeddings/         # 임베딩 생성
│   │   ├── vector_store/       # ChromaDB 직접 연동
│   │   ├── matcher/            # API spec 매칭 엔진
│   │   ├── llm/                # Claude API 직접 연동
│   │   ├── validator/          # 정합성 검사
│   │   ├── curl_generator/     # curl 명령어 생성
│   │   ├── cache/              # 캐싱 시스템
│   │   └── cli/                # CLI 인터페이스
│   ├── langchain_version/       # LangChain 구현
│   ├── llamaindex_version/      # LlamaIndex 구현
│   └── common/                  # 공통 유틸리티
├── tests/                       # 테스트
├── docs/                        # 문서
├── data/                        # API spec 문서
├── benchmarks/                  # 성능 비교
└── comparisons/                 # 기능 비교
```

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.9 이상
- Poetry (의존성 관리)
- Anthropic API 키
- OpenAI API 키 (임베딩용)

### 설치

1. 저장소 클론
```bash
git clone https://github.com/geonhos/poc-agent-log-text-analyzer.git
cd poc-agent-log-text-analyzer
```

2. 의존성 설치
```bash
# Legacy 버전만 설치
make install

# LangChain 버전 포함
make install-langchain

# LlamaIndex 버전 포함
make install-llamaindex

# 모든 버전 설치
make install-all
```

3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 입력
```

### 기본 사용법

```bash
# API spec 파일 로드
analyzer load-spec data/specs/your-api-spec.yaml

# 로그 파일 분석
analyzer analyze logs/your-log-file.log

# 대화형 모드
analyzer interactive

# 텍스트 직접 입력
analyzer analyze-text "POST /api/users with body {name: 'John'}"
```

## 🛠️ 개발

### 개발 환경 설정

```bash
# 의존성 설치
make install

# 코드 포맷팅
make format

# 린팅
make lint

# 타입 체크
make type-check

# 테스트 실행
make test

# 테스트 (커버리지 포함)
make test-cov

# 모든 검사 실행
make all
```

### 테스트

```bash
# 전체 테스트
make test

# Unit 테스트만
make test-unit

# Integration 테스트만
make test-integration

# 커버리지 리포트
make test-cov
```

## 📚 기술 스택

### Legacy 버전
- **LLM**: Anthropic Claude API (직접 연동)
- **벡터 DB**: ChromaDB (직접 연동)
- **임베딩**: OpenAI Embeddings 또는 HuggingFace
- **API Spec 파싱**: pydantic-openapi, openapi-spec-validator
- **CLI**: Click
- **캐싱**: diskcache
- **검증**: jsonschema, pydantic

### LangChain 버전
- **프레임워크**: LangChain
- **LLM**: ChatAnthropic
- **벡터 스토어**: Chroma (LangChain integration)
- **체인**: RetrievalQA, ConversationalRetrievalChain
- **메모리**: ConversationBufferMemory

### LlamaIndex 버전
- **프레임워크**: LlamaIndex
- **LLM**: Anthropic integration
- **인덱스**: VectorStoreIndex
- **쿼리 엔진**: QueryEngine
- **메모리**: ChatMemoryBuffer

## 📖 문서

상세한 문서는 [TASKS.md](./TASKS.md)를 참조하세요.

- [프로젝트 개요](./TASKS.md#프로젝트-개요)
- [구현 전략](./TASKS.md#구현-전략)
- [Phase별 상세 태스크](./TASKS.md#구현-태스크)
- [비교 및 벤치마크](./TASKS.md#phase-26-비교-및-벤치마크)

## 🤝 기여

기여는 언제나 환영합니다! 다음 단계를 따라주세요:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 라이선스

This project is licensed under the MIT License.

## 🔗 관련 링크

- [GitHub Issues](https://github.com/geonhos/poc-agent-log-text-analyzer/issues)
- [Task Document](./TASKS.md)

## 📧 연락처

- GitHub: [@geonhos](https://github.com/geonhos)

---

**현재 진행 상황**: Phase 1 완료 - 프로젝트 초기 설정
