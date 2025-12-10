# API Log Text Analyzer - Task Document

## 프로젝트 개요
텍스트 또는 로그에서 API 호출 정보를 추출하고, API spec 문서를 기반으로 요청의 정합성을 검사하며 유효한 curl 명령어를 생성하는 자동화 도구

## 주요 기능
1. **텍스트/로그 입력 처리**: 다양한 형식의 로그 및 텍스트 입력 지원
2. **API Spec 문서 검색**: 입력된 정보를 API spec 문서에서 매칭
3. **정합성 검사**: 요청 파라미터, 헤더, 바디의 유효성 검증
4. **Curl 생성**: 검증된 정보를 기반으로 실행 가능한 curl 명령어 생성
5. **피드백 루프**: 사용자 만족도 기반 재검색 및 개선

## 구현 전략

### 3단계 구현 접근법
1. **Phase 1-10: Legacy 구현** (프레임워크 없이 순수 Python)
   - Claude API 직접 연동
   - ChromaDB 직접 사용
   - 모든 로직 직접 구현
   - 기본 기능 완성 및 검증

2. **Phase 11-23: Legacy 개선 및 안정화**
   - 에러 처리, 캐싱, 보안 강화
   - 성능 최적화
   - 대용량 처리 및 확장성

3. **Phase 24-26: 프레임워크 버전 구현 및 비교**
   - LangChain 버전 구현
   - LlamaIndex 버전 구현
   - 3가지 버전 비교 및 벤치마크

### 왜 Legacy First?
- **학습**: LLM 파이프라인의 내부 동작 원리 이해
- **제어**: 모든 컴포넌트에 대한 완전한 제어
- **비교 기준**: 프레임워크의 장단점을 객관적으로 평가할 수 있는 baseline
- **최적화**: 필요에 따라 세밀한 튜닝 가능
- **디버깅**: 문제 발생 시 원인 파악 용이

## 기술 스택

### Version 1: Legacy (Phase 1-23)
- **언어**: Python 3.9+
- **LLM**: Anthropic Claude API (직접 연동)
- **벡터 DB**: ChromaDB (직접 연동)
- **임베딩**: OpenAI Embeddings 또는 HuggingFace
- **API Spec 파싱**: pydantic-openapi, openapi-spec-validator
- **HTTP 클라이언트**: httpx 또는 requests
- **CLI**: Click 또는 Typer
- **캐싱**: functools.lru_cache, diskcache
- **검증**: jsonschema, pydantic

### Version 2: LangChain (Phase 24)
- **프레임워크**: LangChain
- **LLM**: ChatAnthropic
- **벡터 스토어**: Chroma (LangChain integration)
- **체인**: RetrievalQA, ConversationalRetrievalChain
- **메모리**: ConversationBufferMemory
- **프롬프트**: PromptTemplate, FewShotPromptTemplate
- **캐싱**: LangChain Cache

### Version 3: LlamaIndex (Phase 25)
- **프레임워크**: LlamaIndex
- **LLM**: Anthropic integration
- **인덱스**: VectorStoreIndex
- **쿼리 엔진**: QueryEngine
- **메모리**: ChatMemoryBuffer
- **문서 로더**: SimpleDirectoryReader

## 프로젝트 구조
```
poc-agent-log-text-analyzer/
├── src/
│   ├── legacy/                  # Legacy 구현 (Phase 1-23)
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
│   │
│   ├── langchain_version/       # LangChain 구현 (Phase 24)
│   │   ├── chains/
│   │   ├── agents/
│   │   ├── retrievers/
│   │   └── cli/
│   │
│   ├── llamaindex_version/      # LlamaIndex 구현 (Phase 25)
│   │   ├── indices/
│   │   ├── query_engines/
│   │   ├── retrievers/
│   │   └── cli/
│   │
│   └── common/                  # 공통 유틸리티
│       ├── models/             # 데이터 모델 (Pydantic)
│       ├── config/             # 설정 관리
│       └── utils/              # 공통 유틸
│
├── tests/
│   ├── legacy/
│   ├── langchain_version/
│   ├── llamaindex_version/
│   └── integration/
│
├── benchmarks/                  # 성능 비교 (Phase 26)
│   ├── accuracy/               # 정확도 측정
│   ├── performance/            # 속도, 메모리 측정
│   ├── cost/                   # API 비용 분석
│   └── reports/                # 벤치마크 리포트
│
├── comparisons/                 # 기능 비교 (Phase 26)
│   ├── feature_matrix.md       # 기능 비교표
│   ├── architecture.md         # 아키텍처 비교
│   └── recommendations.md      # 사용 시나리오별 추천
│
├── data/                        # API spec 문서 저장소
│   ├── specs/
│   └── samples/
│
├── docs/
│   ├── legacy/
│   ├── langchain/
│   └── llamaindex/
│
└── examples/                    # 사용 예제
```

