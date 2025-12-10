"""
Phase 4: 파서 테스트
"""

import sys
from pathlib import Path

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_json_parser():
    """JSON 로그 파서 테스트"""
    print("테스트 1: JSON 로그 파서")

    from common.models import HttpMethod
    from legacy.parsers import JsonLogParser

    parser = JsonLogParser()

    # 단일 JSON 객체
    json_log = '{"method": "GET", "path": "/users", "timestamp": "2024-01-01T10:00:00Z"}'

    assert parser.can_parse(json_log), "JSON 감지 실패"

    api_calls = parser.parse(json_log)
    assert len(api_calls) == 1, f"API 호출 개수가 다름: {len(api_calls)}"

    call = api_calls[0]
    assert call.method == HttpMethod.GET, f"메서드가 다름: {call.method}"
    assert call.path == "/users", f"경로가 다름: {call.path}"
    assert call.timestamp == "2024-01-01T10:00:00Z", f"타임스탬프가 다름: {call.timestamp}"

    print(f"  ✓ 단일 JSON 객체 파싱 성공")

    # JSONL (JSON Lines)
    jsonl_log = """{"method": "GET", "path": "/users/1"}
{"method": "POST", "path": "/users", "body": {"name": "John"}}
{"method": "DELETE", "path": "/users/1"}"""

    api_calls = parser.parse(jsonl_log)
    assert len(api_calls) == 3, f"JSONL 파싱 개수가 다름: {len(api_calls)}"
    assert api_calls[0].method == HttpMethod.GET
    assert api_calls[1].method == HttpMethod.POST
    assert api_calls[1].body == {"name": "John"}
    assert api_calls[2].method == HttpMethod.DELETE

    print(f"  ✓ JSONL 파싱 성공: {len(api_calls)}개 추출")

    return True


def test_text_parser():
    """Plain text 로그 파서 테스트"""
    print("\n테스트 2: Plain Text 로그 파서")

    from common.models import HttpMethod
    from legacy.parsers import TextLogParser

    parser = TextLogParser()

    # 간단한 형식
    text_log = """GET /api/users
POST /api/users with body {"name": "John"}
DELETE /api/users/123 - status: 204"""

    assert parser.can_parse(text_log), "텍스트 감지 실패"

    api_calls = parser.parse(text_log)
    assert len(api_calls) == 3, f"API 호출 개수가 다름: {len(api_calls)}"

    assert api_calls[0].method == HttpMethod.GET
    assert api_calls[0].path == "/api/users"

    assert api_calls[1].method == HttpMethod.POST
    assert api_calls[1].body == {"name": "John"}

    assert api_calls[2].method == HttpMethod.DELETE
    assert api_calls[2].status_code == 204

    print(f"  ✓ 텍스트 로그 파싱 성공: {len(api_calls)}개 추출")

    # 타임스탬프 포함 형식
    timestamped_log = "[2024-01-01 10:00:00] GET /users"
    api_calls = parser.parse(timestamped_log)
    assert len(api_calls) == 1
    assert api_calls[0].timestamp is not None
    print(f"  ✓ 타임스탬프 추출 성공: {api_calls[0].timestamp}")

    return True


def test_http_parser():
    """HTTP request 로그 파서 테스트"""
    print("\n테스트 3: HTTP Request 로그 파서")

    from common.models import HttpMethod
    from legacy.parsers import HttpRequestParser

    parser = HttpRequestParser()

    http_log = """GET /api/users HTTP/1.1
Host: api.example.com
Authorization: Bearer token123
Content-Type: application/json"""

    assert parser.can_parse(http_log), "HTTP request 감지 실패"

    api_calls = parser.parse(http_log)
    assert len(api_calls) == 1, f"API 호출 개수가 다름: {len(api_calls)}"

    call = api_calls[0]
    assert call.method == HttpMethod.GET
    assert call.path == "/api/users"
    assert call.base_url == "https://api.example.com"
    assert "Authorization" in call.headers
    assert call.headers["Authorization"] == "Bearer token123"

    print(f"  ✓ HTTP request 파싱 성공")
    print(f"    - Base URL: {call.base_url}")
    print(f"    - Headers: {len(call.headers)}개")

    # Body 포함 HTTP request
    http_with_body = """POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "John", "email": "john@example.com"}"""

    api_calls = parser.parse(http_with_body)
    assert len(api_calls) == 1
    assert api_calls[0].method == HttpMethod.POST
    assert api_calls[0].body == {"name": "John", "email": "john@example.com"}

    print(f"  ✓ HTTP request with body 파싱 성공")

    return True


