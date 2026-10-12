"""
Search Logger: records every evaluated candidate and accept/reject decision.
"""

import os
import csv
import json
from typing import Dict, Any, List


class SearchLogger:
    HEADERS = [
        "iteration", "candidate_id", "layer", "old_precision", "new_precision",
        "accuracy", "accuracy_drop", "LUT", "BRAM", "DSP", "FF", "latency",
        "benefit_score", "constraint_status", "accepted_rejected", "rejection_reason"
    ]

    def __init__(self, log_csv_path: str = "./results/search/search_history.csv"):
        self.log_csv_path = log_csv_path
        self.history: List[Dict[str, Any]] = []
        os.makedirs(os.path.dirname(log_csv_path), exist_ok=True)
        
        # Write CSV header
        with open(self.log_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()

    def log_candidate(
        self,
        iteration: int,
        candidate_id: str,
        layer: str,
        old_precision: int,
        new_precision: int,
        accuracy: float,
        accuracy_drop: float,
        cost_dict: Dict[str, Any],
        benefit_score: float,
        constraint_status: str,
        accepted: bool,
        rejection_reason: str
    ):
        record = {
            "iteration": iteration,
            "candidate_id": candidate_id,
            "layer": layer,
            "old_precision": old_precision,
            "new_precision": new_precision,
            "accuracy": round(accuracy, 2),
            "accuracy_drop": round(accuracy_drop, 2),
            "LUT": cost_dict.get("lut", 0),
            "BRAM": cost_dict.get("bram_18k", 0),
            "DSP": cost_dict.get("dsp", 0),
            "FF": cost_dict.get("ff", 0),
            "latency": round(cost_dict.get("latency_ms", 0.0), 3),
            "benefit_score": round(benefit_score, 4),
            "constraint_status": constraint_status,
            "accepted_rejected": "ACCEPTED" if accepted else "REJECTED",
            "rejection_reason": rejection_reason
        }
        self.history.append(record)

        with open(self.log_csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writerow(record)

    def save_summary_json(self, json_path: str, summary_data: Dict[str, Any]):
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)
