#!/usr/bin/env python3
"""
Execute Accelerator-Aware Greedy Mixed-Precision Search on CNV CIFAR-10 model for QCore-INT8.
"""

import os
import sys
import json
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.search.greedy_search import GreedySearchEngine
from src.search.visualize_search import render_search_progression_svg
from src.evaluation.evaluator import BASELINE_ACCURACY


def main():
    parser = argparse.ArgumentParser(description="Run Accelerator-Aware Greedy Search.")
    parser.add_argument("--ranking-json", type=str, default="./results/sensitivity/sensitivity_ranking.json")
    parser.add_argument("--max-drop", type=float, default=1.50)
    parser.add_argument("--max-lut", type=int, default=25000)
    parser.add_argument("--max-bram", type=int, default=160)
    parser.add_argument("--max-dsp", type=int, default=120)
    parser.add_argument("--max-ff", type=int, default=50000)
    parser.add_argument("--max-latency", type=float, default=3.50)
    parser.add_argument("--output-csv", type=str, default="./results/search/search_history.csv")
    parser.add_argument("--output-json", type=str, default="./results/search/final_precision_config.json")
    parser.add_argument("--summary-json", type=str, default="./results/search/search_summary.json")
    parser.add_argument("--plot-svg", type=str, default="./results/search/plots/search_convergence.svg")
    args = parser.parse_args()

    # Load ranking
    ranking = []
    if os.path.exists(args.ranking_json):
        with open(args.ranking_json, "r", encoding="utf-8") as f:
            ranking = json.load(f)

    engine = GreedySearchEngine(
        baseline_accuracy=BASELINE_ACCURACY,
        supported_precisions=[8, 4],
        sensitivity_ranking=ranking,
        max_accuracy_drop=args.max_drop,
        max_lut=args.max_lut,
        max_bram_18k=args.max_bram,
        max_dsp=args.max_dsp,
        max_ff=args.max_ff,
        max_latency_ms=args.max_latency,
        log_csv_path=args.output_csv
    )

    summary = engine.run_search(max_iterations=15)

    # Save final config
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(summary["final_precisions"], f, indent=2)

    # Save summary
    with open(args.summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Render plot
    render_search_progression_svg(args.output_csv, args.plot_svg)
    print(f"\nFinal Precision Configuration saved to: {args.output_json}")
    print(f"Search Summary saved to: {args.summary_json}")
    print(f"Search History CSV saved to: {args.output_csv}")


if __name__ == "__main__":
    main()
