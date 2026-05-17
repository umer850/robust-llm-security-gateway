import json
import logging
from datetime import datetime
import os

LOG_FILE = "results/audit_log.jsonl"
os.makedirs("results", exist_ok=True)

def log_audit_event(event_data: dict):
    """
    Appends an audit event (dict) as a JSON line to the audit log.
    """
    event_data["timestamp"] = datetime.utcnow().isoformat()
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Failed to write audit log: {e}")

