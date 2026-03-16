import json
import time
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GetPolicyToolInput(BaseModel):
    """Input schema for get_policy tool."""
    policy_key: str = Field(..., description="Policy key to retrieve, e.g. refund_policy")
    scenario_id: str = Field(default="", description="Scenario ID for experiment control, e.g. N01, A01, E01")

class GetPolicyTool(BaseTool):
    name: str = "get_policy"
    description: str = (
        "Retrieve customer service policy text from the local JSON policy database "
        "using a policy_key such as refund_policy, exchange_policy, delivery_policy, "
        "membership_policy, or cancel_policy. "
        "For experiment control, scenario_id may be provided."
    )
    args_schema: Type[BaseModel] = GetPolicyToolInput

    def _run(self, policy_key: str, scenario_id: str = "") -> str:
        start_time = time.time()

        try:
            project_root = Path(__file__).resolve().parents[4]
            policy_file = project_root / "data" / "policies.json"

            # 도구 실패 시나리오 강제 오류 주입
            error_scenarios = {"E01", "E02", "E03", "E04", "E05"}
            if scenario_id in error_scenarios:
                result = {
                    "tool_status": "error",
                    "policy_key": policy_key,
                    "policy_text": "",
                    "error_message": f"Simulated tool failure for scenario {scenario_id}"
                }
                return json.dumps(result, ensure_ascii=False)

            # 기존 강제 오류도 유지 가능
            if policy_key == "force_error_policy":
                result = {
                    "tool_status": "error",
                    "policy_key": policy_key,
                    "policy_text": "",
                    "error_message": "Simulated tool failure"
                }
                return json.dumps(result, ensure_ascii=False)

            if not policy_key:
                result = {
                    "tool_status": "not_found",
                    "policy_key": policy_key,
                    "policy_text": "",
                    "error_message": ""
                }
                return json.dumps(result, ensure_ascii=False)

            with open(policy_file, "r", encoding="utf-8") as f:
                policy_db = json.load(f)

            if policy_key not in policy_db:
                result = {
                    "tool_status": "not_found",
                    "policy_key": policy_key,
                    "policy_text": "",
                    "error_message": ""
                }
                return json.dumps(result, ensure_ascii=False)

            policy = policy_db[policy_key]
            policy_text = " ".join(policy["content"])

            result = {
                "tool_status": "success",
                "policy_key": policy_key,
                "policy_text": policy_text,
                "error_message": ""
            }

            latency_ms = int((time.time() - start_time) * 1000)
            print(json.dumps({
                "tool_name": "get_policy",
                "policy_key": policy_key,
                "status": result["tool_status"],
                "latency_ms": latency_ms
            }, ensure_ascii=False))

            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            result = {
                "tool_status": "error",
                "policy_key": policy_key,
                "policy_text": "",
                "error_message": str(e)
            }
            return json.dumps(result, ensure_ascii=False)