"""
Candidate Generator: produces valid, hardware-supported one-step precision reduction candidates.
"""

from typing import List, Dict, Any, Tuple


class CandidateGenerator:
    """
    Generates precision reduction candidates ordered by layer sensitivity.
    Strictly filters out unsupported hardware bit-widths.
    """
    def __init__(
        self,
        supported_precisions: List[int] = None,
        sensitivity_ranking: List[Dict[str, Any]] = None,
        require_verified_precision: bool = True
    ):
        # Default verified set: INT8 (native), INT4 (sub-byte packing)
        self.supported_precisions = supported_precisions or [8, 4]
        self.sensitivity_ranking = sensitivity_ranking or []
        self.require_verified_precision = require_verified_precision
        
        # Build layer search priority from sensitivity ranking (least sensitive first)
        self.layer_priority = [
            item["layer"] for item in sorted(
                self.sensitivity_ranking, key=lambda x: x.get("accuracy_drop", 0.0)
            )
        ]

    def is_precision_supported(self, bit_width: int) -> bool:
        """Validates if a precision level is supported by the target accelerator."""
        return bit_width in self.supported_precisions

    def generate_candidates(
        self,
        current_config: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Generates one-step reduction candidates for all layers that can be reduced.
        Returns candidate descriptors ordered by layer sensitivity priority.
        """
        candidates = []
        ordered_layers = self.layer_priority if self.layer_priority else list(current_config.keys())

        # For layers not in sensitivity ranking, append them at the end
        for l in current_config.keys():
            if l not in ordered_layers:
                ordered_layers.append(l)

        candidate_counter = 1
        for layer in ordered_layers:
            curr_bits = current_config[layer]
            
            # Determine potential one-step lower precisions
            # Standard transition: 8 -> 4
            next_precisions = [p for p in sorted(self.supported_precisions, reverse=True) if p < curr_bits]
            
            for next_bits in next_precisions:
                new_config = dict(current_config)
                new_config[layer] = next_bits
                
                cand = {
                    "candidate_id": f"cand_{candidate_counter:03d}",
                    "layer": layer,
                    "old_bits": curr_bits,
                    "new_bits": next_bits,
                    "config": new_config,
                    "is_supported": self.is_precision_supported(next_bits)
                }
                candidate_counter += 1
                candidates.append(cand)

        return candidates
