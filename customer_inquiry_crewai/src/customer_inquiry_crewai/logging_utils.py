import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"

EXPERIMENT_LOG = LOG_DIR / "experiment_results.jsonl"
AGENT_DETAIL_LOG = LOG_DIR / "agent_detail_logs.jsonl"
MAINTAINABILITY_LOG = LOG_DIR / "maintainability_log.jsonl"
SCALABILITY_LOG = LOG_DIR / "scalability_log.jsonl"


def ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, row: dict):
    ensure_log_dir()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def now_iso():
    return datetime.now().isoformat()


def log_experiment_result(row: dict):
    append_jsonl(EXPERIMENT_LOG, row)


def log_agent_detail(row: dict):
    append_jsonl(AGENT_DETAIL_LOG, row)


def log_maintainability(row: dict):
    append_jsonl(MAINTAINABILITY_LOG, row)


def log_scalability(row: dict):
    append_jsonl(SCALABILITY_LOG, row)