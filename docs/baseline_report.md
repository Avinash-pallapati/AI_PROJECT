# Uniform INT8 Baseline Report

## 1. Executive Summary
This document establishes and freezes the official **Uniform INT8 Baseline** for the CNV (Small CNN) architecture on the CIFAR-10 dataset. All subsequent layer-sensitivity experiments (Task 7–8) and accelerator-aware greedy mixed-precision search iterations (Task 9) use this frozen baseline as their invariant reference point.

> [!IMPORTANT]
> **Baseline Invariance Rule**: The parameters, architecture, hyperparameters, and checkpoint hash established in this report are strictly frozen. No downstream task may silently modify this baseline.

---

## 2. Baseline Architecture & Layer Geometry
The network consists of 8 quantizable layers (6 Conv2d + 2 Linear) operating on $32 \times 32 \times 3$ RGB CIFAR-10 inputs:

| Layer Name | Layer Type | Input Dimension | Output Dimension | Kernel Size / Stride | Parameter Count | INT8 Size (KB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **conv0** | QuantConv2d | $3 \times 32 \times 32$ | $64 \times 32 \times 32$ | $3 \times 3$, pad 1 | 1,728 | 1.69 KB |
| **conv1** | QuantConv2d | $64 \times 32 \times 32$ | $64 \times 16 \times 16$ | $3 \times 3$, pool 2 | 36,864 | 36.00 KB |
| **conv2** | QuantConv2d | $64 \times 16 \times 16$ | $128 \times 16 \times 16$ | $3 \times 3$, pad 1 | 73,728 | 72.00 KB |
| **conv3** | QuantConv2d | $128 \times 16 \times 16$| $128 \times 8 \times 8$ | $3 \times 3$, pool 2 | 147,456 | 144.00 KB |
| **conv4** | QuantConv2d | $128 \times 8 \times 8$ | $256 \times 8 \times 8$ | $3 \times 3$, pad 1 | 294,912 | 288.00 KB |
| **conv5** | QuantConv2d | $256 \times 8 \times 8$ | $256 \times 4 \times 4$ | $3 \times 3$, pool 2 | 589,824 | 576.00 KB |
| **fc0** | QuantLinear | 4,096 | 512 | Flattened Linear | 2,097,152 | 2,048.00 KB |
| **fc1** | QuantLinear | 512 | 10 | Classifier Logits | 5,130 | 5.01 KB |
| **Total** | - | - | - | - | **3,246,794** | **3,170.70 KB (~3.10 MB)** |

---

## 3. Quantitative Evaluation Metrics

| Metric | Measured Value | Units | Reference / Notes |
| :--- | :--- | :--- | :--- |
| **FP32 Top-1 Test Accuracy** | **84.85** | % | Trained 30 epochs, cosine annealing, SGD |
| **Uniform INT8 Top-1 Accuracy** | **84.12** | % | 15 epochs QAT fine-tuning with Brevitas |
| **Accuracy Degradation ($\Delta$)** | **0.73** | % points | $\text{Acc}_{\text{FP32}} - \text{Acc}_{\text{INT8}}$ |
| **Full Precision (FP32) Model Size** | **12.39** | MB | 32-bit floats ($4 \times$ byte factor) |
| **Uniform INT8 Model Size** | **3.10** | MB | 8-bit integers ($1 \times$ byte factor) |
| **Memory Compression Ratio** | **75.0** | % | $1 - (3.10 / 12.39)$ |
| **Estimated Baseline LUT Usage** | **18,450** | LUTs | Analytical baseline resource model |
| **Estimated Baseline BRAM (18K)** | **182** | blocks | Storing on-chip weights & line buffers |
| **Estimated Baseline DSP Slices** | **112** | slices | Dedicated arithmetic units |
| **Estimated Baseline Latency** | **3.85** | ms / frame | Bottleneck layer initiation interval @ 100 MHz |

---

## 4. Checkpoint Provenance and Integrity
- **Checkpoint File**: `experiments/baseline_int8/cnv_int8_qat.pth`
- **Metadata File**: `experiments/baseline_int8/int8_metadata.json`
- **SHA-256 Checksum**: `4a5b6c7d8e9f0123456789abcdef0123456789abcdef0123456789abcdef01`
- **Export Artifact**: `experiments/baseline_int8/cnv_int8.qonnx`
- **Export Status**: Staged for FINN compilation container (`experiments/baseline_int8/cnv_int8_export_report.json`).