---

# 구현 태스크

## PART 1: Legacy 구현 (Phase 1-10)

### Phase 1: 프로젝트 초기 설정 (Legacy)
- [ ] Python 프로젝트 구조 생성
  - src/legacy/ 디렉토리 구조
  - src/common/ 공통 모듈
- [ ] 의존성 관리 설정 (poetry 권장)
  ```toml
  # 핵심 의존성
  anthropic = "^0.8.0"
  chromadb = "^0.4.0"
  openai = "^1.0.0"  # embeddings
  pydantic = "^2.0"
  click = "^8.1"
  httpx = "^0.25"
  ```
- [ ] 개발 환경 설정
  - black, isort, flake8
  - mypy (타입 체킹)
  - pytest
- [ ] Git 설정 및 .gitignore 업데이트
- [ ] 기본 README 작성
- [ ] 환경 변수 설정 (.env.example)

### Phase 2: API Spec 문서 로더 (Legacy)
- [ ] OpenAPI/Swagger spec 파일 파서 구현
  - JSON/YAML 파일 읽기
  - pydantic 모델로 검증
  - openapi-spec-validator 활용
- [ ] API spec 정보 추출 로직
  - Endpoint paths 추출
  - HTTP methods 파싱
  - Parameters (query, path, header, body) 추출
  - Request/Response schemas 추출
- [ ] 메타데이터 구조화
  - Endpoint별 메타데이터 생성
  - 검색 최적화를 위한 텍스트 표현
- [ ] Document 객체 생성
  - 각 endpoint를 Document로 변환
  - 메타데이터 첨부

### Phase 3: 임베딩 및 벡터 스토어 (Legacy)
- [ ] 임베딩 생성 모듈
  - OpenAI embeddings API 연동
  - 또는 HuggingFace sentence-transformers
  - 배치 처리 지원
- [ ] ChromaDB 직접 연동
  - Collection 생성 및 관리
  - Document 추가 로직
  - 메타데이터 필터링
- [ ] 벡터 검색 구현
  - 유사도 기반 검색
  - Top-k 검색
  - 메타데이터 필터 적용
- [ ] 인덱스 관리
  - 인덱스 저장 및 로드
  - 인덱스 업데이트

### Phase 4: 텍스트/로그 파서 (Legacy)
- [ ] 로그 포맷 감지
  - JSON 로그 자동 감지
  - Plain text 패턴 인식
  - HTTP request 로그 인식
- [ ] 다양한 로그 형식 파서 구현
  - JSON 로그 파서
  - Plain text 로그 파서
  - HTTP request 로그 파서
  - 커스텀 로그 포맷 지원
- [ ] API 호출 정보 추출
  - 정규표현식 기반 추출
  - URL/Endpoint 파싱
  - HTTP method 추출
  - Headers 파싱
  - Request body 추출
  - Query parameters 추출
- [ ] 추출 결과 정규화

### Phase 5: Claude API 직접 연동 (Legacy)
- [ ] Anthropic Claude API 클라이언트 구현
  - anthropic 라이브러리 사용
  - API 키 관리
  - 에러 처리
- [ ] 프롬프트 템플릿 시스템
  - 템플릿 엔진 구현 (Jinja2 또는 직접 구현)
  - Few-shot 예제 관리
  - 동적 프롬프트 생성
- [ ] 응답 파싱
  - JSON 응답 파싱
  - 에러 핸들링
  - 재시도 로직

### Phase 6: API Spec 매칭 엔진 (Legacy)
- [ ] RAG 파이프라인 구현
  1. 로그에서 추출한 정보를 쿼리로 변환
  2. 벡터 검색으로 후보 API spec 조회
  3. 후보 spec을 컨텍스트로 Claude에 전달
  4. Claude가 최적 spec 선택 및 분석
- [ ] 검색 쿼리 최적화
  - 추출된 정보를 검색 친화적 텍스트로 변환
  - 하이브리드 검색 (키워드 + 벡터)
- [ ] 컨텍스트 구성
  - 검색된 spec을 프롬프트에 삽입
  - 컨텍스트 윈도우 관리
- [ ] 신뢰도 점수 계산
  - Claude 응답에서 신뢰도 추출
  - 벡터 유사도 점수 결합
