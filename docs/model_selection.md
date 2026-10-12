# Model Selection and Dataset Evaluation Report

## 1. Objective and Evaluation Criteria
In accordance with **Task 3 (Dataset and Model Selection)** of the Master Game Plan, we evaluate candidate Convolutional Neural Network (CNN) architectures on CIFAR-10 against six critical engineering and research criteria:
1. **Training Runtime & Convergence Speed**: Can the model train and fine-tune rapidly on commodity compute without days of GPU overhead?
2. **Brevitas Quantization Compatibility**: Can every parameter and activation layer be cleanly mapped to Brevitas primitives (`QuantConv2d`, `QuantIdentity`, `QuantReLU`, `QuantLinear`)?
3. **FINN-ONNX & QONNX Export Feasibility**: Is the network topology directly exportable to QONNX without unsupported graph transformation nodes?
4. **FPGA Resource Fit (QCore-INT8 Target)**: Can the model weights and feature maps fit within mid-range FPGA on-chip Block RAM (BRAM) without requiring off-chip DRAM streaming bottlenecks?
5. **Architectural Complexity**: Does the architecture avoid complex graph branches (e.g., residual connections or depthwise separable patterns) that complicate hardware synchronization?
6. **Mixed-Precision Demonstration Fidelity**: Does the architecture have sufficient layers ($N \ge 6$) and parameter diversity to clearly demonstrate per-layer sensitivity variance and multi-bit tradeoffs?

---

## 2. Comparative Matrix of Candidate Architectures

| Evaluation Criterion | ResNet-18 | MobileNetV2 | CNV (Small CNN - VGG style) |
| :--- | :--- | :--- | :--- |
| **Parameters** | ~11.17 Million | ~2.23 Million | ~1.54 Million |
| **CIFAR-10 Top-1 FP32 Accuracy** | 93.0% – 95.0% | 90.0% – 92.5% | 82.0% – 86.5% |
| **MAC Operations (per frame)** | ~556 MFLOPs | ~90 MFLOPs | ~58 MFLOPs |
| **Graph Topology** | Residual skip connections (additions) | Inverted residuals + Depthwise Separable | Pure feedforward sequential (VGG-like) |
| **Brevitas & QONNX Compatibility** | Requires residual branch scaling | High sensitivity in depthwise layers | **Native reference model in Brevitas & FINN** |
| **FINN Streaming Compatibility** | High FIFO buffering overhead to balance branch latencies | Depthwise convolutions require non-standard sliding window units | **100% native support in FINN compiler** |
| **FPGA On-Chip BRAM Fit** | Fails: 11.2 MB weights exceeds on-chip BRAM of Zynq-7000/UltraScale+ | Marginal: Requires ~2.2 MB on-chip memory | **Passes: Fits easily inside on-chip BRAM (1.5 MB in INT8, 0.77 MB in INT4)** |
| **Training / Fine-Tuning Speed** | Moderate (~30-60 min CPU/GPU) | Moderate-Slow (requires careful schedule) | **Fast (<15 min on standard compute)** |
| **Mixed-Precision Search Space** | $4^{18} \approx 6.87 \times 10^{10}$ | $4^{53} \approx 10^{31}$ | **$4^8 = 65,536$ (8 quantizable layers)** |

---

## 3. Deep Analysis of Candidates

### Candidate A: ResNet-18
- *Strengths*: High classification accuracy on CIFAR-10 (~94%), standard academic benchmark.
- *Fatal Flaws for Custom FPGA*:
  1. Residual add branches require cycle-accurate FIFO delay matching on hardware dataflows.
  2. With 11.2 million parameters, storing INT8 weights requires 11.2 MB. A standard FPGA like the Zynq-7020 has only 4.9 Mb (~612 KB) of BRAM; even a larger ZCU102 board has 32.1 Mb (~4 MB) of BRAM. ResNet-18 cannot fit entirely on-chip, forcing external DDR memory interfaces that obscure core per-layer arithmetic tradeoffs.

### Candidate B: MobileNetV2
- *Strengths*: Highly parameter-efficient.
- *Fatal Flaws for Custom FPGA*:
  1. Depthwise separable convolutions isolate $3 \times 3$ kernels per channel (only 9 parameters per filter). Under 4-bit or 2-bit quantization, depthwise layers exhibit catastrophic representational collapse unless specialized per-channel scaling is implemented.
  2. FINN's streaming dataflow engine requires complex memory access patterns to implement depthwise sliding window units.

### Candidate C: CNV Small CNN (Selected Recommendation)
- *Strengths*:
  1. Established as the official canonical benchmark in both the FINN paper (Blott et al., 2018) and Brevitas repository for FPGA deployment.
  2. Pure sequential structure (6 convolutional layers + 2 fully-connected layers). Every layer has clean, standard $3 \times 3$ convolutions or dense projections.
  3. 1.54M parameters: at INT8, requires ~1.5 MB; at INT4, requires ~0.77 MB, allowing complete on-chip BRAM residency on mid-to-high capacity FPGAs.
  4. Search space of $4^8 = 65,536$ configurations allows comprehensive validation of greedy search, layer sensitivity, and hardware constraints without excessive simulation delays.

---

## 4. Human Approval Gate G1 Recommendation
We formally recommend **CNV (Small CNN)** as the primary model for Tasks 4–9. It satisfies all criteria of the Master Game Plan checklist, maximizes technical rigor, and prevents off-chip memory bottlenecks from masking the per-layer mixed-precision findings.
