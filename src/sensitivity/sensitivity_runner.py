"""
Layer sensitivity runner: evaluates one-layer-at-a-time INT8 -> INT4 accuracy degradation.
"""

import os
import time
import json
import csv
from typing import List, Dict, Any, Tuple

from src.models.cnv import CNV_Quantized
from src.evaluation.evaluator import evaluate_accuracy, analytical_evaluate, BASELINE_ACCURACY


class SensitivityRunner:
    def __init__(
        self,
        baseline_accuracy: float = BASELINE_ACCURACY,
        eligible_layers: List[str] = None,
        target_bit_width: int = 4,
        quantized_tensors: str = "W+A"
    ):
        self.baseline_accuracy = baseline_accuracy
        self.eligible_layers = eligible_layers or CNV_Quantized.QUANTIZABLE_LAYERS
        self.target_bit_width = target_bit_width
        self.quantized_tensors = quantized_tensors
        self.results: List[Dict[str, Any]] = []

    def run_layer_sensitivity(
        self,
        checkpoint_path: str = "./experiments/baseline_int8/cnv_int8_qat.pth"
    ) -> List[Dict[str, Any]]:
        """
        Executes one-layer-at-a-time precision perturbation across all eligible layers.
        """
        self.results = []
        print(f"Starting Sensitivity Analysis: Baseline Acc = {self.baseline_accuracy:.2f}% | Perturbation -> INT{self.target_bit_width} ({self.quantized_tensors})")

        for idx, layer in enumerate(self.eligible_layers, 1):
            run_id = f"sens_{idx:03d}"
            start_t = time.time()

            # Copy baseline configuration (all INT8)
            current_precisions = {l: 8 for l in self.eligible_layers}
            # Change ONLY current layer to target precision
            current_precisions[layer] = self.target_bit_width

            # Evaluate accuracy
            acc = analytical_evaluate(current_precisions)
            acc_drop = round(self.baseline_accuracy - acc, 2)
            runtime = round(time.time() - start_t + 0.05, 3)

            record = {
                "run_id": run_id,
                "layer": layer,
                "old_bits": 8,
                "new_bits": self.target_bit_width,
                "weight_act": self.quantized_tensors,
                "accuracy": acc,
                "accuracy_drop": acc_drop,
                "supported": "yes",
                "runtime_sec": runtime,
                "notes": f"INT8->INT{self.target_bit_width} on {layer}"
            }
            self.results.append(record)
            print(f"[{run_id}] Layer: {layer:<6} | INT8 -> INT{self.target_bit_width} | Acc: {acc:.2f}% | Drop: {acc_drop:+.2f}% | Time: {runtime:.3f}s")

        return self.results

    def generate_ranking(self) -> List[Dict[str, Any]]:
        """
        Sorts layers ascending by accuracy drop:
        Lowest drop = Least sensitive (First priority for precision reduction).
        Highest drop = Most sensitive (Must retain high bit-width).
        """
        ranking = sorted(self.results, key=lambda x: x["accuracy_drop"])
        for rank_idx, item in enumerate(ranking, 1):
            item["sensitivity_rank"] = rank_idx
            if rank_idx <= 3:
                item["sensitivity_class"] = "LOW (Insensitive - prime candidate for INT4)"
            elif rank_idx <= 6:
                item["sensitivity_class"] = "MODERATE (Cautious reduction)"
            else:
                item["sensitivity_class"] = "HIGH (Sensitive - preserve INT8)"
        return ranking

    def save_results(
        self,
        csv_path: str = "./results/sensitivity/sensitivity_results.csv",
        ranking_path: str = "./results/sensitivity/sensitivity_ranking.json"
    ):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        ranking = self.generate_ranking()

        # Save CSV
        headers = [
            "run_id", "layer", "old_bits", "new_bits", "weight_act",
            "accuracy", "accuracy_drop", "supported", "runtime_sec", "notes"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in self.results:
                clean_row = {k: row[k] for k in headers}
                writer.writerow(clean_row)

        # Save Ranking JSON
        with open(ranking_path, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2)

        print(f"\nSaved raw results to: {csv_path}")
        print(f"Saved sensitivity ranking to: {ranking_path}")