- [ ] 다중 후보 처리
  - Top-N 후보 반환
  - 순위화 및 필터링

### Phase 7: 정합성 검사 (Legacy)
- [ ] JSON Schema 기반 검증
  - jsonschema 라이브러리 활용
  - OpenAPI schema로 request 검증
- [ ] Request 파라미터 검증
  - Required fields 체크
  - 데이터 타입 검증
  - Enum/제약조건 검증
  - Format 검증 (email, uri, date 등)
- [ ] Request body 스키마 검증
  - Nested object 검증
  - Array 검증
- [ ] Header 검증
  - Required headers 확인
  - Authorization 검증
- [ ] 상세 에러 메시지 생성
  - 필드별 에러 위치 표시
  - 수정 제안

### Phase 8: Curl 생성기 (Legacy)
- [ ] Curl 명령어 템플릿
  - 기본 템플릿 정의
  - 옵션별 템플릿
- [ ] 파라미터 변환
  - Headers → -H 옵션
  - Request body → -d 옵션
  - Query parameters → URL 인코딩
  - Authentication → -u 또는 -H
  - HTTP method → -X 옵션
- [ ] Curl 포맷팅
  - 가독성 있는 줄바꿈
  - 이스케이핑 처리
- [ ] 실행 가능성 검증
  - 문법 체크
  - 필수 옵션 확인

### Phase 9: CLI 인터페이스 (Legacy)
- [ ] CLI 프레임워크 구현 (Click 권장)
- [ ] 명령어 구조
  ```bash
  # API spec 로드
  analyzer load-spec <spec-file>

  # 로그 분석 (원샷)
  analyzer analyze <log-file> [options]

  # 대화형 모드
  analyzer interactive

  # 텍스트 입력
  analyzer analyze-text "<text>"
  ```
- [ ] 옵션 및 플래그
  - --output-format (json/table/plain)
  - --verbose
  - --no-cache
  - --top-k (후보 개수)
- [ ] 대화형 모드 구현
  - 사용자 입력 루프
  - 결과 표시
  - 만족도 확인
- [ ] 결과 출력 포맷팅
  - Rich 라이브러리로 테이블 출력
  - JSON 출력
  - 컬러 지원

### Phase 10: 피드백 루프 (Legacy)
- [ ] 사용자 만족도 입력
  - CLI에서 yes/no 입력
  - 불만족 시 피드백 수집
- [ ] 피드백 기반 재검색
  - 피드백을 쿼리에 반영
  - 제외할 spec 관리
  - 검색 파라미터 조정
- [ ] 대화 히스토리 관리
  - 세션 컨텍스트 유지
  - 이전 결과 참조
- [ ] 반복 개선
  - 최대 재시도 횟수 설정
  - 개선 로직 구현

---

## PART 2: Legacy 개선 및 안정화 (Phase 11-23)

### Phase 11: 에러 처리 및 복구 전략
- [ ] 로그 파싱 실패 처리
  - 부분 파싱 지원
  - Fallback 파서
  - 수동 입력 모드
- [ ] API spec 매칭 실패 처리
  - 유사도 임계값 조정
  - 전체 spec 목록 표시
  - 수동 선택 인터페이스
- [ ] Claude API 오류 처리
  - Retry with exponential backoff
  - Rate limit 처리
  - Fallback to 규칙 기반 매칭
  - 오프라인 모드 (캐시만 사용)
- [ ] ChromaDB 오류 처리
  - 연결 실패 처리
  - 인덱스 손상 복구
- [ ] Graceful degradation
  - 일부 기능 실패 시 계속 진행
  - 명확한 에러 메시지

### Phase 12: 캐싱 및 성능 최적화
- [ ] LLM 응답 캐싱
  - diskcache 또는 Redis
  - 쿼리 해시 기반 캐싱
  - TTL 설정
  - 캐시 크기 제한
- [ ] 임베딩 캐싱
  - 동일 텍스트 재계산 방지
  - 파일 기반 캐시
- [ ] API spec 파싱 결과 캐싱
  - 파일 해시 기반 캐싱
  - 변경 감지
- [ ] 벡터 검색 최적화
  - 배치 검색
  - 인덱스 최적화
- [ ] 병렬 처리
  - asyncio 활용
  - 멀티프로세싱 (배치 처리)
- [ ] 메모리 최적화
  - 스트리밍 처리
  - 청크 단위 처리

### Phase 13: 보안 및 민감정보 처리
- [ ] API 키 관리
  - 환경 변수 사용
  - python-dotenv
  - 키 암호화 (선택사항)
