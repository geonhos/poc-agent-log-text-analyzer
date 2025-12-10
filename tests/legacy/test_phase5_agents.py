"""
Phase 5: Agent 통합 테스트
"""

import json
import sys
from pathlib import Path

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_log_analyzer_agent():
    """LogAnalyzerAgent 테스트"""
    print("테스트 1: LogAnalyzerAgent")

    from legacy.agents import LogAnalyzerAgent

    agent = LogAnalyzerAgent()

    # 텍스트 입력
    log_text = """GET /api/users
POST /api/users with body {"name": "John"}
DELETE /api/users/123"""

    result = agent.execute(log_text)

    assert result["total_count"] == 3, f"API 호출 개수가 다름: {result['total_count']}"
    assert "GET" in result["formats"], "GET 메서드가 없음"
    assert "POST" in result["formats"], "POST 메서드가 없음"
    assert "DELETE" in result["formats"], "DELETE 메서드가 없음"

    print(f"  ✓ 텍스트 입력 분석 성공: {result['total_count']}개 추출")

    # 파일 입력
    sample_file = project_root / "data" / "logs" / "sample_json.log"
    if sample_file.exists():
        result = agent.execute(str(sample_file))
        assert result["total_count"] == 5, f"파일 분석 개수가 다름: {result['total_count']}"
        print(f"  ✓ 파일 입력 분석 성공: {result['total_count']}개 추출")

        # 요약 출력
        summary = agent.get_summary(result)
        assert "총 5개 API 호출 추출" in summary
        print(f"  ✓ 요약 생성 성공")

    # 리스트 입력
    log_list = [
        '{"method": "GET", "path": "/users"}',
        '{"method": "POST", "path": "/users", "body": {"name": "Jane"}}',
    ]
    result = agent.execute(log_list)
    assert result["total_count"] == 2, f"리스트 분석 개수가 다름: {result['total_count']}"
    print(f"  ✓ 리스트 입력 분석 성공: {result['total_count']}개 추출")

    return True


def test_api_call_generator_agent():
    """ApiCallGeneratorAgent 테스트"""
    print("\n테스트 2: ApiCallGeneratorAgent")

    from common.models import ApiCall, HttpMethod
    from legacy.agents import ApiCallGeneratorAgent

    agent = ApiCallGeneratorAgent()

    # 테스트용 ApiCall 생성
    api_call = ApiCall(
        method=HttpMethod.POST,
        path="/api/users",
        base_url="https://api.example.com",
        headers={"Content-Type": "application/json", "Authorization": "Bearer token123"},
        body={"name": "John", "email": "john@example.com"},
        query_params={"page": "1"},
    )

    # curl 생성
    result = agent.execute(api_call, context={"format": "curl"})
    assert result["format"] == "curl"
    assert result["count"] == 1
    assert len(result["outputs"]) == 1

    curl = result["outputs"][0]
    assert "curl" in curl
    assert "-X POST" in curl
    assert "https://api.example.com/api/users" in curl
    print(f"  ✓ curl 생성 성공")

    # HTTP dump 생성
    result = agent.execute(api_call, context={"format": "http"})
    assert result["format"] == "http"
    assert result["count"] == 1

    http_dump = result["outputs"][0]
    assert "POST" in http_dump
    assert "Content-Type: application/json" in http_dump
    print(f"  ✓ HTTP dump 생성 성공")

    # Postman collection 생성
    api_calls = [
        ApiCall(method=HttpMethod.GET, path="/users", base_url="https://api.example.com"),
        ApiCall(
            method=HttpMethod.POST,
            path="/users",
            base_url="https://api.example.com",
            body={"name": "Jane"},
        ),
    ]

    result = agent.execute(api_calls, context={"format": "postman", "name": "Test Collection"})
    assert result["format"] == "postman"
    assert result["count"] == 2

    collection = result["collection"]
    assert collection["info"]["name"] == "Test Collection"
    assert len(collection["item"]) == 2
    print(f"  ✓ Postman collection 생성 성공: {len(collection['item'])}개 item")

    # 요약 출력
    summary = agent.get_summary(result)
    assert "postman" in summary
    assert "2개" in summary
    print(f"  ✓ 요약 생성 성공")

    return True


def test_agent_workflow():
    """AgentWorkflow 테스트"""
    print("\n테스트 3: AgentWorkflow")

    from legacy.agents import ApiCallGeneratorAgent, AgentWorkflow, LogAnalyzerAgent

    # 워크플로우 생성
    workflow = AgentWorkflow(name="Test Workflow")
    workflow.add_agent(LogAnalyzerAgent())
    workflow.add_agent(ApiCallGeneratorAgent())

    # 텍스트 입력으로 실행
    log_text = """GET /api/users
POST /api/users with body {"name": "John"}"""

    result = workflow.execute(log_text, context={"format": "curl"})

    assert result["success"], "워크플로우 실행 실패"
    assert result["agents_executed"] == 2, f"Agent 실행 개수가 다름: {result['agents_executed']}"
    assert len(result["errors"]) == 0, f"에러 발생: {result['errors']}"

    # LogAnalyzerAgent 결과 확인
    analyzer_result = result["results"][0]
    assert analyzer_result["success"], "LogAnalyzerAgent 실패"
    assert analyzer_result["result"]["total_count"] == 2

    # ApiCallGeneratorAgent 결과 확인
    generator_result = result["results"][1]
    assert generator_result["success"], "ApiCallGeneratorAgent 실패"
    assert generator_result["result"]["format"] == "curl"
    assert len(generator_result["result"]["outputs"]) == 2

    print(f"  ✓ 워크플로우 실행 성공: {result['agents_executed']}개 Agent")

    # 요약 출력
    summary = workflow.get_summary()
    assert "Test Workflow" in summary
    assert "✓" in summary
    print(f"  ✓ 요약 생성 성공")

    return True


