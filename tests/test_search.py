"""
Comprehensive Unit Tests for Accelerator-Aware Greedy Search Engine.
Tests all 11 mandatory criteria from the Master Game Plan:
1. Candidate generation
2. Unsupported precision rejection
3. Accuracy constraint
4. LUT constraint
5. BRAM constraint
6. DSP constraint
7. FF constraint
8. Candidate scoring
9. Search termination
10. Search logging
11. Final configuration validity
"""

import unittest
import os
import csv
from src.search.candidate_generator import CandidateGenerator
from src.search.constraint_checker import ConstraintChecker
from src.search.benefit import BenefitCalculator
from src.search.cost_estimator import MockCostEstimator
from src.search.logger import SearchLogger
from src.search.greedy_search import GreedySearchEngine
from src.models.cnv import CNV_Quantized


class TestGreedySearch(unittest.TestCase):
    def setUp(self):
        self.ranking = [
            {"layer": "conv3", "accuracy_drop": 0.28},
            {"layer": "conv2", "accuracy_drop": 0.31},
            {"layer": "conv4", "accuracy_drop": 0.35},
            {"layer": "conv1", "accuracy_drop": 0.42},
            {"layer": "fc0",   "accuracy_drop": 0.45},
            {"layer": "conv5", "accuracy_drop": 0.78},
            {"layer": "conv0", "accuracy_drop": 3.85},
            {"layer": "fc1",   "accuracy_drop": 4.20}
        ]

    # Test 1: Candidate generation
    def test_01_candidate_generation(self):
        generator = CandidateGenerator(
            supported_precisions=[8, 4],
            sensitivity_ranking=self.ranking
        )
        current_config = {l: 8 for l in CNV_Quantized.QUANTIZABLE_LAYERS}
        cands = generator.generate_candidates(current_config)
        self.assertEqual(len(cands), 8)
        # Verify sensitivity order (first candidate should be least sensitive: conv3)
        self.assertEqual(cands[0]["layer"], "conv3")
        self.assertEqual(cands[0]["old_bits"], 8)
        self.assertEqual(cands[0]["new_bits"], 4)

    # Test 2: Unsupported precision rejection
    def test_02_unsupported_precision_rejection(self):
        generator = CandidateGenerator(supported_precisions=[8, 4])
        self.assertTrue(generator.is_precision_supported(8))
        self.assertTrue(generator.is_precision_supported(4))
        self.assertFalse(generator.is_precision_supported(6))
        self.assertFalse(generator.is_precision_supported(2))

    # Test 3: Accuracy constraint
    def test_03_accuracy_constraint(self):
        checker = ConstraintChecker(max_accuracy_drop=1.50)
        cost = {"lut": 18000, "bram_18k": 150, "dsp": 100, "ff": 35000, "latency_ms": 3.2}
        valid, msg = checker.check_constraints(accuracy_drop=1.20, cost_dict=cost)
        self.assertTrue(valid)

        invalid, reason = checker.check_constraints(accuracy_drop=1.85, cost_dict=cost)
        self.assertFalse(invalid)
        self.assertIn("Accuracy drop violation", reason)

    # Test 4: LUT constraint
    def test_04_lut_constraint(self):
        checker = ConstraintChecker(max_lut=20000)
        cost_ok = {"lut": 19500, "bram_18k": 150, "dsp": 100, "ff": 35000, "latency_ms": 3.2}
        self.assertTrue(checker.check_constraints(0.5, cost_ok)[0])

        cost_bad = {"lut": 21000, "bram_18k": 150, "dsp": 100, "ff": 35000, "latency_ms": 3.2}
        valid, reason = checker.check_constraints(0.5, cost_bad)
        self.assertFalse(valid)
        self.assertIn("LUT budget exceeded", reason)

    # Test 5: BRAM constraint
    def test_05_bram_constraint(self):
        checker = ConstraintChecker(max_bram_18k=150)
        cost_ok = {"lut": 18000, "bram_18k": 140, "dsp": 100, "ff": 35000, "latency_ms": 3.2}
        self.assertTrue(checker.check_constraints(0.5, cost_ok)[0])

        cost_bad = {"lut": 18000, "bram_18k": 165, "dsp": 100, "ff": 35000, "latency_ms": 3.2}
        valid, reason = checker.check_constraints(0.5, cost_bad)
        self.assertFalse(valid)
        self.assertIn("BRAM budget exceeded", reason)

    # Test 6: DSP constraint
    def test_06_dsp_constraint(self):
        checker = ConstraintChecker(max_dsp=100)
        cost_ok = {"lut": 18000, "bram_18k": 140, "dsp": 90, "ff": 35000, "latency_ms": 3.2}
        self.assertTrue(checker.check_constraints(0.5, cost_ok)[0])

        cost_bad = {"lut": 18000, "bram_18k": 140, "dsp": 115, "ff": 35000, "latency_ms": 3.2}
        valid, reason = checker.check_constraints(0.5, cost_bad)
        self.assertFalse(valid)
        self.assertIn("DSP budget exceeded", reason)

    # Test 7: FF constraint
    def test_07_ff_constraint(self):
        checker = ConstraintChecker(max_ff=40000)
        cost_ok = {"lut": 18000, "bram_18k": 140, "dsp": 90, "ff": 38000, "latency_ms": 3.2}
        self.assertTrue(checker.check_constraints(0.5, cost_ok)[0])

        cost_bad = {"lut": 18000, "bram_18k": 140, "dsp": 90, "ff": 42000, "latency_ms": 3.2}
        valid, reason = checker.check_constraints(0.5, cost_bad)
        self.assertFalse(valid)
        self.assertIn("FF budget exceeded", reason)

    # Test 8: Candidate scoring
    def test_08_candidate_scoring(self):
        calc = BenefitCalculator(base_bram=182, base_dsp=112, base_lut=18450, base_latency=3.85)
        # Reduced resources should give positive score
        cand_cost = {"lut": 18000, "bram_18k": 120, "dsp": 80, "latency_ms": 3.0}
        score = calc.calculate_score(cand_cost)
        self.assertGreater(score, 0.0)

    # Test 9: Search termination
    def test_09_search_termination(self):
        # Setting impossible accuracy drop should terminate immediately at iteration 1
        engine = GreedySearchEngine(
            max_accuracy_drop=0.01,
            sensitivity_ranking=self.ranking,
            log_csv_path="./results/search/test_termination_log.csv"
        )
        res = engine.run_search(max_iterations=10)
        self.assertEqual(res["total_accepted_steps"], 0)
        if os.path.exists("./results/search/test_termination_log.csv"):
            os.remove("./results/search/test_termination_log.csv")

    # Test 10: Search logging
    def test_10_search_logging(self):
        test_log = "./results/search/test_search_log.csv"
        logger = SearchLogger(log_csv_path=test_log)
        logger.log_candidate(
            iteration=1,
            candidate_id="cand_001",
            layer="conv3",
            old_precision=8,
            new_precision=4,
            accuracy=83.84,
            accuracy_drop=0.28,
            cost_dict={"lut": 18400, "bram_18k": 172, "dsp": 102, "ff": 36000, "latency_ms": 3.8},
            benefit_score=0.052,
            constraint_status="PASSED",
            accepted=True,
            rejection_reason="ACCEPTED_BEST_BENEFIT"
        )
        self.assertTrue(os.path.exists(test_log))
        with open(test_log, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 1)
            self.assertEqual(reader[0]["candidate_id"], "cand_001")
            self.assertEqual(reader[0]["accepted_rejected"], "ACCEPTED")
        os.remove(test_log)

    # Test 11: Final configuration validity
    def test_11_final_configuration_validity(self):
        engine = GreedySearchEngine(
            max_accuracy_drop=1.50,
            sensitivity_ranking=self.ranking,
            log_csv_path="./results/search/test_validity_log.csv"
        )
        res = engine.run_search(max_iterations=10)
        final_cfg = res["final_precisions"]
        self.assertEqual(len(final_cfg), 8)
        for layer, bits in final_cfg.items():
            self.assertIn(bits, [8, 4])
        # Ensure sensitive layer fc1 was preserved at INT8
        self.assertEqual(final_cfg["fc1"], 8)
        self.assertEqual(final_cfg["conv0"], 8)
        if os.path.exists("./results/search/test_validity_log.csv"):
            os.remove("./results/search/test_validity_log.csv")


if __name__ == "__main__":
    unittest.main()
