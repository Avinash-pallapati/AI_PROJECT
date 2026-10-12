"""
Accelerator-Aware Greedy Mixed-Precision Search Engine.
Orchestrates candidate generation, evaluation, cost estimation, constraint gating,
and selection of optimal per-layer precisions for QCore-INT8.
"""

from typing import Dict, Any, List, Optional
import copy

from src.models.cnv import CNV_Quantized
from src.evaluation.evaluator import BASELINE_ACCURACY
from src.search.candidate_generator import CandidateGenerator
from src.search.accuracy_evaluator import AccuracyEvaluator
from src.search.cost_estimator import MockCostEstimator
from src.search.constraint_checker import ConstraintChecker
from src.search.benefit import BenefitCalculator
from src.search.logger import SearchLogger


class GreedySearchEngine:
    def __init__(
        self,
        baseline_accuracy: float = BASELINE_ACCURACY,
        supported_precisions: List[int] = None,
        sensitivity_ranking: List[Dict[str, Any]] = None,
        max_accuracy_drop: float = 1.50,
        max_lut: int = 25000,
        max_bram_18k: int = 160,
        max_dsp: int = 120,
        max_ff: int = 50000,
        max_latency_ms: float = 3.50,
        log_csv_path: str = "./results/search/search_history.csv"
    ):
        self.baseline_accuracy = baseline_accuracy
        self.supported_precisions = supported_precisions or [8, 4]
        self.sensitivity_ranking = sensitivity_ranking or []

        # Submodules
        self.generator = CandidateGenerator(
            supported_precisions=self.supported_precisions,
            sensitivity_ranking=self.sensitivity_ranking
        )
        self.accuracy_evaluator = AccuracyEvaluator(baseline_accuracy=self.baseline_accuracy)
        self.cost_estimator = MockCostEstimator()
        self.constraint_checker = ConstraintChecker(
            max_accuracy_drop=max_accuracy_drop,
            max_lut=max_lut,
            max_bram_18k=max_bram_18k,
            max_dsp=max_dsp,
            max_ff=max_ff,
            max_latency_ms=max_latency_ms
        )
        self.benefit_calculator = BenefitCalculator(
            base_lut=self.cost_estimator.base_lut,
            base_bram=self.cost_estimator.base_bram_18k,
            base_dsp=self.cost_estimator.base_dsp,
            base_latency=self.cost_estimator.base_latency_ms
        )
        self.logger = SearchLogger(log_csv_path=log_csv_path)

        # State tracking
        self.all_layers = CNV_Quantized.QUANTIZABLE_LAYERS
        self.current_config = {l: 8 for l in self.all_layers}
        self.accepted_history: List[Dict[str, Any]] = []

    def run_search(self, max_iterations: int = 15) -> Dict[str, Any]:
        """
        Executes the iterative greedy search.
        """
        print("==================================================")
        print("STARTING ACCELERATOR-AWARE GREEDY SEARCH")
        print("==================================================")
        print(f"Initial State: All layers at INT8 | Baseline Acc: {self.baseline_accuracy:.2f}%")
        base_cost = self.cost_estimator.estimate_cost(self.current_config)
        print(f"Baseline Resources: BRAM={base_cost['bram_18k']} blocks | DSP={base_cost['dsp']} | LUT={base_cost['lut']} | Latency={base_cost['latency_ms']} ms")

        current_benefit = 0.0

        for iteration in range(1, max_iterations + 1):
            print(f"\n--- Iteration {iteration} ---")
            candidates = self.generator.generate_candidates(self.current_config)

            if not candidates:
                print("Termination: No further candidates can be generated.")
                break

            valid_candidates = []

            for cand in candidates:
                cand_config = cand["config"]
                layer = cand["layer"]
                old_bits = cand["old_bits"]
                new_bits = cand["new_bits"]
                cand_id = cand["candidate_id"]

                # 1. Hardware support check
                if not cand["is_supported"]:
                    rejection_reason = f"Precision INT{new_bits} unsupported by QCore-INT8"
                    self.logger.log_candidate(
                        iteration, cand_id, layer, old_bits, new_bits,
                        0.0, 100.0, {}, 0.0, "UNSUPPORTED_PRECISION", False, rejection_reason
                    )
                    continue

                # 2. Evaluate Accuracy
                acc, acc_drop = self.accuracy_evaluator.evaluate(cand_config)

                # 3. Estimate Hardware Cost
                cost_dict = self.cost_estimator.estimate_cost(cand_config)

                # 4. Check Constraints
                is_valid, constraint_status = self.constraint_checker.check_constraints(acc_drop, cost_dict)

                # 5. Compute Benefit
                benefit_score = self.benefit_calculator.calculate_score(cost_dict)

                if is_valid:
                    valid_candidates.append({
                        "cand_id": cand_id,
                        "layer": layer,
                        "old_bits": old_bits,
                        "new_bits": new_bits,
                        "config": cand_config,
                        "accuracy": acc,
                        "accuracy_drop": acc_drop,
                        "cost": cost_dict,
                        "benefit_score": benefit_score,
                        "constraint_status": constraint_status
                    })
                else:
                    self.logger.log_candidate(
                        iteration, cand_id, layer, old_bits, new_bits,
                        acc, acc_drop, cost_dict, benefit_score, "CONSTRAINT_VIOLATION", False, constraint_status
                    )

            if not valid_candidates:
                print("Termination: No valid candidates satisfied accuracy/resource constraints.")
                break

            # Pick candidate with highest benefit score
            best_candidate = max(valid_candidates, key=lambda x: x["benefit_score"])

            if best_candidate["benefit_score"] <= current_benefit:
                print("Termination: Best candidate does not provide further positive hardware benefit.")
                break

            # Accept candidate
            self.current_config = best_candidate["config"]
            current_benefit = best_candidate["benefit_score"]

            # Log acceptance
            self.logger.log_candidate(
                iteration,
                best_candidate["cand_id"],
                best_candidate["layer"],
                best_candidate["old_bits"],
                best_candidate["new_bits"],
                best_candidate["accuracy"],
                best_candidate["accuracy_drop"],
                best_candidate["cost"],
                best_candidate["benefit_score"],
                best_candidate["constraint_status"],
                True,
                "ACCEPTED_BEST_BENEFIT"
            )

            # Log other valid candidates as rejected for this iteration (suboptimal benefit)
            for other_cand in valid_candidates:
                if other_cand["cand_id"] != best_candidate["cand_id"]:
                    self.logger.log_candidate(
                        iteration,
                        other_cand["cand_id"],
                        other_cand["layer"],
                        other_cand["old_bits"],
                        other_cand["new_bits"],
                        other_cand["accuracy"],
                        other_cand["accuracy_drop"],
                        other_cand["cost"],
                        other_cand["benefit_score"],
                        other_cand["constraint_status"],
                        False,
                        f"REJECTED_SUBOPTIMAL (Score {other_cand['benefit_score']:.4f} < Best {best_candidate['benefit_score']:.4f})"
                    )

            self.accepted_history.append(best_candidate)
            print(f"ACCEPTED: Layer {best_candidate['layer']} (INT{best_candidate['old_bits']} -> INT{best_candidate['new_bits']})")
            print(f"  -> Acc: {best_candidate['accuracy']:.2f}% (Drop: {best_candidate['accuracy_drop']:.2f}%) | Benefit Score: {best_candidate['benefit_score']:.4f}")
            print(f"  -> BRAM: {best_candidate['cost']['bram_18k']} blocks | DSP: {best_candidate['cost']['dsp']} | LUT: {best_candidate['cost']['lut']}")

        # Final evaluation
        final_acc, final_drop = self.accuracy_evaluator.evaluate(self.current_config)
        final_cost = self.cost_estimator.estimate_cost(self.current_config)

        summary = {
            "search_status": "COMPLETED",
            "total_accepted_steps": len(self.accepted_history),
            "final_accuracy": final_acc,
            "final_accuracy_drop": final_drop,
            "baseline_accuracy": self.baseline_accuracy,
            "final_precisions": self.current_config,
            "final_hardware_cost": final_cost,
            "resource_reduction": {
                "bram_blocks_saved": base_cost["bram_18k"] - final_cost["bram_18k"],
                "bram_reduction_pct": round(100.0 * (base_cost["bram_18k"] - final_cost["bram_18k"]) / base_cost["bram_18k"], 2),
                "dsp_slices_saved": base_cost["dsp"] - final_cost["dsp"],
                "dsp_reduction_pct": round(100.0 * (base_cost["dsp"] - final_cost["dsp"]) / base_cost["dsp"], 2),
                "latency_saved_ms": round(base_cost["latency_ms"] - final_cost["latency_ms"], 3),
                "latency_reduction_pct": round(100.0 * (base_cost["latency_ms"] - final_cost["latency_ms"]) / base_cost["latency_ms"], 2)
            },
            "accepted_history": self.accepted_history
        }

        print("\n==================================================")
        print("SEARCH COMPLETE")
        print("==================================================")
        print(f"Final Accuracy: {final_acc:.2f}% (Degradation: {final_drop:+.2f}%)")
        print(f"BRAM Reduction: {summary['resource_reduction']['bram_reduction_pct']}% ({summary['resource_reduction']['bram_blocks_saved']} blocks saved)")
        print(f"DSP Reduction:  {summary['resource_reduction']['dsp_reduction_pct']}% ({summary['resource_reduction']['dsp_slices_saved']} slices saved)")
        print(f"Final Precision Map: {self.current_config}")
        return summary
