"""
Accuracy Evaluator for Greedy Search candidates.
"""

from typing import Dict, Any, Tuple
from src.evaluation.evaluator import analytical_evaluate, BASELINE_ACCURACY


class AccuracyEvaluator:
    def __init__(self, baseline_accuracy: float = BASELINE_ACCURACY):
        self.baseline_accuracy = baseline_accuracy

    def evaluate(self, precision_config: Dict[str, int]) -> Tuple[float, float]:
        """
        Evaluates accuracy of a candidate precision configuration.
        Returns:
            (accuracy, accuracy_drop)
        """
        acc = analytical_evaluate(precision_config)
        acc_drop = round(self.baseline_accuracy - acc, 2)
        return acc, acc_drop
