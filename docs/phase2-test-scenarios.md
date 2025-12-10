# Phase 2: API Spec Document Loader - 테스트 시나리오

## 개요

Phase 2는 OpenAPI/Swagger spec 파일을 로드하고 파싱하여 Document로 변환하는 기능을 구현합니다.

## 테스트 환경

- **테스트 파일**: `tests/legacy/test_spec_loader_simple.py`
- **샘플 데이터**: `data/specs/sample_users_api.yaml`
- **실행 방법**: `poetry run python3 tests/legacy/test_spec_loader_simple.py`

## 테스트 시나리오

### 테스트 1: YAML 파일 로드

**목적**: OpenAPI spec YAML 파일을 읽고 기본 정보를 추출하는 기능 검증

**입력**:
- 파일 경로: `data/specs/sample_users_api.yaml`
- OpenAPI 3.0.0 형식의 Users API spec

**실행 단계**:
1. `OpenAPISpecLoader` 인스턴스 생성 (validate=False)
2. `load_from_file()` 메서드로 YAML 파일 로드
3. 반환된 `APISpec` 객체 검증

**기대 결과**:
- ✅ APISpec 객체가 정상적으로 생성됨
- ✅ title = "Users API"
- ✅ version = "1.0.0"
- ✅ openapi_version = "3.0.0"
- ✅ base_url = "https://api.example.com/v1"
- ✅ endpoints = 5개

**검증 항목**:
```python
assert isinstance(spec, APISpec)
assert spec.title == "Users API"
assert spec.version == "1.0.0"
assert spec.openapi_version == "3.0.0"
assert spec.base_url == "https://api.example.com/v1"
assert len(spec.endpoints) == 5
```

---

### 테스트 2: Endpoint 추출

**목적**: API spec에서 모든 endpoint를 정확히 추출하는지 검증

**입력**:
- 로드된 APISpec 객체
- 5개의 endpoint (GET /users, POST /users, GET /users/{userId}, PUT /users/{userId}, DELETE /users/{userId})

**실행 단계**:
1. APISpec 객체에서 endpoints 목록 확인
2. 특정 endpoint 조회 (`get_endpoint("GET", "/users")`)
3. endpoint의 속성 검증

**기대 결과**:
- ✅ 전체 endpoint 개수 = 5
- ✅ GET /users endpoint가 존재
- ✅ summary = "List all users"
- ✅ tags = ['users']

**검증 항목**:
```python
assert len(spec.endpoints) == 5
get_users = spec.get_endpoint("GET", "/users")
assert get_users is not None
assert get_users.summary == "List all users"
assert "users" in get_users.tags
```

**추출된 Endpoints**:
1. GET /users - List all users
2. POST /users - Create a new user
3. GET /users/{userId} - Get user by ID
4. PUT /users/{userId} - Update user
5. DELETE /users/{userId} - Delete user

---

### 테스트 3: Parameters 추출

**목적**: API endpoint의 query, path 파라미터를 정확히 추출하는지 검증

**입력**:
- GET /users endpoint (2개의 query 파라미터 포함)

**실행 단계**:
1. GET /users endpoint의 parameters 목록 조회
2. 각 파라미터의 속성 확인

**기대 결과**:
- ✅ 파라미터 개수 = 2
- ✅ limit (query): required=False
- ✅ offset (query): required=False

**검증 항목**:
```python
assert len(get_users.parameters) == 2

# limit 파라미터
- name: "limit"
- location: QUERY
- required: False
- description: "Maximum number of users to return"
- schema: {type: integer, minimum: 1, maximum: 100, default: 20}

# offset 파라미터
- name: "offset"
- location: QUERY
- required: False
- description: "Number of users to skip"
- schema: {type: integer, minimum: 0, default: 0}
```

---

### 테스트 4: Document 변환

**목적**: APISpec을 DocumentCollection으로 정확히 변환하는지 검증

**입력**:
- 로드된 APISpec 객체

**실행 단계**:
1. `SpecToDocumentConverter` 인스턴스 생성
2. `convert()` 메서드로 APISpec을 DocumentCollection으로 변환
3. 변환된 컬렉션 검증

**기대 결과**:
- ✅ DocumentCollection 객체 생성 성공
- ✅ Collection name = "Users API"
- ✅ Document 개수 = 5 (각 endpoint당 1개)
- ✅ 첫 번째 Document ID = "get_users"
- ✅ 메타데이터 포함: method, path

