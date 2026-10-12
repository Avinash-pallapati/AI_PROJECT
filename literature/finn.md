# FINN: Framework for Quantized Neural Network Acceleration on FPGAs

## 1. Overview and Lineage
- **Key Papers**:
  - *FINN: A Framework for Fast, Scalable Binarized Neural Network Inference* (Umuroglu et al., FPGA 2017)
  - *FINN-R: An End-to-End Deep Learning Framework for Fast Exploration of Quantized Neural Networks* (Blott et al., ACM TRETS 2018)
- **Primary Goal**: Automatically compile trained Quantized Neural Networks (QNNs) into fully streaming, line-rate FPGA dataflow accelerators.

---

## 2. FINN Architectural Flow and Core Concepts
1. **Compilation Pipeline**:
   ```
   PyTorch / Brevitas QNN
         ↓ (Brevitas export)
   QONNX / FINN-ONNX Intermediate Representation
         ↓ (Streamlining & Tidy-up transformations)
   HLS-Ready Custom Hardware Layers
         ↓ (Folding & Parallelism Allocation: SIMD, PE)
   Vivado HLS C++ IP Generation
         ↓ (Vivado IPI Stitching & Synthesis)
   Deployable FPGA Bitstream
   ```
2. **Streaming Dataflow Paradigm**:
   - Each neural network layer maps to a dedicated hardware processing block (e.g., Matrix-Vector-Threshold Unit, MVTU).
   - Layers communicate via point-to-point AXI Stream FIFOs, eliminating off-chip DRAM memory bottleneck during inference.
3. **Folding Parameters (Parallelism Tuning)**:
   - **SIMD (Single Instruction Multiple Data)**: Number of input channels processed in parallel.
   - **PE (Processing Elements)**: Number of output channels / matrix rows computed in parallel.
   - Bit-width directly dictates the hardware footprint of the MVTU arithmetic cores (XNOR gates for 1-bit, LUT-based multipliers for 2-4 bits, DSP slices for 8-bit+).
4. **Analytical Cost and Resource Estimation**:
   - FINN contains analytical estimation models calculating expected LUTs, BRAMs, and DSPs from layer geometry, folding factors, and bit-widths.
   - Latency is determined by the maximum layer latency (bottleneck layer): $\text{Cycles} = \max_l \left( \frac{\text{Cycles}_l}{\text{Layer } l} \right)$.

---

## 3. Comparison with Our Approach

| Dimension | FINN Framework | Our Project Adaptation |
| :--- | :--- | :--- |
| **Primary Scope** | QNN-to-FPGA compiler and streaming IP generator | Mixed-precision search engine tailored to a custom accelerator (**QCore-INT8**) |
| **Precision Decision** | Statically fixed prior to compilation by developer | Dynamically explored by accelerator-aware greedy search |
| **Cost Estimation** | Used for post-hoc validation or manual folding tuning | Integrated directly into the automated optimization loop to accept/reject precision steps |
| **Hardware Architecture**| Heterogeneous streaming dataflow pipeline per network | QCore-INT8 custom accelerator architecture |

---

## 4. Scope and Research Lineage

```
EXISTING WORK
  - FINN compiler, streaming dataflow architectures, and QONNX intermediate representation.
  - Brevitas-to-FINN export pathway.
        ↓
OUR ADAPTATION
  - Leverage FPGA resource estimation principles (LUT, BRAM, DSP, latency scaling with precision).
  - Embed hardware estimation directly into the greedy precision search loop.
  - Target our custom QCore-INT8 accelerator constraints.
        ↓
OUR EXPERIMENTAL VALIDATION
  - Verify Brevitas exportability.
  - Compare search-predicted resource reductions against baseline requirements.
```
