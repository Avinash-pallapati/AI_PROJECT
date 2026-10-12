"""
Unit tests for CNV model architecture and layer structure.
"""

import unittest
from src.models.cnv import CNV_Quantized
from src.quantization.brevitas_layers import get_layer_parameter_counts


class TestModelArchitecture(unittest.TestCase):
    def test_quantizable_layers_count(self):
        """Verifies that the CNV model has exactly 8 quantizable layers."""
        layers = CNV_Quantized.QUANTIZABLE_LAYERS
        self.assertEqual(len(layers), 8)
        self.assertIn("conv0", layers)
        self.assertIn("fc1", layers)

    def test_layer_parameter_counts(self):
        """Verifies accurate layer parameter calculations."""
        params = get_layer_parameter_counts()
        self.assertEqual(params["conv0"], 3 * 64 * 3 * 3)  # 1728
        self.assertEqual(params["conv1"], 64 * 64 * 3 * 3) # 36864
        self.assertEqual(params["fc0"], 4096 * 512)        # 2097152
        self.assertEqual(params["fc1"], 512 * 10 + 10)     # 5130
        self.assertEqual(sum(params.values()), 3246794)

    def test_set_layer_precision(self):
        """Verifies updating precision dictionary on model instance."""
        model = CNV_Quantized()
        self.assertEqual(model.precisions["conv3"], 8)
        model.set_layer_precision("conv3", 4)
        self.assertEqual(model.precisions["conv3"], 4)

        with self.assertRaises(ValueError):
            model.set_layer_precision("invalid_layer", 4)


if __name__ == "__main__":
    unittest.main()
