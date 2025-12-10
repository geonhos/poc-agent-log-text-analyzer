"""
Phase 5: LLM 통합 테스트
"""

import sys
from pathlib import Path

# src 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_ollama_connection():
    """Ollama 서버 연결 테스트"""
    print("테스트 1: Ollama 서버 연결")

    from legacy.llm import OllamaLLM

    llm = OllamaLLM()

    # 연결 확인
    connected = llm.check_connection()
    assert connected, "Ollama 서버에 연결할 수 없습니다. 'ollama serve' 실행 확인 필요"

    print(f"  ✓ Ollama 서버 연결 성공: {llm.base_url}")

    # 모델 목록 조회
    models = llm.list_models()
    assert len(models) > 0, "사용 가능한 모델이 없습니다"

    print(f"  ✓ 사용 가능한 모델: {', '.join(models)}")

    return True


def test_ollama_generate():
    """Ollama 텍스트 생성 테스트"""
    print("\n테스트 2: Ollama 텍스트 생성")

    from legacy.llm import OllamaLLM

    llm = OllamaLLM(model="llama2:7b-chat-q4_0")

    # 간단한 텍스트 생성
    prompt = "What is 2+2? Answer with only the number."
    response = llm.generate(prompt=prompt, temperature=0.1, max_tokens=10)

    assert response.content, "응답 내용이 비어있습니다"
    assert response.model == "llama2:7b-chat-q4_0"
    assert response.usage is not None

    print(f"  ✓ 텍스트 생성 성공")
    print(f"    프롬프트: {prompt}")
    print(f"    응답: {response.content[:100]}")
    print(f"    토큰 사용: {response.usage}")

    return True


def test_ollama_chat():
    """Ollama 채팅 테스트"""
    print("\n테스트 3: Ollama 채팅")

    from legacy.llm import OllamaLLM

    llm = OllamaLLM()

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Answer briefly."},
        {"role": "user", "content": "What is an API?"},
    ]

    response = llm.chat(messages=messages, temperature=0.3, max_tokens=100)

    assert response.content, "응답 내용이 비어있습니다"

    print(f"  ✓ 채팅 성공")
    print(f"    응답: {response.content[:150]}...")

    return True


def test_prompt_template():
    """프롬프트 템플릿 테스트"""
    print("\n테스트 4: 프롬프트 템플릿")

    from legacy.llm import PromptTemplate

    # 기본 템플릿
    template = PromptTemplate("Hello, ${name}! You are ${age} years old.")
    result = template.format(name="Alice", age=25)

    assert "Alice" in result
    assert "25" in result
    print(f"  ✓ 기본 템플릿 렌더링 성공")

    # Few-shot 템플릿
    template = PromptTemplate(
        "Solve the problem:\n\n${examples}\n\nProblem: ${problem}",
        few_shot_examples=[
            {"input": "2+2", "output": "4"},
            {"input": "3+5", "output": "8"},
        ],
    )

    result = template.format(problem="10+5")
    assert "Example 1:" in result
    assert "2+2" in result
    assert "10+5" in result
    print(f"  ✓ Few-shot 템플릿 렌더링 성공")

    return True


def test_llm_log_analyzer_agent():
    """LLM LogAnalyzerAgent 테스트"""
    print("\n테스트 5: LLM LogAnalyzerAgent")

    from legacy.agents import LLMLogAnalyzerAgent

    agent = LLMLogAnalyzerAgent(model="llama2:7b-chat-q4_0")

    # 구조화되지 않은 로그 텍스트
    log_text = """
    The user made a GET request to /api/users endpoint and received a 200 response.
    Then they sent a POST to /api/posts with some data and got 201 created status.
    """

    print(f"  입력 로그:")
    print(f"    {log_text.strip()[:100]}...")
    print(f"  LLM 분석 중... (시간이 걸릴 수 있습니다)")

    result = agent.execute(log_text, context={"temperature": 0.1, "max_tokens": 1000})

    assert result["llm_used"], "LLM이 사용되지 않았습니다"
    assert result["total_count"] >= 0, "API 호출 개수가 음수입니다"

    print(f"  ✓ LLM 분석 완료")
    print(f"    추출된 API 호출: {result['total_count']}개")

    if result["total_count"] > 0:
        for idx, call in enumerate(result["api_calls"][:3], 1):
            print(f"    {idx}. {call.method.value} {call.path}")

    # 요약 출력
    summary = agent.get_summary(result)
    assert "LLM 로그 분석" in summary
    print(f"  ✓ 요약 생성 성공")

    return True