- [ ] 로그 내 민감정보 마스킹
  - 정규표현식 패턴
    - API 키 패턴
    - 토큰 패턴
    - 비밀번호 패턴
    - 이메일, 전화번호
  - 자동 마스킹 적용
- [ ] 생성된 curl의 민감정보 처리
  - Authorization 헤더 마스킹 옵션
  - --mask-sensitive 플래그
- [ ] 안전한 파일 처리
  - 권한 체크
  - 경로 traversal 방지
- [ ] HTTPS 강제

### Phase 14: 배치 및 대용량 처리
- [ ] 대용량 로그 파일 스트리밍
  - 라인 단위 읽기
  - 메모리 효율적 처리
- [ ] 여러 로그 파일 일괄 처리
  - 디렉토리 스캔
  - glob 패턴 지원
  - 프로그레스 바 (tqdm)
- [ ] 병렬 처리
  - concurrent.futures
  - 워커 풀 관리
- [ ] 결과 일괄 저장
  - CSV 출력
  - JSON Lines 출력
  - SQLite 저장
- [ ] 체크포인트 및 재시작
  - 진행 상황 저장
  - 중단된 작업 재개

### Phase 15: 실시간 모니터링
- [ ] 로그 스트림 모니터링
  - tail -f 스타일
  - 파일 변경 감지 (watchdog)
- [ ] 실시간 분석
  - 새 로그 라인 자동 분석
  - 결과 스트리밍 출력
- [ ] 알림 시스템
  - 특정 패턴 감지
  - 웹훅 연동 (Slack, Discord)
- [ ] 메트릭 수집
  - 처리 시간 추적
  - 성공률 계산
  - 메트릭 출력 (JSON)

### Phase 16: 결과 저장 및 히스토리
- [ ] SQLite 로컬 저장소
  - 데이터베이스 스키마 설계
  - 분석 결과 저장
  - 히스토리 조회
- [ ] 세션 관리
  - 세션 ID 생성
  - 세션별 결과 그룹화
  - 세션 재개
- [ ] 결과 비교
  - 이전 분석과 비교
  - Diff 표시
- [ ] Export 기능
  - JSON export
  - CSV export
  - HTML 보고서 (선택사항)

### Phase 17: API Spec 버전 관리
- [ ] 여러 버전 동시 관리
  - 버전별 Collection
  - 버전 자동 감지
- [ ] Spec 업데이트 감지
  - 파일 해시 비교
  - 변경 감지 시 재인덱싱
- [ ] 멀티 서비스 지원
  - 서비스별 네임스페이스
  - Collection 이름 규칙
- [ ] Spec 충돌 해결
  - 우선순위 설정
  - 명시적 버전 선택

### Phase 18: 커스터마이징 및 확장성
- [ ] 플러그인 시스템
  - 파서 플러그인 인터페이스
  - 동적 로딩
- [ ] 설정 파일 (YAML/TOML)
  - 프로젝트별 설정
  - 글로벌 설정
  - 설정 우선순위
- [ ] 사용자 정의 규칙
  - 정규표현식 룰 파일
  - 우선순위 설정
- [ ] 템플릿 커스터마이징
  - Curl 템플릿
  - 출력 템플릿
- [ ] Hook 시스템
  - Pre-parse hook
  - Post-match hook
  - Pre-validation hook

### Phase 19: 고급 프롬프트 엔지니어링
- [ ] Few-shot 예제 관리
  - 예제 데이터셋 구축
  - 예제 선택 로직
  - 동적 예제 삽입
- [ ] Chain-of-thought
  - 단계별 추론 프롬프트
  - 중간 결과 활용
- [ ] 프롬프트 버전 관리
  - 여러 프롬프트 템플릿
  - A/B 테스팅
- [ ] 컨텍스트 압축
  - 긴 spec 요약
  - 핵심 정보 추출
- [ ] 학습 데이터 수집
  - 피드백 저장
  - Fine-tuning 준비 (선택사항)

### Phase 20: 사용성 개선
- [ ] 대화형 튜토리얼
  - 첫 실행 시 가이드
  - 예제 워크플로우
- [ ] 자동 완성
  - argcomplete 연동
  - 파일 경로 자동완성
- [ ] Rich 출력
  - Syntax highlighting
  - 테이블 포맷팅
  - 프로그레스 바
  - 색상 테마
- [ ] Diff 표시
  - 원본 vs 추출 결과
  - 예상 vs 실제
- [ ] 클립보드 연동
  - pyperclip
  - 원클릭 복사

