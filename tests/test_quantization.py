"""
Unit tests for quantization size calculation and bit scaling.
"""

import unittest
from src.quantization.brevitas_layers import calculate_model_size_mb


class TestQuantizationUtils(unittest.TestCase):
    def test_model_size_uniform_int8(self):
        """Verifies uniform INT8 model size calculation."""
        precisions = {f"conv{i}": 8 for i in range(6)}
        precisions.update({"fc0": 8, "fc1": 8})
        params, size_mb = calculate_model_size_mb(None, precisions)
        self.assertEqual(params, 3246794)
        # 3,246,794 bytes / (1024*1024) ≈ 3.096 MB
        self.assertAlmostEqual(size_mb, 3.0964, places=2)

    def test_model_size_uniform_int4(self):
        """Verifies uniform INT4 model size calculation (exactly half of INT8)."""
        precisions_8 = {f"conv{i}": 8 for i in range(6)}
        precisions_8.update({"fc0": 8, "fc1": 8})
        _, size_8 = calculate_model_size_mb(None, precisions_8)

        precisions_4 = {f"conv{i}": 4 for i in range(6)}
        precisions_4.update({"fc0": 4, "fc1": 4})
        _, size_4 = calculate_model_size_mb(None, precisions_4)

        self.assertAlmostEqual(size_4, size_8 / 2.0, places=3)


if __name__ == "__main__":
    unittest.main()
