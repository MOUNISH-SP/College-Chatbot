import json
from datetime import datetime


def log_interaction(question, confidence):
    log_entry = {
        "timestamp": str(datetime.now()),
        "question": question,
        "confidence_score": confidence
    }

    with open("logs.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
