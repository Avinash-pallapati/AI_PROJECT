"""
Constraint Checker for Greedy Search candidates.
Validates multi-dimensional hardware resource budgets and accuracy thresholds.
"""

from typing import Dict, Any, Tuple


class ConstraintChecker:
    def __init__(
        self,
        max_accuracy_drop: float = 1.50,
        max_lut: int = 25000,
        max_bram_18k: int = 160,
        max_dsp: int = 120,
        max_ff: int = 50000,
        max_latency_ms: float = 3.50
    ):
        self.max_accuracy_drop = max_accuracy_drop
        self.max_lut = max_lut
        self.max_bram_18k = max_bram_18k
        self.max_dsp = max_dsp
        self.max_ff = max_ff
        self.max_latency_ms = max_latency_ms

    def check_constraints(
        self,
        accuracy_drop: float,
        cost_dict: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Evaluates whether a candidate satisfies all configured constraints.
        Returns:
            (is_valid: bool, status_or_rejection_reason: str)
        """
        # 1. Accuracy Constraint
        if accuracy_drop > self.max_accuracy_drop:
            return False, f"Accuracy drop violation: {accuracy_drop:.2f}% > max {self.max_accuracy_drop:.2f}%"

        # 2. LUT Constraint
        lut = cost_dict.get("lut", 0)
        if lut > self.max_lut:
            return False, f"LUT budget exceeded: {lut} > max {self.max_lut}"

        # 3. BRAM Constraint
        bram = cost_dict.get("bram_18k", 0)
        if bram > self.max_bram_18k:
            return False, f"BRAM budget exceeded: {bram} > max {self.max_bram_18k}"

        # 4. DSP Constraint
        dsp = cost_dict.get("dsp", 0)
        if dsp > self.max_dsp:
            return False, f"DSP budget exceeded: {dsp} > max {self.max_dsp}"

        # 5. FF Constraint
        ff = cost_dict.get("ff", 0)
        if ff > self.max_ff:
            return False, f"FF budget exceeded: {ff} > max {self.max_ff}"

        # 6. Latency Constraint
        latency = cost_dict.get("latency_ms", 0.0)
        if self.max_latency_ms and latency > self.max_latency_ms:
            return False, f"Latency ceiling exceeded: {latency:.2f}ms > max {self.max_latency_ms:.2f}ms"

        return True, "PASSED_ALL_CONSTRAINTS"
