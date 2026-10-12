"""
Quantized and FP32 model definitions for CNV on CIFAR-10.
"""

from typing import Dict, Optional, Tuple

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    class nn:
        class Module:
            pass

try:
    import brevitas.nn as qnn
    from brevitas.quant import Int8WeightPerTensorFloat, Int8ActPerTensorFloat
    BREVITAS_AVAILABLE = True
except ImportError:
    BREVITAS_AVAILABLE = False


class CNV_FP32(nn.Module if TORCH_AVAILABLE else object):
    """
    Standard Full-Precision (FP32) CNV Network for CIFAR-10.
    Consists of 6 Convolutional layers and 2 Fully-Connected layers.
    """
    def __init__(self, num_classes: int = 10):
        if not TORCH_AVAILABLE:
            self.num_classes = num_classes
            return
        super().__init__()
        self.num_classes = num_classes

        # Feature extractor
        self.conv0 = nn.Conv2d(3, 64, kernel_size=3, padding=1, bias=False)
        self.bn0 = nn.BatchNorm2d(64)
        self.relu0 = nn.ReLU(inplace=True)

        self.conv1 = nn.Conv2d(64, 64, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu1 = nn.ReLU(inplace=True)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(128)
        self.relu2 = nn.ReLU(inplace=True)

        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1, bias=False)
        self.bn3 = nn.BatchNorm2d(128)
        self.relu3 = nn.ReLU(inplace=True)
        self.pool3 = nn.MaxPool2d(2, 2)

        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1, bias=False)
        self.bn4 = nn.BatchNorm2d(256)
        self.relu4 = nn.ReLU(inplace=True)

        self.conv5 = nn.Conv2d(256, 256, kernel_size=3, padding=1, bias=False)
        self.bn5 = nn.BatchNorm2d(256)
        self.relu5 = nn.ReLU(inplace=True)
        self.pool5 = nn.MaxPool2d(2, 2)

        # Classifier
        self.fc0 = nn.Linear(256 * 4 * 4, 512, bias=False)
        self.bn_fc0 = nn.BatchNorm1d(512)
        self.relu_fc0 = nn.ReLU(inplace=True)

        self.fc1 = nn.Linear(512, num_classes, bias=True)

    def forward(self, x):
        x = self.relu0(self.bn0(self.conv0(x)))
        x = self.pool1(self.relu1(self.bn1(self.conv1(x))))

        x = self.relu2(self.bn2(self.conv2(x)))
        x = self.pool3(self.relu3(self.bn3(self.conv3(x))))

        x = self.relu4(self.bn4(self.conv4(x)))
        x = self.pool5(self.relu5(self.bn5(self.conv5(x))))

        x = x.view(x.size(0), -1)
        x = self.relu_fc0(self.bn_fc0(self.fc0(x)))
        x = self.fc1(x)
        return x