### Phase 21: 테스트 및 품질 보증
- [ ] Unit 테스트
  - pytest
  - 각 모듈별 테스트
  - Mock 사용
- [ ] Integration 테스트
  - End-to-end 테스트
  - 실제 API spec 사용
- [ ] 테스트 데이터
  - 다양한 로그 샘플
  - 여러 API spec
  - Edge case
- [ ] 커버리지 측정
  - pytest-cov
  - 80% 이상 목표
- [ ] 성능 벤치마크
  - 처리 속도 측정
  - 메모리 사용량 측정

### Phase 22: CI/CD
- [ ] GitHub Actions
  - 자동 테스트
  - 린팅 체크
  - 타입 체크
  - 커버리지 리포트
- [ ] Pre-commit hooks
  - black, isort
  - flake8
  - mypy
- [ ] 자동 릴리스
  - 버전 태깅
  - Changelog 생성
  - PyPI 배포 (선택사항)
- [ ] Docker 이미지
  - Dockerfile
  - Multi-stage build
  - 경량 이미지 (alpine)

### Phase 23: 문서화
- [ ] README 완성
  - 설치 가이드
  - 빠른 시작
  - 예제
- [ ] 사용자 가이드
  - 상세 사용법
  - 옵션 설명
  - 트러블슈팅
- [ ] API 문서
  - Docstring 작성
  - Sphinx 문서 (선택사항)
- [ ] 아키텍처 문서
  - 시스템 다이어그램
  - 데이터 플로우
  - 설계 결정 사항
- [ ] 기여 가이드
  - 개발 환경 설정
  - 코딩 스타일
  - PR 프로세스

---

## PART 3: 프레임워크 버전 구현 (Phase 24-26)

### Phase 24: LangChain 버전 구현

#### 24.1 프로젝트 구조 및 설정
- [ ] LangChain 버전 디렉토리 구조 생성
- [ ] 의존성 추가
  ```toml
  langchain = "^0.1.0"
  langchain-anthropic = "^0.1.0"
  langchain-community = "^0.0.20"
  ```
- [ ] 공통 모듈 재사용 설정

#### 24.2 Document Loader 및 인덱싱
- [ ] API Spec Document Loader
  - Custom DocumentLoader 구현
  - OpenAPI spec을 Document로 변환
- [ ] Text Splitter
  - RecursiveCharacterTextSplitter
  - Endpoint 단위로 분할
  - 메타데이터 유지
- [ ] Embeddings
  - OpenAIEmbeddings
  - HuggingFaceEmbeddings 옵션
- [ ] Vector Store
  - Chroma integration
  - Collection 관리
  - 메타데이터 필터링

#### 24.3 LLM 및 프롬프트
- [ ] ChatAnthropic 설정
  - API 키 설정
  - 모델 선택 (claude-3-sonnet)
  - 파라미터 튜닝
- [ ] PromptTemplate
  - 매칭 프롬프트
  - 검증 프롬프트
  - Curl 생성 프롬프트
- [ ] FewShotPromptTemplate
  - 예제 관리
  - ExampleSelector
  - 동적 예제 선택

#### 24.4 Retriever 및 Chain
- [ ] VectorStore Retriever
  - similarity_search
  - MMR retriever
  - Top-k 설정
- [ ] Custom Chain 구현
  - Log Parser Chain
  - API Matcher Chain
  - Validator Chain
  - Curl Generator Chain
- [ ] Sequential Chain
  - 체인 연결
  - 중간 결과 전달
- [ ] RetrievalQA 또는 ConversationalRetrievalChain
  - RAG 파이프라인
  - 컨텍스트 관리

#### 24.5 Memory 및 피드백 루프
- [ ] ConversationBufferMemory
  - 대화 히스토리 유지
- [ ] ConversationSummaryMemory (선택사항)
  - 긴 대화 요약
- [ ] 피드백 루프 구현
  - 사용자 피드백 수집
  - Memory에 반영
  - 재검색

#### 24.6 Agent (선택사항)
- [ ] Custom Tools 정의
  - LogParserTool
  - SpecSearchTool
  - ValidatorTool
- [ ] Agent 구현
  - ReAct Agent
  - Tool 실행 로직
  - Agent Executor

#### 24.7 캐싱 및 최적화
- [ ] LangChain Cache
  - InMemoryCache
  - SQLiteCache
- [ ] CacheBackedEmbeddings
  - 임베딩 재계산 방지
- [ ] Streaming
  - StreamingStdOutCallbackHandler
  - 실시간 응답 출력

