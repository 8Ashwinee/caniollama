from compat_check.models import CaseOutcome
from compat_check.suite.cases import CASES
from compat_check.suite.scoring import score_response

BASIC_CASE = next(c for c in CASES if c.case_id == "single_tool_basic")
CONTROL_CASE = next(c for c in CASES if c.case_id == "no_tools_needed_control")


def test_structured_tool_call_scores_pass():
    response = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": "get_weather", "arguments": {"city": "Tokyo"}}}
            ],
        }
    }
    assert score_response(BASIC_CASE, response) == CaseOutcome.STRUCTURED_PASS


def test_json_in_content_scores_fallback():
    response = {
        "message": {
            "role": "assistant",
            "content": '{"name": "get_weather", "arguments": {"city": "Tokyo"}}',
        }
    }
    assert score_response(BASIC_CASE, response) == CaseOutcome.JSON_IN_CONTENT_FALLBACK


def test_plain_text_with_no_tool_call_scores_error():
    response = {"message": {"role": "assistant", "content": ""}}
    assert score_response(BASIC_CASE, response) == CaseOutcome.TIMEOUT_OR_ERROR


def test_plain_prose_answer_scores_fallback_bucket():
    response = {"message": {"role": "assistant", "content": "It's sunny in Tokyo today."}}
    assert score_response(BASIC_CASE, response) == CaseOutcome.JSON_IN_CONTENT_FALLBACK


def test_control_case_correctly_skips_tool_call():
    response = {"message": {"role": "assistant", "content": "Bonjour !"}}
    assert score_response(CONTROL_CASE, response) == CaseOutcome.STRUCTURED_PASS


def test_control_case_still_passes_if_model_calls_tool_anyway():
    response = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "get_weather", "arguments": {"city": "?"}}}],
        }
    }
    assert score_response(CONTROL_CASE, response) == CaseOutcome.STRUCTURED_PASS
