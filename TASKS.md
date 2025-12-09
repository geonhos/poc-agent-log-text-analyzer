# API Log Text Analyzer - Task Document

## 프로젝트 개요
텍스트 또는 로그에서 API 호출 정보를 추출하고, API spec 문서를 기반으로 요청의 정합성을 검사하며 유효한 curl 명령어를 생성하는 자동화 도구

## 주요 기능
1. **텍스트/로그 입력 처리**: 다양한 형식의 로그 및 텍스트 입력 지원
2. **API Spec 문서 검색**: 입력된 정보를 API spec 문서에서 매칭
3. **정합성 검사**: 요청 파라미터, 헤더, 바디의 유효성 검증
4. **Curl 생성**: 검증된 정보를 기반으로 실행 가능한 curl 명령어 생성
5. **피드백 루프**: 사용자 만족도 기반 재검색 및 개선

## 기술 스택
- **언어**: Python 3.9+
- **API Spec 파싱**: OpenAPI/Swagger 파서
- **LLM**: Claude API (문맥 이해 및 매칭)
- **벡터 DB**: ChromaDB (API spec 문서 검색)
- **CLI**: Click 또는 Typer

## 프로젝트 구조
```
poc-agent-log-text-analyzer/
├── src/
│   ├── parsers/          # 로그/텍스트 파서
│   ├── spec_loader/      # API spec 문서 로더
│   ├── matcher/          # API spec 매칭 엔진
│   ├── validator/        # 정합성 검사
│   ├── curl_generator/   # curl 명령어 생성
│   └── cli/             # CLI 인터페이스
├── tests/
├── docs/
└── data/                # API spec 문서 저장소
```

## 구현 태스크

### Phase 1: 프로젝트 초기 설정
- [ ] Python 프로젝트 구조 생성
- [ ] 의존성 관리 설정 (poetry/pip)
- [ ] 개발 환경 설정 (linting, formatting)
- [ ] Git 설정 및 .gitignore 업데이트
- [ ] 기본 README 작성

### Phase 2: API Spec 문서 로더
- [ ] OpenAPI/Swagger spec 파일 파서 구현
- [ ] API spec 정보 추출 로직
  - Endpoint paths
  - HTTP methods
  - Parameters (query, path, header, body)
  - Request/Response schemas
- [ ] ChromaDB 연동 및 임베딩 저장
- [ ] API spec 검색 인덱스 구축

### Phase 3: 텍스트/로그 파서
- [ ] 다양한 로그 형식 파서 구현
  - JSON 로그
  - Plain text 로그
  - HTTP request 로그
  - Application 로그
- [ ] 로그에서 API 호출 정보 추출
  - URL/Endpoint
  - HTTP method
  - Headers
  - Request body
  - Parameters
- [ ] 정규표현식 기반 패턴 매칭

### Phase 4: API Spec 매칭 엔진
- [ ] 벡터 기반 유사도 검색 구현
- [ ] Claude API 연동
  - 입력 텍스트 분석
  - API spec과의 매칭
  - 컨텍스트 기반 추론
- [ ] 매칭 결과 신뢰도 점수 계산
- [ ] 다중 후보 반환 및 순위화

### Phase 5: 정합성 검사
- [ ] Request 파라미터 검증
  - Required fields 체크
  - 데이터 타입 검증
  - Enum/제약조건 검증
- [ ] Request body 스키마 검증
- [ ] Header 검증
- [ ] 검증 실패 시 상세 에러 메시지 생성

### Phase 6: Curl 생성기
- [ ] API spec 기반 curl 템플릿 생성
- [ ] 추출된 파라미터를 curl 옵션으로 변환
  - Headers (-H)
  - Request body (-d)
  - Query parameters
  - Authentication
- [ ] curl 명령어 포맷팅 및 출력
- [ ] 실행 가능성 검증

### Phase 7: CLI 인터페이스
- [ ] CLI 프레임워크 구현
- [ ] 명령어 구조 설계
  ```
  analyzer analyze <log-file>
  analyzer load-spec <spec-file>
  analyzer interactive
  ```