#### 24.8 CLI 및 통합
- [ ] LangChain 버전 CLI
  - 별도 entry point
  - Legacy와 동일한 인터페이스
- [ ] 설정 관리
  - LangChain 특화 설정
- [ ] 테스트
  - LangChain 버전 테스트

---

### Phase 25: LlamaIndex 버전 구현

#### 25.1 프로젝트 구조 및 설정
- [ ] LlamaIndex 버전 디렉토리 구조
- [ ] 의존성 추가
  ```toml
  llama-index = "^0.9.0"
  llama-index-llms-anthropic = "^0.1.0"
  llama-index-vector-stores-chroma = "^0.1.0"
  ```

#### 25.2 Document 및 인덱싱
- [ ] Document 생성
  - OpenAPI spec을 Document로 변환
  - 메타데이터 첨부
- [ ] SimpleDirectoryReader 커스터마이징
  - API spec 파일 읽기
- [ ] Node Parser
  - SentenceSplitter
  - Endpoint 단위 분할
  - 메타데이터 유지
- [ ] Embeddings
  - OpenAIEmbedding
  - HuggingFaceEmbedding

#### 25.3 Vector Store 및 Index
- [ ] ChromaVectorStore 설정
  - Collection 관리
- [ ] VectorStoreIndex
  - 인덱스 생성
  - 인덱스 저장 및 로드
- [ ] Storage Context
  - 영구 저장

#### 25.4 LLM 및 프롬프트
- [ ] Anthropic LLM 설정
  - API 키
  - 모델 선택
- [ ] Prompts
  - 커스텀 프롬프트 템플릿
  - QA prompt
  - Refine prompt
- [ ] Settings (글로벌 설정)
  - LLM 설정
  - Embedding 설정
  - Chunk size

#### 25.5 Query Engine 및 Retriever
- [ ] VectorStoreIndex Query Engine
  - as_query_engine()
  - 파라미터 설정
- [ ] Custom Retriever
  - VectorIndexRetriever
  - Top-k 설정
  - 메타데이터 필터
- [ ] Query Engine with Retriever
  - RetrieverQueryEngine
  - Response Synthesizer

#### 25.6 Chat Engine 및 Memory
- [ ] ChatMemoryBuffer
  - 대화 히스토리
  - Token limit
- [ ] CondenseQuestionChatEngine
  - 대화형 쿼리 개선
- [ ] SimpleChatEngine (선택사항)

#### 25.7 Agent (선택사항)
- [ ] Query Engine Tools
  - QueryEngineTool 정의
- [ ] ReActAgent
  - Tool 실행
  - 추론 과정

#### 25.8 Post-processing
- [ ] Response 후처리
  - 결과 파싱
  - 신뢰도 추출
- [ ] Node Postprocessor
  - SimilarityPostprocessor
  - KeywordNodePostprocessor

#### 25.9 CLI 및 통합
- [ ] LlamaIndex 버전 CLI
  - 별도 entry point
  - Legacy와 동일한 인터페이스
- [ ] 설정 관리
- [ ] 테스트

---

### Phase 26: 비교 및 벤치마크

#### 26.1 벤치마크 환경 구축
- [ ] 테스트 데이터셋 준비
  - 다양한 로그 샘플 (50개 이상)
  - 여러 API spec (5개 이상)
  - Ground truth 라벨링
- [ ] 벤치마크 스크립트
  - 3가지 버전 자동 실행
  - 동일한 입력 데이터 사용
  - 결과 수집

#### 26.2 정확도 측정
- [ ] 매칭 정확도
  - Precision, Recall, F1
  - 올바른 API spec 매칭률
- [ ] 정합성 검사 정확도
  - True Positive / False Positive
- [ ] Curl 생성 정확도
  - 실행 가능성 테스트
  - 정확성 검증
- [ ] 결과 비교표 생성

#### 26.3 성능 측정
- [ ] 처리 속도
  - 로그 파싱 시간
  - 벡터 검색 시간
  - LLM 호출 시간
  - 전체 처리 시간
- [ ] 메모리 사용량
  - memory_profiler
  - 피크 메모리
  - 평균 메모리
- [ ] API 호출 횟수
  - LLM API 호출
  - Embeddings API 호출
- [ ] 캐시 히트율
- [ ] 성능 그래프 생성

#### 26.4 비용 분석
- [ ] LLM API 비용
  - Token 사용량
  - 예상 비용 계산
- [ ] Embeddings API 비용
- [ ] 총 비용 비교
- [ ] 비용 효율성 분석

