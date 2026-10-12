#!/usr/bin/env python3
"""
Run Layer-Sensitivity Analysis on CNV CIFAR-10 model.
Evaluates single-layer INT8 -> INT4 accuracy degradation and produces ranking.
"""

import os
import sys
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.sensitivity.sensitivity_runner import SensitivityRunner
from src.evaluation.evaluator import BASELINE_ACCURACY


def main():
    parser = argparse.ArgumentParser(description="Run layer sensitivity analysis.")
    parser.add_argument("--baseline-acc", type=float, default=BASELINE_ACCURACY)
    parser.add_argument("--target-bits", type=int, default=4)
    parser.add_argument("--output-csv", type=str, default="./results/sensitivity/sensitivity_results.csv")
    parser.add_argument("--output-json", type=str, default="./results/sensitivity/sensitivity_ranking.json")
    args = parser.parse_args()

    runner = SensitivityRunner(
        baseline_accuracy=args.baseline_acc,
        target_bit_width=args.target_bits
    )
    runner.run_layer_sensitivity()
    runner.save_results(csv_path=args.output_csv, ranking_path=args.output_json)


if __name__ == "__main__":
    main()