- [ ] 대화형 모드 구현
- [ ] 결과 출력 포맷팅 (JSON/Table/Plain)

### Phase 8: 피드백 루프
- [ ] 사용자 만족도 입력 인터페이스
- [ ] 피드백 기반 재검색 로직
- [ ] 매칭 결과 개선 메커니즘
- [ ] 사용자 선호도 학습 (선택사항)

### Phase 9: 테스트 및 문서화
- [ ] Unit 테스트 작성
- [ ] Integration 테스트
- [ ] 샘플 API spec 및 로그 데이터 준비
- [ ] 사용자 가이드 작성
- [ ] API 문서 작성

### Phase 10: 최적화 및 배포
- [ ] 성능 최적화
- [ ] 에러 핸들링 개선
- [ ] 로깅 및 디버깅 기능
- [ ] 배포 스크립트 작성
- [ ] Docker 컨테이너화 (선택사항)

---

## 개선 및 보완 태스크

### Phase 11: 에러 처리 및 복구 전략
- [ ] 로그 파싱 실패 시 fallback 전략
  - 부분 파싱 지원
  - 수동 입력 모드로 전환
  - 다른 파서 자동 시도
- [ ] API spec 매칭 실패 처리
  - 유사도 임계값 조정 옵션
  - 수동 spec 선택 인터페이스
  - 전체 spec 목록 표시
- [ ] LLM API 오류 처리
  - Retry 로직 with exponential backoff
  - Fallback to 규칙 기반 매칭
  - 오프라인 모드 지원
- [ ] 네트워크 오류 및 타임아웃 처리
- [ ] Graceful degradation 구현

### Phase 12: 캐싱 및 성능 최적화
- [ ] LLM 응답 캐싱
  - 동일 쿼리 중복 호출 방지
  - TTL 기반 캐시 만료
  - 캐시 크기 관리
- [ ] API spec 파싱 결과 캐싱
- [ ] 벡터 검색 결과 캐싱
- [ ] 메모리 사용량 최적화
- [ ] 배치 처리 시 병렬화
- [ ] 지연 로딩 (Lazy loading) 구현

### Phase 13: 보안 및 민감정보 처리
- [ ] API 키 안전한 저장 및 관리
  - 환경 변수 사용
  - 키 암호화
  - Vault 연동 (선택사항)
- [ ] 로그 내 민감정보 마스킹
  - 토큰, 비밀번호, API 키 자동 감지
  - PII (개인식별정보) 필터링
  - 정규표현식 기반 패턴 매칭
- [ ] 생성된 curl의 민감정보 처리
  - Authorization 헤더 마스킹 옵션
  - 안전한 출력 모드
- [ ] 로그 파일 접근 권한 검증
- [ ] HTTPS 강제 사용

### Phase 14: 배치 및 대용량 처리
- [ ] 대용량 로그 파일 스트리밍 처리
  - 청크 단위 읽기
  - 메모리 효율적 파싱
- [ ] 여러 로그 파일 일괄 처리
  - 디렉토리 스캔
  - 와일드카드 패턴 지원
  - 진행률 표시
- [ ] 병렬 처리 구현
  - 멀티프로세싱/멀티스레딩
  - Worker pool 관리
- [ ] 결과 일괄 저장
  - CSV/JSON 출력
  - 데이터베이스 저장
- [ ] 재시작 가능한 처리 (체크포인트)

### Phase 15: 실시간 및 모니터링 기능
- [ ] 로그 스트림 실시간 모니터링
  - Tail -f 스타일 모니터링
  - 실시간 분석 및 알림
- [ ] 웹 대시보드 (선택사항)
  - 실시간 통계
  - 매칭 결과 시각화
- [ ] 알림 시스템
  - 특정 패턴 감지 시 알림
  - Slack/Discord 웹훅 연동
- [ ] 메트릭 수집 및 모니터링
  - Prometheus 메트릭 노출
  - 처리 시간, 성공률 추적