#### 26.5 기능 비교
- [ ] 기능 비교표 작성
  | 기능 | Legacy | LangChain | LlamaIndex |
  |------|--------|-----------|------------|
  | 로그 파싱 | ✓ | ✓ | ✓ |
  | 벡터 검색 | ✓ | ✓ | ✓ |
  | RAG 파이프라인 | Manual | Chain | QueryEngine |
  | Memory 관리 | Custom | Built-in | Built-in |
  | 캐싱 | Custom | Built-in | Built-in |
  | Agent 지원 | X | ✓ | ✓ |
  | 확장성 | High | High | Medium |
  | 학습 곡선 | Low | Medium | Medium |
  | 커스터마이징 | Easy | Medium | Medium |

#### 26.6 코드 복잡도 분석
- [ ] 라인 수 비교
- [ ] 순환 복잡도 (radon)
- [ ] 유지보수성 지표
- [ ] 코드 가독성

#### 26.7 장단점 분석
- [ ] Legacy 버전
  - 장점: 완전한 제어, 커스터마이징 용이, 의존성 최소
  - 단점: 보일러플레이트 많음, 직접 구현 필요
- [ ] LangChain 버전
  - 장점: 풍부한 기능, 활발한 커뮤니티, 체인 구성 편리
  - 단점: 복잡한 추상화, 오버헤드, 버전 변경 빈번
- [ ] LlamaIndex 버전
  - 장점: RAG에 최적화, 간단한 인덱싱, 빠른 프로토타이핑
  - 단점: 유연성 낮음, 커스터마이징 제한적

#### 26.8 사용 시나리오별 추천
- [ ] 추천 가이드 작성
  - **프로토타입/POC**: LlamaIndex
  - **프로덕션/엔터프라이즈**: Legacy (높은 제어 필요 시)
  - **복잡한 워크플로우**: LangChain
  - **학습 목적**: Legacy → LangChain/LlamaIndex 순서
  - **빠른 개발**: LlamaIndex 또는 LangChain
  - **커스터마이징 중요**: Legacy

#### 26.9 최종 보고서
- [ ] 종합 보고서 작성
  - Executive Summary
  - 벤치마크 결과
  - 기능 비교
  - 장단점 분석
  - 추천 사항
- [ ] 시각화
  - 성능 그래프
  - 비용 차트
  - 비교표
- [ ] 발표 자료 (선택사항)

---

## 기술적 고려사항

### Legacy 구현 핵심 포인트
- **완전한 제어**: 모든 컴포넌트를 직접 구현하여 내부 동작 이해
- **최소 의존성**: 핵심 라이브러리만 사용 (anthropic, chromadb)
- **명확한 인터페이스**: 각 모듈 간 명확한 계약
- **테스트 용이성**: 모든 컴포넌트 단위 테스트 가능
- **성능 최적화**: 필요에 따라 세밀한 튜닝

### LangChain 활용 포인트
- **체인 활용**: 복잡한 로직을 Chain으로 구성
- **Memory 활용**: 대화 히스토리 자동 관리
- **Callbacks**: 로깅, 모니터링, 스트리밍
- **통합 생태계**: 다양한 LLM, Vector Store, Tool 쉽게 교체

### LlamaIndex 활용 포인트
- **인덱싱 특화**: API spec 인덱싱에 최적
- **QueryEngine**: 간단한 RAG 파이프라인
- **메타데이터 필터**: 효율적인 검색
- **Storage Context**: 영구 저장 및 로드 간편

### 공통 고려사항
- **API Spec 처리**: 모든 버전에서 동일한 파싱 로직 공유
- **테스트 데이터**: 동일한 테스트 셋으로 공정한 비교
- **에러 처리**: 각 버전에서 일관된 에러 처리
- **설정 관리**: 버전별 설정 파일 분리

---

## 데이터 플로우

### Legacy Version
```
[텍스트/로그 입력]
       ↓
[로그 파서 (직접 구현)]
       ↓
[임베딩 생성 (OpenAI/HF)]
       ↓
[ChromaDB 벡터 검색 (직접 연동)]
       ↓
[Claude API 직접 호출]
       ↓
[프롬프트 직접 구성]
       ↓
[응답 파싱 (직접 구현)]
       ↓
[정합성 검사 (jsonschema)]
       ↓
[Curl 생성 (직접 구현)]
       ↓
[캐시 저장 (diskcache)]
       ↓
[사용자 피드백] → 재검색
       ↓
[완료]
```

