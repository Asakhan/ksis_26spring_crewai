# CrewAI Customer Inquiry Experiment

본 프로젝트는 **AI Agent Framework 비교 연구**를 위한 CrewAI 기반 통제 실험 구현체입니다.

실험 목적은 다음과 같습니다.

* 서비스 개발 관점에서의 적합성 평가
* 유지보수성 및 확장성 비교
* 운영 비용 및 실행 구조 분석
* LangGraph와의 정량 비교

---

# 1. 실험 아키텍처

본 실험은 **3-Agent 고정 구조**로 구성됩니다.

```
IntentAgent → PolicyAgent (Tool) → ResponseAgent
```

### Agent 구성

1. **IntentAgent**

   * 고객 문의를 분석
   * intent, needs_policy_lookup, policy_key 구조화 JSON 출력

2. **PolicyAgent**

   * 이전 task 결과 기반 정책 조회
   * 필요 시 get_policy tool 1회 호출
   * tool_status, policy_key, policy_text 반환

3. **ResponseAgent**

   * 최종 고객 응답 생성
   * answer_status 포함 JSON 반환

---

# 2. 통제 환경 (Controlled Environment)

실험 공정성을 위해 아래 항목은 고정됩니다.

* LLM: `gpt-4o-mini`
* temperature: `0`
* max_tokens: `512`
* 동일 system prompt 구조
* 동일 JSON 정책 DB
* 동일 Python tool 함수
* memory 비활성화
* self-reflection 비활성화
* replanning 비활성화
* delegation 비활성화
* 사람 개입 없음
* 최대 agent step = 3
* 최대 tool call = 1

---

# 3. 프로젝트 구조

```
customer_inquiry_crewai/
│
├── src/customer_inquiry_crewai/
│   ├── crew.py
│   ├── experiment_runner.py
│   ├── logging_utils.py
│   ├── tools.py
│   └── policy_db.json
│
├── logs/
│   ├── experiment_results.jsonl
│   ├── agent_detail_logs.jsonl
│   ├── maintainability_log.jsonl
│   └── scalability_log.jsonl
│
├── test_scenarios.json
└── README.md
```

---

# 4. 로그 구조

## 4.1 Summary Log

파일: `experiment_results.jsonl`
테스트 1건당 1줄 기록

```json
{
  "experiment_meta": {
    "run_id": "...",
    "framework": "CrewAI",
    "model": "gpt-4o-mini",
    "temperature": 0,
    "max_tokens": 512,
    "timestamp": "..."
  },
  "test_case": {
    "test_id": "N01",
    "type": "normal",
    "user_input": "..."
  },
  "execution_metrics": {
    "intent": "...",
    "policy_key": "...",
    "answer_status": "...",
    "task_success": true,
    "response_time_ms": 842,
    "total_token_usage": null,
    "tool_call_count": 1,
    "agent_step_count": 3
  },
  "error_info": {
    "tool_status": "success",
    "error_message": ""
  }
}
```

### 평가 항목 매핑

| 필드                     | 평가 지표         |
| ---------------------- | ------------- |
| task_success           | TSR 계산        |
| response_time_ms       | 평균 응답시간       |
| total_token_usage      | 평균 비용         |
| tool_call_count        | 운영 비용         |
| agent_step_count       | 구조 비교         |
| intent / answer_status | expected 값 비교 |

---

## 4.2 Agent Detail Log

파일: `agent_detail_logs.jsonl`
테스트 1건당 3줄 기록

```json
{
  "run_id": "...",
  "framework": "CrewAI",
  "test_id": "N01",
  "agent_stage": "IntentAgent",
  "input_tokens": null,
  "output_tokens": null,
  "latency_ms": null,
  "output_json": { ... }
}
```

용도:

* 중간 단계 오류 분석
* Agent 호출 구조 비교
* 부록용 로그

---

## 4.3 Maintainability Log

파일: `maintainability_log.jsonl`

정책 변경 실험 후 수동 기록

```json
{
  "framework": "CrewAI",
  "change_type": "policy_update",
  "modified_files": 1,
  "modified_lines": 4,
  "change_time_minutes": 6,
  "regression_pass_rate": 1.0
}
```

---

## 4.4 Scalability Log

파일: `scalability_log.jsonl`

Agent 추가 실험 후 수동 기록

```json
{
  "framework": "CrewAI",
  "change_type": "agent_addition",
  "new_agent": "SentimentAgent",
  "modified_files": 3,
  "modified_lines": 22,
  "dependency_change": true,
  "redeploy_time_minutes": 5,
  "regression_pass_rate": 0.95
}
```

---

# 5. 테스트 실행 방법

## 1. 가상환경 생성

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

## 2. 패키지 설치

```bash
pip install -r requirements.txt
```

## 3. 실험 실행

```bash
python src/customer_inquiry_crewai/experiment_runner.py
```

---

# 6. 테스트 시나리오 구조

`test_scenarios.json` 예시:

```json
{
  "id": "N01",
  "type": "normal",
  "user_input": "I want a refund",
  "expected": {
    "intent": "refund",
    "policy_key": "refund_policy",
    "answer_status": "success"
  }
}
```

---

# 7. JSON 출력 강제 구조

모든 Agent는 **Valid JSON Only** 정책을 따릅니다.

Pydantic 기반 구조 검증을 통해:

* key 누락 방지
* schema 불일치 방지
* 형식 오류 방지

---

# 8. 확장 실험 예시

SentimentAgent 추가 시:

* agent_step_count = 4
* modified_files 기록
* regression_pass_rate 계산

---

# 9. 재현성

* 동일 모델
* 동일 프롬프트
* 동일 정책 DB
* 동일 tool
* memory 비활성화

실험 재현이 가능하도록 설계되었습니다.

---

# 10. 연구 목적

본 구현은 다음 연구 질문에 답하기 위한 것입니다.

1. 실제 서비스 개발에 어떤 프레임워크가 유리한가
2. 유지보수성은 어떤가
3. 확장성은 어떤가
4. 운영 비용은 어떤가
5. 개발 생산성은 어떤가