def test_predefined_workflows():
    """사전 정의된 워크플로우 테스트"""
    print("\n테스트 4: 사전 정의된 워크플로우")

    from legacy.agents.workflow import (
        create_log_to_curl_workflow,
        create_log_to_postman_workflow,
    )

    # Log to Curl 워크플로우
    workflow = create_log_to_curl_workflow()
    log_text = '{"method": "GET", "path": "/users"}'

    result = workflow.execute(log_text, context={"format": "curl"})
    assert result["success"]
    assert result["agents_executed"] == 2
    print(f"  ✓ Log to Curl 워크플로우 성공")

    # Log to Postman 워크플로우
    workflow = create_log_to_postman_workflow()
    result = workflow.execute(log_text, context={"format": "postman", "name": "My API"})
    assert result["success"]
    assert result["final_output"]["format"] == "postman"
    assert result["final_output"]["collection"]["info"]["name"] == "My API"
    print(f"  ✓ Log to Postman 워크플로우 성공")

    return True


def test_workflow_error_handling():
    """워크플로우 에러 핸들링 테스트"""
    print("\n테스트 5: 워크플로우 에러 핸들링")

    from legacy.agents import AgentWorkflow, ApiCallGeneratorAgent

    workflow = AgentWorkflow(name="Error Test")
    workflow.add_agent(ApiCallGeneratorAgent())

    # 잘못된 입력 (ApiCall 객체가 아닌 문자열)
    result = workflow.execute("invalid input", stop_on_error=False)

    assert not result["success"], "에러가 감지되지 않음"
    assert len(result["errors"]) > 0, "에러 목록이 비어있음"
    print(f"  ✓ 에러 핸들링 성공: {len(result['errors'])}개 에러 감지")

    # stop_on_error=True 테스트
    try:
        workflow.execute("invalid input", stop_on_error=True)
        assert False, "AgentError가 발생해야 함"
    except Exception as e:
        from legacy.agents import AgentError

        assert isinstance(e, AgentError)
        print(f"  ✓ stop_on_error 동작 확인")

    return True


def test_integration_with_sample_files():
    """샘플 파일과 통합 테스트"""
    print("\n테스트 6: 샘플 파일 통합 테스트")

    from legacy.agents.workflow import create_log_to_curl_workflow

    workflow = create_log_to_curl_workflow()
    sample_file = project_root / "data" / "logs" / "sample_json.log"

    if not sample_file.exists():
        print(f"  ⚠ sample_json.log 파일 없음")
        return True

    # 파일 → curl 변환
    result = workflow.execute(str(sample_file), context={"format": "curl"})

    assert result["success"], "워크플로우 실행 실패"

    # 생성된 curl 명령어 확인
    final_output = result["final_output"]
    assert final_output["format"] == "curl"
    assert final_output["count"] == 5

    curl_commands = final_output["outputs"]
    assert len(curl_commands) == 5
    assert all("curl" in cmd for cmd in curl_commands)

    print(f"  ✓ 파일 통합 테스트 성공: {len(curl_commands)}개 curl 생성")

    # 첫 번째 curl 명령어 출력
    print(f"\n  예시 curl 명령어:")
    print(f"  {curl_commands[0][:100]}...")

    return True


def test_postman_collection_export():
    """Postman collection 파일 저장 테스트"""
    print("\n테스트 7: Postman collection 파일 저장")

    from legacy.agents import ApiCallGeneratorAgent
    from legacy.agents.workflow import create_log_to_postman_workflow

    workflow = create_log_to_postman_workflow()
    sample_file = project_root / "data" / "logs" / "sample_json.log"

    if not sample_file.exists():
        print(f"  ⚠ sample_json.log 파일 없음")
        return True

    # 파일 → Postman collection 변환
    result = workflow.execute(
        str(sample_file), context={"format": "postman", "name": "Sample API Collection"}
    )

    assert result["success"]

    collection = result["final_output"]["collection"]

    # 파일로 저장
    output_file = project_root / "data" / "postman_collection.json"
    agent = ApiCallGeneratorAgent()
    agent.save_postman_collection(collection, str(output_file))

    assert output_file.exists(), "Postman collection 파일이 생성되지 않음"

    # 파일 내용 확인
    with open(output_file, "r") as f:
        saved_collection = json.load(f)

    assert saved_collection["info"]["name"] == "Sample API Collection"
    assert len(saved_collection["item"]) == 5

    print(f"  ✓ Postman collection 파일 저장 성공: {output_file}")

    # 파일 삭제
    output_file.unlink()

    return True


def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Phase 5: Agent 통합 테스트")
    print("=" * 60)

    tests = [
        test_log_analyzer_agent,
        test_api_call_generator_agent,
        test_agent_workflow,
        test_predefined_workflows,
        test_workflow_error_handling,
        test_integration_with_sample_files,
        test_postman_collection_export,
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
        print("\n✅ 모든 Agent 테스트 통과")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