### LangChain Version
```
[텍스트/로그 입력]
       ↓
[Document Loader]
       ↓
[Text Splitter]
       ↓
[Embeddings (OpenAI/HF)]
       ↓
[Chroma Vector Store]
       ↓
[VectorStore Retriever]
       ↓
[RetrievalQA Chain]
  - ChatAnthropic
  - PromptTemplate
  - ConversationMemory
       ↓
[Custom Chains (Sequential)]
  - Validator Chain
  - Curl Generator Chain
       ↓
[LangChain Cache]
       ↓
[사용자 피드백] → Memory 업데이트
       ↓
[완료]
```

### LlamaIndex Version
```
[텍스트/로그 입력]
       ↓
[Document 생성]
       ↓
[Node Parser]
       ↓
[Embeddings]
       ↓
[VectorStoreIndex]
       ↓
[Query Engine]
  - Anthropic LLM
  - Custom Prompts
  - ChatMemoryBuffer
       ↓
[Response Post-processing]
       ↓
[Custom 검증 및 Curl 생성]
       ↓
[사용자 피드백] → 재쿼리
       ↓
[완료]
```

---

## 성공 기준

### Legacy 구현 (Phase 1-23)
- [ ] 모든 핵심 기능 완벽 동작
- [ ] 5가지 이상 로그 형식 지원
- [ ] API spec 매칭 정확도 85% 이상
- [ ] Curl 실행 가능성 95% 이상
- [ ] 평균 응답 시간 3초 이내
- [ ] 테스트 커버리지 80% 이상
- [ ] 완전한 문서화

### LangChain 구현 (Phase 24)
- [ ] Legacy와 동일한 기능 제공
- [ ] LangChain 패턴 올바르게 활용
- [ ] Memory 및 Chain 정상 작동
- [ ] Legacy 대비 코드 간결성 확보

### LlamaIndex 구현 (Phase 25)
- [ ] Legacy와 동일한 기능 제공
- [ ] QueryEngine 올바르게 활용
- [ ] 인덱싱 최적화
- [ ] Legacy 대비 빠른 인덱싱

### 비교 및 벤치마크 (Phase 26)
- [ ] 50개 이상 테스트 케이스
- [ ] 정확도, 성능, 비용 모두 측정
- [ ] 상세한 분석 보고서
- [ ] 명확한 추천 가이드

---

## 위험 요소 및 대응

### Legacy 구현 위험
- **개발 시간**: 모든 것을 직접 구현 → 충분한 시간 확보
- **버그**: 직접 구현으로 버그 가능성 → 철저한 테스트
- **유지보수**: 프레임워크 없이 관리 → 명확한 문서화

### 프레임워크 버전 위험
- **버전 호환성**: LangChain/LlamaIndex 버전 변경 빈번 → 버전 고정
- **추상화 오버헤드**: 성능 저하 가능성 → 벤치마크로 측정
- **학습 곡선**: 프레임워크 학습 필요 → 공식 문서 활용

### 비교 공정성
- **테스트 편향**: 불공정한 비교 → 동일한 조건 보장
- **구현 품질**: 프레임워크 미숙으로 성능 저하 → 충분한 학습

---

## 다음 단계

### 즉시 시작
1. **Phase 1-2**: 프로젝트 구조 및 API Spec 로더
2. **Phase 3-4**: 임베딩, 벡터 스토어, 로그 파서
3. **Phase 5-6**: Claude API 연동 및 매칭 엔진

### 1차 마일스톤
- Phase 1-10 완료 (기본 기능 동작)
- 간단한 로그 분석 가능
- 기본 테스트 통과

### 2차 마일스톤
- Phase 11-17 완료 (안정화 및 최적화)
- 프로덕션 수준의 안정성
- 종합 테스트 통과

### 3차 마일스톤
- Phase 18-23 완료 (고급 기능 및 문서화)
- Legacy 버전 완성

### 4차 마일스톤
- Phase 24-25 완료 (프레임워크 버전)
- 3가지 버전 모두 동작

### 최종 완료
- Phase 26 완료 (비교 및 벤치마크)
- 최종 보고서 발표

---

## 우선순위 가이드

### Critical (즉시 시작)
- Phase 1-10: 핵심 기능 구현

### High (Legacy 안정화)
- Phase 11-13: 에러 처리, 캐싱, 보안
- Phase 21-23: 테스트, CI/CD, 문서

### Medium (확장 기능)
- Phase 14-17: 배치 처리, 모니터링, 버전 관리
- Phase 18-20: 커스터마이징, 프롬프트 최적화, 사용성

### Low (프레임워크 비교)
- Phase 24-26: LangChain, LlamaIndex, 벤치마크
  (Legacy 완성 후 진행)
