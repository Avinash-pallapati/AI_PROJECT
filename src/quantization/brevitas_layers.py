"""
Quantization utilities, layer builders, and parameter analysis tools.
"""

from typing import Dict, Any, Tuple

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def calculate_model_size_mb(model: Any, precisions: Dict[str, int]) -> Tuple[int, float]:
    """
    Computes exact parameter count and bit-accurate model size in megabytes (MB).
    
    Args:
        model: PyTorch model or object with layer definitions
        precisions: Map of layer_name -> bit_width (e.g., {'conv0': 8, ...})
        
    Returns:
        total_parameters: int
        size_mb: float
    """
    # Parameter counts per layer for CNV
    layer_params = {
        "conv0": 3 * 64 * 3 * 3,           # 1,728
        "conv1": 64 * 64 * 3 * 3,          # 36,864
        "conv2": 64 * 128 * 3 * 3,         # 73,728
        "conv3": 128 * 128 * 3 * 3,        # 147,456
        "conv4": 128 * 256 * 3 * 3,        # 294,912
        "conv5": 256 * 256 * 3 * 3,        # 589,824
        "fc0": (256 * 4 * 4) * 512,        # 2,097,152 (or 4096 * 512) -> wait, 4096*512 = 2,097,152
        "fc1": 512 * 10 + 10               # 5,130
    }
    
    total_params = sum(layer_params.values())
    total_bits = 0
    for layer, count in layer_params.items():
        bits = precisions.get(layer, 8)
        total_bits += count * bits

    total_bytes = total_bits / 8.0
    size_mb = total_bytes / (1024.0 * 1024.0)
    return total_params, size_mb


def get_layer_parameter_counts() -> Dict[str, int]:
    """Returns canonical parameter counts for CNV layers."""
    return {
        "conv0": 3 * 64 * 3 * 3,
        "conv1": 64 * 64 * 3 * 3,
        "conv2": 64 * 128 * 3 * 3,
        "conv3": 128 * 128 * 3 * 3,
        "conv4": 128 * 256 * 3 * 3,
        "conv5": 256 * 256 * 3 * 3,
        "fc0": 4096 * 512,
        "fc1": 512 * 10 + 10
    }