class CNV_Quantized(nn.Module if TORCH_AVAILABLE else object):
    """
    Quantized CNV Model with configurable per-layer bit-widths.
    Uses Brevitas quantized layers if available.
    """
    QUANTIZABLE_LAYERS = ["conv0", "conv1", "conv2", "conv3", "conv4", "conv5", "fc0", "fc1"]

    def __init__(self, precisions: Optional[Dict[str, int]] = None, num_classes: int = 10):
        if not TORCH_AVAILABLE:
            self.precisions = precisions or {layer: 8 for layer in self.QUANTIZABLE_LAYERS}
            self.num_classes = num_classes
            return
        super().__init__()
        self.num_classes = num_classes
        
        # Default all layers to INT8 if not specified
        self.precisions = {layer: 8 for layer in self.QUANTIZABLE_LAYERS}
        if precisions:
            self.precisions.update(precisions)

        if BREVITAS_AVAILABLE:
            self._init_brevitas_layers()
        else:
            self._init_simulated_layers()

    def _init_brevitas_layers(self):
        # Input quantization
        self.quant_input = qnn.QuantIdentity(bit_width=8, return_quant_tensor=True)

        # Conv 0
        w_b0 = self.precisions["conv0"]
        self.conv0 = qnn.QuantConv2d(3, 64, kernel_size=3, padding=1, bias=False, weight_bit_width=w_b0)
        self.bn0 = nn.BatchNorm2d(64)
        self.relu0 = qnn.QuantReLU(bit_width=w_b0, return_quant_tensor=True)

        # Conv 1
        w_b1 = self.precisions["conv1"]
        self.conv1 = qnn.QuantConv2d(64, 64, kernel_size=3, padding=1, bias=False, weight_bit_width=w_b1)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu1 = qnn.QuantReLU(bit_width=w_b1, return_quant_tensor=True)
        self.pool1 = nn.MaxPool2d(2, 2)

        # Conv 2
        w_b2 = self.precisions["conv2"]
        self.conv2 = qnn.QuantConv2d(64, 128, kernel_size=3, padding=1, bias=False, weight_bit_width=w_b2)
        self.bn2 = nn.BatchNorm2d(128)
        self.relu2 = qnn.QuantReLU(bit_width=w_b2, return_quant_tensor=True)

        # Conv 3
        w_b3 = self.precisions["conv3"]
        self.conv3 = qnn.QuantConv2d(128, 128, kernel_size=3, padding=1, bias=False, weight_bit_width=w_b3)
        self.bn3 = nn.BatchNorm2d(128)
        self.relu3 = qnn.QuantReLU(bit_width=w_b3, return_quant_tensor=True)
        self.pool3 = nn.MaxPool2d(2, 2)

        # Conv 4
        w_b4 = self.precisions["conv4"]
        self.conv4 = qnn.QuantConv2d(128, 256, kernel_size=3, padding=1, bias=False, weight_bit_width=w_b4)
        self.bn4 = nn.BatchNorm2d(256)
        self.relu4 = qnn.QuantReLU(bit_width=w_b4, return_quant_tensor=True)

        # Conv 5
        w_b5 = self.precisions["conv5"]
        self.conv5 = qnn.QuantConv2d(256, 256, kernel_size=3, padding=1, bias=False, weight_bit_width=w_b5)
        self.bn5 = nn.BatchNorm2d(256)
        self.relu5 = qnn.QuantReLU(bit_width=w_b5, return_quant_tensor=True)
        self.pool5 = nn.MaxPool2d(2, 2)

        # FC 0
        w_bfc0 = self.precisions["fc0"]
        self.fc0 = qnn.QuantLinear(256 * 4 * 4, 512, bias=False, weight_bit_width=w_bfc0)
        self.bn_fc0 = nn.BatchNorm1d(512)
        self.relu_fc0 = qnn.QuantReLU(bit_width=w_bfc0, return_quant_tensor=True)

        # FC 1
        w_bfc1 = self.precisions["fc1"]
        self.fc1 = qnn.QuantLinear(512, self.num_classes, bias=True, weight_bit_width=w_bfc1)

    def _init_simulated_layers(self):
        # Fallback simulated model when Brevitas is not installed
        self.conv0 = nn.Conv2d(3, 64, kernel_size=3, padding=1, bias=False)
        self.bn0 = nn.BatchNorm2d(64)
        self.relu0 = nn.ReLU(inplace=True)

        self.conv1 = nn.Conv2d(64, 64, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu1 = nn.ReLU(inplace=True)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(128)
        self.relu2 = nn.ReLU(inplace=True)

        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1, bias=False)
        self.bn3 = nn.BatchNorm2d(128)
        self.relu3 = nn.ReLU(inplace=True)
        self.pool3 = nn.MaxPool2d(2, 2)

        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1, bias=False)
        self.bn4 = nn.BatchNorm2d(256)
        self.relu4 = nn.ReLU(inplace=True)

        self.conv5 = nn.Conv2d(256, 256, kernel_size=3, padding=1, bias=False)
        self.bn5 = nn.BatchNorm2d(256)
        self.relu5 = nn.ReLU(inplace=True)
        self.pool5 = nn.MaxPool2d(2, 2)

        self.fc0 = nn.Linear(256 * 4 * 4, 512, bias=False)
        self.bn_fc0 = nn.BatchNorm1d(512)
        self.relu_fc0 = nn.ReLU(inplace=True)

        self.fc1 = nn.Linear(512, self.num_classes, bias=True)

    def forward(self, x):
        if BREVITAS_AVAILABLE and hasattr(self, 'quant_input'):
            x = self.quant_input(x)
        x = self.relu0(self.bn0(self.conv0(x)))
        x = self.pool1(self.relu1(self.bn1(self.conv1(x))))

        x = self.relu2(self.bn2(self.conv2(x)))
        x = self.pool3(self.relu3(self.bn3(self.conv3(x))))

        x = self.relu4(self.bn4(self.conv4(x)))
        x = self.pool5(self.relu5(self.bn5(self.conv5(x))))

        x = x.view(x.size(0), -1)
        x = self.relu_fc0(self.bn_fc0(self.fc0(x)))
        x = self.fc1(x)
        return x

    def set_layer_precision(self, layer_name: str, bit_width: int):
        """Update precision for a specific layer."""
        if layer_name not in self.QUANTIZABLE_LAYERS:
            raise ValueError(f"Unknown layer: {layer_name}. Must be in {self.QUANTIZABLE_LAYERS}")
        self.precisions[layer_name] = bit_width
        layer = getattr(self, layer_name, None)
        if layer and hasattr(layer, 'change_weight_bit_width'):
            layer.change_weight_bit_width(bit_width)
