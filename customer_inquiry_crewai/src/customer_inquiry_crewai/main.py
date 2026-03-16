#!/usr/bin/env python
import sys
import json
import warnings

from customer_inquiry_crewai.crew import CustomerInquiryCrewai

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew in interactive mode.
    User enters a customer inquiry manually.
    """
    customer_query = input("고객 문의를 입력하세요: ").strip()

    if not customer_query:
        print("문의 문장이 비어 있습니다.")
        return

    inputs = {
        "customer_query": customer_query,
        "scenario_id": ""
    }

    try:
        crew_instance = CustomerInquiryCrewai().crew()
        result = crew_instance.kickoff(inputs=inputs)

        print("\n===== FINAL RESULT =====")
        print(result)

        print("\n===== TASK OUTPUTS =====")
        for idx, task_output in enumerate(crew_instance.tasks_output, start=1):
            print(f"\n[Task {idx}]")
            if task_output.pydantic:
                print(task_output.pydantic.model_dump_json(
                    ensure_ascii=False,
                    indent=2
                ))
            else:
                print(task_output.raw)

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    For this experiment, a fixed sample query is used.
    """
    inputs = {
        "customer_query": "환불받고 싶은데 구매한 지 3일 됐어요."
    }
    try:
        CustomerInquiryCrewai().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CustomerInquiryCrewai().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and return the results.
    For this experiment, a fixed sample query is used.
    """
    inputs = {
        "customer_query": "배송은 보통 며칠 걸리나요?"
    }

    try:
        CustomerInquiryCrewai().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    Expected payload example:
    {"customer_query": "환불받고 싶은데 구매한 지 3일 됐어요."}
    """

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    customer_query = trigger_payload.get("customer_query", "").strip()

    if not customer_query:
        raise Exception("Trigger payload must include 'customer_query'.")

    scenario_id = trigger_payload.get("scenario_id", "").strip()

    inputs = {
        "customer_query": customer_query,
        "scenario_id": scenario_id
    }

    try:
        result = CustomerInquiryCrewai().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")