def test_predefined_prompts():
    """사전 정의된 프롬프트 테스트"""
    print("\n테스트 6: 사전 정의된 프롬프트")

    from legacy.llm.prompt_template import LogAnalysisPrompts

    # EXTRACT_API_CALLS 템플릿
    prompt = LogAnalysisPrompts.EXTRACT_API_CALLS.format(
        log_text='{"method": "GET", "path": "/users"}'
    )

    assert "extract" in prompt.lower() or "analyze" in prompt.lower()
    assert "/users" in prompt
    print(f"  ✓ EXTRACT_API_CALLS 템플릿 렌더링 성공")

    # ENHANCE_API_CALL 템플릿
    prompt = LogAnalysisPrompts.ENHANCE_API_CALL.format(
        method="POST", path="/api/users", additional_info="Body: {name: 'John'}"
    )

    assert "POST" in prompt
    assert "/api/users" in prompt
    print(f"  ✓ ENHANCE_API_CALL 템플릿 렌더링 성공")

    return True


def test_llm_with_complex_log():
    """복잡한 로그에 대한 LLM 분석 테스트"""
    print("\n테스트 7: 복잡한 로그 LLM 분석")

    from legacy.agents import LLMLogAnalyzerAgent

    agent = LLMLogAnalyzerAgent()

    # 복잡한 자연어 로그
    complex_log = """
    [2024-01-01 10:00:00] Application started
    [2024-01-01 10:00:05] User 'john@example.com' authenticated successfully
    [2024-01-01 10:00:10] Fetching user profile from GET /api/v1/users/123
    [2024-01-01 10:00:15] Response received: 200 OK
    [2024-01-01 10:00:20] User updated their name via PUT request to /api/v1/users/123
    [2024-01-01 10:00:25] Update successful: 204 No Content
    [2024-01-01 10:00:30] User logged out
    """

    print(f"  복잡한 로그 분석 중... (시간이 걸릴 수 있습니다)")

    result = agent.execute(complex_log, context={"temperature": 0.2})

    print(f"  ✓ 분석 완료: {result['total_count']}개 API 호출 발견")

    if result["total_count"] > 0:
        print(f"  발견된 API 호출:")
        for call in result["api_calls"]:
            status = f" (status: {call.status_code})" if call.status_code else ""
            print(f"    - {call.method.value} {call.path}{status}")

    return True


def test_llm_error_handling():
    """LLM 에러 핸들링 테스트"""
    print("\n테스트 8: LLM 에러 핸들링")

    from legacy.agents import AgentError, LLMLogAnalyzerAgent

    # 존재하지 않는 모델로 초기화
    agent = LLMLogAnalyzerAgent(model="nonexistent-model:latest")

    try:
        # 분석 시도
        agent.execute("GET /test", context={"max_tokens": 10})
        assert False, "존재하지 않는 모델로 에러가 발생해야 함"
    except AgentError as e:
        print(f"  ✓ 에러 핸들링 성공: {str(e)[:80]}...")

    return True


def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Phase 5: LLM 통합 테스트")
    print("=" * 60)
    print("\n⚠️  주의: 이 테스트는 Ollama 서버가 실행 중이어야 합니다.")
    print("   'ollama serve' 명령으로 서버를 시작하세요.\n")

    tests = [
        test_ollama_connection,
        test_ollama_generate,
        test_ollama_chat,
        test_prompt_template,
        test_llm_log_analyzer_agent,
        test_predefined_prompts,
        test_llm_with_complex_log,
        test_llm_error_handling,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except AssertionError as e:
            error_msg = str(e)
            if "연결할 수 없습니다" in error_msg:
                print(f"\n⚠️  테스트 스킵: Ollama 서버가 실행 중이 아닙니다")
                skipped += 1
                break  # Ollama 연결 실패 시 나머지 테스트 스킵
            else:
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
    print(f"결과: {passed}개 성공, {failed}개 실패, {skipped}개 스킵")
    print("=" * 60)

    if skipped > 0:
        print("\n⚠️  일부 테스트가 스킵되었습니다.")
        print("   Ollama 서버를 실행하고 다시 시도하세요:")
        print("   $ ollama serve")
    elif failed == 0:
        print("\n✅ 모든 LLM 테스트 통과")

    return 0 if (failed == 0 and skipped == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