### Phase 16: 결과 저장 및 히스토리 관리
- [ ] 분석 결과 데이터베이스 저장
  - SQLite 로컬 저장소
  - 히스토리 조회 기능
- [ ] 세션 관리
  - 분석 세션별 결과 그룹화
  - 세션 재개 기능
- [ ] 결과 비교 기능
  - 이전 분석과 비교
  - 차이점 하이라이트
- [ ] Export 기능
  - 다양한 형식 지원 (JSON, CSV, HTML)
  - 보고서 생성

### Phase 17: API Spec 버전 및 멀티 스펙 관리
- [ ] 여러 버전의 API spec 동시 관리
  - 버전별 인덱스 분리
  - 버전 자동 감지
- [ ] API spec 업데이트 감지
  - 파일 변경 모니터링
  - 자동 재인덱싱
- [ ] 멀티 서비스 지원
  - 여러 마이크로서비스 spec 통합 관리
  - 서비스별 네임스페이스
- [ ] Spec 충돌 해결
  - 동일 endpoint 다른 spec 처리
  - 우선순위 규칙

### Phase 18: 커스터마이징 및 확장성
- [ ] 플러그인 시스템 설계
  - 커스텀 파서 플러그인
  - 커스텀 검증 규칙
  - 커스텀 출력 포맷터
- [ ] 설정 파일 시스템
  - YAML/TOML 기반 설정
  - 프로젝트별 설정
  - 글로벌 설정
- [ ] 사용자 정의 매칭 규칙
  - 정규표현식 룰
  - 우선순위 조정
- [ ] 템플릿 시스템
  - 커스텀 curl 템플릿
  - 출력 포맷 템플릿
- [ ] Hook 시스템
  - Pre/Post 처리 훅

### Phase 19: 고급 LLM 활용
- [ ] Few-shot learning 최적화
  - 예제 데이터셋 구축
  - 동적 예제 선택
- [ ] Chain-of-thought prompting
  - 단계별 추론 과정 표시
  - 신뢰도 향상
- [ ] Multi-agent 협업 (선택사항)
  - 파싱 전문 agent
  - 매칭 전문 agent
  - 검증 전문 agent
- [ ] 학습 데이터 수집 및 개선
  - 사용자 피드백 저장
  - Fine-tuning 데이터 준비
- [ ] 다른 LLM 모델 지원
  - GPT-4, Gemini 등
  - 모델 전환 기능

### Phase 20: 사용성 개선
- [ ] 대화형 튜토리얼
  - 첫 실행 시 가이드
  - 예제 워크플로우
- [ ] 자동 완성 지원
  - CLI 명령어 자동완성
  - 파일 경로 자동완성
- [ ] 컬러풀한 출력
  - 구문 강조
  - 성공/실패 색상 구분
  - 프로그레스 바
- [ ] Diff 표시
  - 원본 로그 vs 추출된 정보
  - 예상 요청 vs 실제 요청
- [ ] 복사 가능한 출력
  - 원클릭 복사 (CLI 클립보드 연동)
  - 실행 가능한 스크립트 생성

### Phase 21: 테스트 및 품질 보증
- [ ] 종합 테스트 스위트
  - 다양한 로그 형식 테스트
  - Edge case 처리 테스트
- [ ] 성능 벤치마크
  - 대용량 파일 처리 시간
  - 메모리 사용량 측정
- [ ] 정확도 테스트
  - 매칭 정확도 측정
  - False positive/negative 분석
- [ ] 부하 테스트
  - 동시 다중 요청 처리
- [ ] Mock API spec 생성기
  - 테스트용 다양한 spec 자동 생성

### Phase 22: CI/CD 및 배포
- [ ] GitHub Actions 워크플로우
  - 자동 테스트
  - 린팅 및 포맷 체크
  - 커버리지 리포트
- [ ] 자동 릴리스
  - 버전 태깅
  - Changelog 자동 생성
  - PyPI 배포
- [ ] Docker 이미지
  - Multi-stage build
  - 최소 이미지 크기 최적화
