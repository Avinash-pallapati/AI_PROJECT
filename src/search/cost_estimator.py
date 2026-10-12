"""
================================================================================
MOCK COST ESTIMATOR — NOT REAL FPGA MEASUREMENT
================================================================================
This module provides a deterministic analytical hardware cost model for 
evaluating LUT, BRAM (18K), DSP, FF, and Latency under varying per-layer bit-widths.
It is explicitly labeled as an analytical simulation model for algorithm validation
and does NOT represent final physical FPGA bitstream measurements from Vivado.
================================================================================
"""

from typing import Dict, Any, Tuple
from src.quantization.brevitas_layers import get_layer_parameter_counts


class MockCostEstimator:
    """
    Deterministic analytical cost estimator simulating FPGA hardware resource scaling.
    Clearly labeled: MOCK COST ESTIMATOR — NOT REAL FPGA MEASUREMENT.
    """
    def __init__(self):
        self.label = "MOCK COST ESTIMATOR — NOT REAL FPGA MEASUREMENT"
        self.layer_params = get_layer_parameter_counts()
        self.total_params = sum(self.layer_params.values())

        # Baseline INT8 hardware reference values (Zynq-7020 baseline scale)
        self.base_lut = 18450
        self.base_bram_18k = 182
        self.base_dsp = 112
        self.base_ff = 36800
        self.base_latency_ms = 3.85

        # BRAM distribution across layers at INT8 (total = 182 blocks)
        # Weights account for majority; on-chip line buffers account for remainder
        self.layer_base_bram = {
            "conv0": 4,
            "conv1": 8,
            "conv2": 14,
            "conv3": 20,
            "conv4": 32,
            "conv5": 44,
            "fc0":   56,
            "fc1":   4
        }

        # DSP allocation across layers (total = 112 slices)
        self.layer_base_dsp = {
            "conv0": 8,
            "conv1": 12,
            "conv2": 16,
            "conv3": 20,
            "conv4": 24,
            "conv5": 24,
            "fc0":   8,
            "fc1":   0  # Synthesized in logic
        }

    def estimate_cost(self, precision_config: Dict[str, int]) -> Dict[str, Any]:
        """
        Estimates hardware resources and latency for a given per-layer precision map.
        Returns:
            dict containing lut, bram_18k, dsp, ff, latency_ms, estimator_type
        """
        total_bram = 0
        total_dsp = 0
        lut_delta = 0

        for layer, bits in precision_config.items():
            base_bram = self.layer_base_bram.get(layer, 10)
            base_dsp = self.layer_base_dsp.get(layer, 10)

            # BRAM scales directly with parameter bit-width
            bram_scale = bits / 8.0
            layer_bram = round(base_bram * bram_scale)
            total_bram += layer_bram

            # In sub-byte precision (INT4), arithmetic can migrate to packed DSPs or LUTs
            if bits <= 4:
                # 50% DSP reduction; minor LUT logic increase for unpacking/multiplexing
                total_dsp += round(base_dsp * 0.5)
                lut_delta += round(base_dsp * 12)  # ~12 LUTs per packed multiplier channel
            else:
                total_dsp += base_dsp

        # Flip-flops scale with pipelining and data bus widths
        avg_bit_width = sum(precision_config.values()) / max(len(precision_config), 1)
        ff_scale = avg_bit_width / 8.0
        total_ff = round(self.base_ff * (0.6 + 0.4 * ff_scale))

        # Total LUTs: base logic + packing multiplexers
        total_lut = self.base_lut + lut_delta - round((8.0 - avg_bit_width) * 220)

        # Latency: memory transfer time drops with reduced bit-width
        # Compute initiation interval bottleneck
        latency_scale = 0.5 + 0.5 * (avg_bit_width / 8.0)
        est_latency = round(self.base_latency_ms * latency_scale, 3)

        return {
            "estimator_type": self.label,
            "lut": int(total_lut),
            "bram_18k": int(total_bram),
            "dsp": int(total_dsp),
            "ff": int(total_ff),
            "latency_ms": float(est_latency)
        }
