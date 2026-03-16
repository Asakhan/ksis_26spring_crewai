from typing import List, Literal
from pydantic import BaseModel, Field


class IntentAnalysisOutput(BaseModel):
    intent: Literal["refund", "exchange", "delivery", "membership", "cancel", "unknown"]
    needs_policy_lookup: bool
    policy_key: str = Field(default="")
    ambiguity: bool
    missing_info: List[str] = Field(default_factory=list)


class PolicyRetrievalOutput(BaseModel):
    tool_status: Literal["success", "not_found", "error"]
    policy_key: str = Field(default="")
    policy_text: str = Field(default="")
    error_message: str = Field(default="")


class ResponseGenerationOutput(BaseModel):
    answer: str
    answer_status: Literal["success", "needs_clarification", "tool_error", "policy_not_found"]
    used_policy_key: str = Field(default="")