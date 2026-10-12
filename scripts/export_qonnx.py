#!/usr/bin/env python3
"""
Export Brevitas Quantized Model to QONNX representation.
"""

import os
import sys
import json
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.cnv import CNV_Quantized

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import brevitas
    from brevitas.export import export_qonnx
    BREVITAS_EXPORT_AVAILABLE = True
except ImportError:
    BREVITAS_EXPORT_AVAILABLE = False


def export_model_to_qonnx(
    checkpoint_path: str = "./experiments/baseline_int8/cnv_int8_qat.pth",
    output_path: str = "./experiments/baseline_int8/cnv_int8.qonnx"
):
    print("==================================================")
    print("EXPORTING QUANTIZED MODEL TO QONNX")
    print("==================================================")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report_path = output_path.replace(".qonnx", "_export_report.json")

    status = {
        "export_attempted": True,
        "brevitas_available": BREVITAS_EXPORT_AVAILABLE,
        "torch_available": TORCH_AVAILABLE,
        "success": False,
        "reason": "",
        "target_file": output_path
    }

    if TORCH_AVAILABLE and BREVITAS_EXPORT_AVAILABLE:
        try:
            model = CNV_Quantized(precisions={layer: 8 for layer in CNV_Quantized.QUANTIZABLE_LAYERS})
            if os.path.exists(checkpoint_path) and checkpoint_path.endswith(".pth"):
                model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"), strict=False)
            dummy_input = torch.randn(1, 3, 32, 32)
            export_qonnx(model, input_t=dummy_input, export_path=output_path)
            status["success"] = True
            status["reason"] = "Successfully exported QONNX graph via Brevitas manager."
            print(f"Export successful: {output_path}")
        except Exception as e:
            status["success"] = False
            status["reason"] = f"Export failed with exception: {str(e)}"
            print(f"Export error: {e}")
    else:
        status["success"] = False
        missing = []
        if not TORCH_AVAILABLE:
            missing.append("PyTorch")
        if not BREVITAS_EXPORT_AVAILABLE:
            missing.append("Brevitas/QONNX")
        status["reason"] = f"Host runtime missing: {', '.join(missing)}. QONNX export will be performed inside FINN Docker container."
        # Create placeholder artifact
        with open(output_path, "w") as f:
            f.write("# QONNX Graph Placeholder for FINN flow\n")
        print(status["reason"])

    with open(report_path, "w") as f:
        json.dump(status, f, indent=2)

    print(f"Export report written to: {report_path}")
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, default="./experiments/baseline_int8/cnv_int8_qat.pth")
    parser.add_argument("--output", type=str, default="./experiments/baseline_int8/cnv_int8.qonnx")
    args = parser.parse_args()

    export_model_to_qonnx(checkpoint_path=args.checkpoint, output_path=args.output)
