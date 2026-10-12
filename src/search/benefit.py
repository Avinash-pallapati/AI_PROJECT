"""
Benefit scoring module: computes transparent normalized hardware benefit score.
"""

from typing import Dict, Any


class BenefitCalculator:
    """
    Computes a transparent, normalized hardware benefit score relative to baseline.
    Formula:
        Score = w_bram * (dBRAM / BaseBRAM) + w_dsp * (dDSP / BaseDSP) + 
                w_lut * (dLUT / BaseLUT) + w_lat * (dLat / BaseLat)
    """
    def __init__(
        self,
        base_lut: int = 18450,
        base_bram: int = 182,
        base_dsp: int = 112,
        base_latency: float = 3.85,
        w_bram: float = 0.50,
        w_lut: float = 0.20,
        w_dsp: float = 0.20,
        w_lat: float = 0.10
    ):
        self.base_lut = max(base_lut, 1)
        self.base_bram = max(base_bram, 1)
        self.base_dsp = max(base_dsp, 1)
        self.base_latency = max(base_latency, 0.001)

        self.w_bram = w_bram
        self.w_lut = w_lut
        self.w_dsp = w_dsp
        self.w_lat = w_lat

    def calculate_score(
        self,
        cost_dict: Dict[str, Any]
    ) -> float:
        """
        Computes benefit score. Positive score indicates hardware resource savings.
        """
        cand_lut = cost_dict.get("lut", self.base_lut)
        cand_bram = cost_dict.get("bram_18k", self.base_bram)
        cand_dsp = cost_dict.get("dsp", self.base_dsp)
        cand_latency = cost_dict.get("latency_ms", self.base_latency)

        bram_red = (self.base_bram - cand_bram) / self.base_bram
        dsp_red = (self.base_dsp - cand_dsp) / self.base_dsp
        lut_red = (self.base_lut - cand_lut) / self.base_lut
        lat_red = (self.base_latency - cand_latency) / self.base_latency

        score = (
            self.w_bram * bram_red +
            self.w_dsp * dsp_red +
            self.w_lut * lut_red +
            self.w_lat * lat_red
        )

        return round(float(score), 4)