**검증 항목**:
```python
assert isinstance(collection, DocumentCollection)
assert collection.name == "Users API"
assert collection.count() == 5

# 첫 번째 document 검증
doc = collection.documents[0]
assert doc.id == "get_users"
assert doc.metadata.get('method') == "GET"
assert doc.metadata.get('path') == "/users"
assert len(doc.content) > 0
```

**Document 구조**:
```python
{
    "id": "get_users",
    "content": "GET /users\nSummary: List all users\n...",
    "metadata": {
        "source": "api_spec",
        "type": "endpoint",
        "method": "GET",
        "path": "/users",
        "tags": ["users"],
        "summary": "List all users",
        "description": "Retrieve a list of all users with optional filtering",
        "api_title": "Users API",
        "api_version": "1.0.0",
        "operation_id": "listUsers",
        "deprecated": False
    }
}
```

---

### 테스트 5: Document 텍스트 표현

**목적**: Document의 content가 검색에 적합한 형태로 생성되는지 검증

**입력**:
- 변환된 DocumentCollection
- GET /users document

**실행 단계**:
1. DocumentCollection에서 GET /users document 검색
2. content 필드의 텍스트 구조 검증
3. 주요 정보 포함 여부 확인

**기대 결과**:
- ✅ "GET /users" 문자열 포함
- ✅ "List all users" (summary) 포함
- ✅ Parameters 정보 포함

**검증 항목**:
```python
assert "GET /users" in get_users_doc.content
assert "List all users" in get_users_doc.content
```

**텍스트 표현 예시**:
```
GET /users
Summary: List all users
Description: Retrieve a list of all users with optional filtering
Tags: users
Parameters: limit (query): Maximum number of users to return; offset (query): Number of users to skip
```

---

## 테스트 실행 결과

### 성공 케이스

```
============================================================
Phase 2: Spec Loader 검증 테스트
============================================================
테스트 1: YAML 파일 로드
  ✓ Title: Users API
  ✓ Version: 1.0.0
  ✓ OpenAPI: 3.0.0
  ✓ Base URL: https://api.example.com/v1
  ✓ Endpoints: 5개

테스트 2: Endpoint 추출
  ✓ 전체 Endpoint 개수: 5
  ✓ GET /users: List all users
  ✓ Tags: ['users']

테스트 3: Parameters 추출
  ✓ limit (query): required=False
  ✓ offset (query): required=False

테스트 4: Document 변환
  ✓ Collection name: Users API
  ✓ Document 개수: 5
  ✓ 첫 번째 Document ID: get_users
  ✓ Method: GET
  ✓ Path: /users
  ✓ Content 길이: 214자

테스트 5: Document 텍스트 표현
  ✓ GET /users Document content:
  GET /users
  Summary: List all users
  Description: Retrieve a list of all users with optional filtering
  Tags: users
  Parameters: limit (query): Maximum number of users to return; offset (query): Number of users to skip

============================================================
결과: 5개 성공, 0개 실패
============================================================
```

---

## 테스트 커버리지

### 검증된 기능

1. **파일 로딩**
   - ✅ YAML 파일 읽기
   - ✅ OpenAPI 3.0 파싱
   - ✅ 기본 정보 추출 (title, version, description)
   - ✅ Base URL 추출

2. **Endpoint 파싱**
   - ✅ 모든 HTTP 메서드 지원 (GET, POST, PUT, DELETE)
   - ✅ Path 파라미터 인식 (/users/{userId})
   - ✅ Operation ID 추출
   - ✅ Summary 및 Description 추출
   - ✅ Tags 추출

3. **Parameters 처리**
   - ✅ Query 파라미터 추출
   - ✅ Path 파라미터 추출
   - ✅ Required 플래그 처리
   - ✅ Schema 정보 보존

4. **Document 변환**
   - ✅ APISpec → DocumentCollection 변환
   - ✅ APIEndpoint → Document 변환
   - ✅ 고유 ID 생성 (method_path 형식)
   - ✅ 메타데이터 매핑
   - ✅ 검색 최적화된 텍스트 표현 생성

### 미검증 영역 (향후 추가 필요)

- ⏳ JSON 형식 spec 파일
- ⏳ Swagger 2.x 형식
- ⏳ Request Body 상세 검증
- ⏳ Response 상세 검증
- ⏳ $ref 참조 처리
- ⏳ Security 정의 처리
- ⏳ 에러 케이스 (잘못된 파일, 형식 오류 등)

---

## 다음 단계

Phase 2 완료 후 다음 단계:
- Phase 3: Embeddings and Vector Store
- Phase 4: LLM Integration
- Phase 5: Log Parsing and API Call Extraction
- Phase 6: API Call Validation
- Phase 7: Curl Command Generation