- [ ] Kubernetes 배포 (선택사항)
  - Helm 차트
  - 서비스 메시 연동

### Phase 23: 문서 및 커뮤니티
- [ ] 상세한 문서 작성
  - 설치 가이드
  - 사용 예제
  - 트러블슈팅
  - FAQ
- [ ] API 레퍼런스 자동 생성
  - Docstring 기반 문서화
  - Sphinx/MkDocs 연동
- [ ] 비디오 튜토리얼
- [ ] 블로그 포스트
- [ ] 기여 가이드
  - 코드 컨벤션
  - PR 프로세스

---

## 기술적 고려사항

### API Spec 처리
- OpenAPI 3.0/3.1 우선 지원
- Swagger 2.0 호환성
- 다중 spec 파일 관리
- GraphQL spec 지원 (선택사항)

### LLM 활용
- Claude API를 통한 자연어 이해
- Few-shot learning으로 매칭 정확도 향상
- Context window 관리
- 비용 최적화 (캐싱, 배치 처리)

### 벡터 검색
- ChromaDB를 통한 효율적인 검색
- 임베딩 모델 선택 (e.g., text-embedding-3-small)
- 하이브리드 검색 (키워드 + 벡터)
- 인덱스 최적화

### 정합성 검사
- JSON Schema 기반 검증
- OpenAPI validation library 활용
- 상세한 에러 메시지
- 자동 수정 제안

### 사용자 경험
- 명확한 출력 포맷
- 진행 상황 표시
- 컬러풀한 터미널 출력
- 에러 처리 및 복구
- 직관적인 명령어

---

## 데이터 플로우

```
[텍스트/로그 입력]
       ↓
[로그 파서] → 추출된 API 정보
       ↓
[캐시 확인] → Hit? → [캐시된 결과 반환]
       ↓ Miss
[벡터 검색] → API spec 후보 목록
       ↓
[LLM 매칭] → 최적 API spec 선택
       ↓
[정합성 검사] → 검증 결과
       ↓
[Curl 생성] → 실행 가능한 curl
       ↓
[결과 캐싱 & 저장]
       ↓
[사용자 피드백] → 만족? (No → 재검색)
       ↓
[완료]
```

---

## 성공 기준
- [ ] 다양한 로그 형식 지원 (최소 5가지)
- [ ] API spec 매칭 정확도 85% 이상
- [ ] 생성된 curl의 실행 가능성 95% 이상
- [ ] 평균 응답 시간 3초 이내 (캐시 미사용)
- [ ] 캐시 적중 시 1초 이내 응답
- [ ] 사용자 피드백 루프 정상 작동
- [ ] 대용량 파일 (100MB+) 처리 가능
- [ ] 메모리 사용량 500MB 이하
- [ ] 테스트 커버리지 80% 이상
- [ ] 문서 완성도 90% 이상

---

## 위험 요소 및 대응

### 기술적 위험
- **LLM API 비용**: 캐싱, 배치 처리로 최소화
- **매칭 정확도**: 지속적인 프롬프트 개선, Few-shot learning
- **성능 병목**: 프로파일링, 최적화, 비동기 처리
- **ChromaDB 확장성**: 인덱스 최적화, 샤딩 고려

### 운영 위험
- **API 키 관리**: 안전한 저장, 로테이션 정책
- **민감정보 노출**: 자동 마스킹, 감사 로그
- **의존성 취약점**: 정기적 업데이트, 보안 스캔

---

## 다음 단계
1. Phase 1 태스크부터 순차적으로 진행
2. 각 Phase 완료 시 테스트 및 검증
3. Phase 11-23의 개선 사항은 우선순위에 따라 진행
4. 지속적인 피드백 반영 및 개선
5. 정기적인 성능 및 정확도 측정

## 우선순위 가이드
- **High**: Phase 1-10 (핵심 기능)
- **Medium**: Phase 11-17 (안정성 및 확장성)
- **Low**: Phase 18-23 (고급 기능 및 최적화)
