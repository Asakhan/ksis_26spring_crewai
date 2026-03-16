import json
import time
from pathlib import Path
from datetime import datetime

from customer_inquiry_crewai.crew import CustomerInquiryCrewai
from customer_inquiry_crewai.logging_utils import log_experiment_result, log_agent_detail

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
LOG_DIR = BASE_DIR.parent.parent / "logs"

TEST_FILE = DATA_DIR / "test_scenarios.json"
LOG_FILE = LOG_DIR / "experiment_results.jsonl"

RUN_ID = datetime.now().strftime("%Y-%m-%d-%H%M%S")


def ensure_dirs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_test_scenarios():
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def append_jsonl(path: Path, row: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe_dump(task_output):
    if hasattr(task_output, "pydantic") and task_output.pydantic:
        return task_output.pydantic.model_dump()
    if hasattr(task_output, "raw"):
        return {"raw": task_output.raw}
    return {}


def evaluate_success(expected, actual):
    return (
        actual.get("intent") == expected["expected_intent"]
        and actual.get("policy_key") == expected["expected_policy_key"]
        and actual.get("answer_status") == expected["expected_answer_status"]
    )


def run_single_scenario(scenario: dict):
    crew_obj = CustomerInquiryCrewai().crew()

    inputs = {
        "customer_query": scenario["user_input"],
        "scenario_id": scenario["id"]
    }

    start = time.time()
    result = crew_obj.kickoff(inputs=inputs)
    elapsed_ms = int((time.time() - start) * 1000)

    task_outputs = getattr(crew_obj, "tasks_output", [])

    intent_result = safe_dump(task_outputs[0]) if len(task_outputs) > 0 else {}
    policy_result = safe_dump(task_outputs[1]) if len(task_outputs) > 1 else {}
    response_result = safe_dump(task_outputs[2]) if len(task_outputs) > 2 else {}

    log_task_detail(RUN_ID, "CrewAI", scenario["id"], "IntentAgent", intent_result, None)
    log_task_detail(RUN_ID, "CrewAI", scenario["id"], "PolicyAgent", policy_result, None)
    log_task_detail(RUN_ID, "CrewAI", scenario["id"], "ResponseAgent", response_result, None)

    actual = {
        "intent": intent_result.get("intent", ""),
        "policy_key": response_result.get("used_policy_key", policy_result.get("policy_key", "")),
        "answer_status": response_result.get("answer_status", ""),
        "tool_status": policy_result.get("tool_status", ""),
        "error_message": policy_result.get("error_message", "")
    }

    task_success = evaluate_success(scenario, actual)

    row = {
        "experiment_meta": {
            "run_id": RUN_ID,
            "framework": "CrewAI",
            "model": "gpt-4o-mini",
            "temperature": 0,
            "max_tokens": 512,
            "timestamp": datetime.now().isoformat()
        },
        "test_case": {
            "test_id": scenario["id"],
            "type": scenario["type"],
            "user_input": scenario["user_input"]
        },
        "execution_metrics": {
            "intent": actual["intent"],
            "policy_key": actual["policy_key"],
            "answer_status": actual["answer_status"],
            "task_success": task_success,
            "response_time_ms": elapsed_ms,
            "total_token_usage": None,
            "prompt_tokens": None,
            "completion_tokens": None,
            "tool_call_count": 1 if policy_result else 0,
            "agent_step_count": len(task_outputs)
        },
        "error_info": {
            "tool_status": actual["tool_status"],
            "error_message": actual["error_message"]
        }
    }

    log_experiment_result(row)

    append_jsonl(LOG_FILE, row)
    return row

def log_task_detail(run_id: str, framework: str, test_id: str, agent_stage: str, task_output: dict, latency_ms: int | None = None):
    log_agent_detail({
        "run_id": run_id,
        "framework": framework,
        "test_id": test_id,
        "agent_stage": agent_stage,
        "input_tokens": None,
        "output_tokens": None,
        "latency_ms": latency_ms,
        "output_json": task_output
    })