def test_extractor():
    """API Call Extractor 통합 테스트"""
    print("\n테스트 4: API Call Extractor")

    from legacy.parsers import ApiCallExtractor

    extractor = ApiCallExtractor()

    # JSON 로그
    json_log = '{"method": "GET", "path": "/users"}'
    format_name = extractor.detect_format(json_log)
    assert format_name == "JsonLogParser", f"JSON 감지 실패: {format_name}"
    api_calls = extractor.extract(json_log)
    assert len(api_calls) == 1
    print(f"  ✓ JSON 자동 감지 및 파싱 성공")

    # Plain text 로그
    text_log = "GET /api/users"
    format_name = extractor.detect_format(text_log)
    assert format_name == "TextLogParser", f"텍스트 감지 실패: {format_name}"
    api_calls = extractor.extract(text_log)
    assert len(api_calls) == 1
    print(f"  ✓ 텍스트 자동 감지 및 파싱 성공")

    # HTTP request 로그
    http_log = "GET /api/users HTTP/1.1\nHost: api.example.com"
    format_name = extractor.detect_format(http_log)
    assert format_name == "HttpRequestParser", f"HTTP 감지 실패: {format_name}"
    api_calls = extractor.extract(http_log)
    assert len(api_calls) == 1
    print(f"  ✓ HTTP request 자동 감지 및 파싱 성공")

    return True


def test_sample_files():
    """샘플 로그 파일 테스트"""
    print("\n테스트 5: 샘플 로그 파일 파싱")

    from legacy.parsers import ApiCallExtractor

    extractor = ApiCallExtractor()
    data_dir = project_root / "data" / "logs"

    # JSON 로그 파일
    json_file = data_dir / "sample_json.log"
    if json_file.exists():
        api_calls = extractor.extract_from_file(str(json_file))
        print(f"  ✓ sample_json.log: {len(api_calls)}개 API 호출 추출")
        assert len(api_calls) == 5
    else:
        print(f"  ⚠ sample_json.log 파일 없음")

    # 텍스트 로그 파일
    text_file = data_dir / "sample_text.log"
    if text_file.exists():
        api_calls = extractor.extract_from_file(str(text_file))
        print(f"  ✓ sample_text.log: {len(api_calls)}개 API 호출 추출")
        assert len(api_calls) == 5
    else:
        print(f"  ⚠ sample_text.log 파일 없음")

    # HTTP 로그 파일
    http_file = data_dir / "sample_http.log"
    if http_file.exists():
        api_calls = extractor.extract_from_file(str(http_file))
        print(f"  ✓ sample_http.log: {len(api_calls)}개 API 호출 추출")
        assert len(api_calls) == 3

        # 첫 번째 호출 상세 확인
        first_call = api_calls[0]
        print(f"    - {first_call.get_summary()}")
        print(f"    - Base URL: {first_call.base_url}")
        print(f"    - Headers: {list(first_call.headers.keys())}")
    else:
        print(f"  ⚠ sample_http.log 파일 없음")

    return True


def test_api_call_model():
    """ApiCall 모델 테스트"""
    print("\n테스트 6: ApiCall 모델")

    from common.models import ApiCall, HttpMethod

    # 기본 API call
    call = ApiCall(
        method=HttpMethod.GET,
        path="/api/users/123",
        base_url="https://api.example.com",
        query_params={"page": "1", "limit": "10"},
        headers={"Authorization": "Bearer token"},
    )

    # 전체 URL 생성
    full_url = call.get_full_url()
    assert "https://api.example.com/api/users/123" in full_url
    assert "page=1" in full_url
    assert "limit=10" in full_url
    print(f"  ✓ 전체 URL 생성: {full_url}")

    # 요약 텍스트
    summary = call.get_summary()
    assert summary == "GET /api/users/123"
    print(f"  ✓ 요약 텍스트: {summary}")

    # Curl 명령어 생성
    curl = call.to_curl_command()
    assert "curl" in curl
    assert "-X GET" in curl
    assert "Authorization" in curl
    print(f"  ✓ Curl 명령어 생성 성공")

    return True


def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Phase 4: 텍스트/로그 파서 테스트")
    print("=" * 60)

    tests = [
        test_json_parser,
        test_text_parser,
        test_http_parser,
        test_extractor,
        test_sample_files,
        test_api_call_model,
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
            import traceback

            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"\n✗ 에러 발생: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"결과: {passed}개 성공, {failed}개 실패")
    print("=" * 60)

    if failed == 0:
        print("\n✅ 모든 파서 테스트 통과")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
