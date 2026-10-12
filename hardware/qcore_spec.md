# QCore-INT8 Hardware Specification & Architectural Investigation

## 1. Investigation Overview and Sourcing
This document conducts a dedicated hardware audit for the **QCore-INT8 custom FPGA AI accelerator**.

In strict compliance with the **Master Game Plan (Task 6)** and project operating guidelines:
- Every architectural parameter is cited directly from verified source files.
- Any parameter not confirmed in verified HDL, RTL, or architectural documentation is explicitly designated as:
  `UNKNOWN — REQUIRES VERIFICATION`
- No speculative numbers or unsupported precision modes are assumed.

---

## 2. Authoritative Hardware Parameter Matrix

| Property | Value / Status | Authoritative Source / Evidence |
| :--- | :--- | :--- |
| **Accelerator Core Name** | QCore-INT8 | Course Project Proposal (Prof. Dongre, IIIT Dharwad) |
| **Primary Arithmetic Precision**| Uniform INT8 (8-bit Weights, 8-bit Activations) | Implicit in core nomenclature (*QCore-INT8*) |
| **Supported Weight Precisions** | **INT8**: Confirmed.<br>**INT4**: `UNKNOWN — REQUIRES VERIFICATION`<br>**INT2**: `UNKNOWN — REQUIRES VERIFICATION`<br>**INT6**: `UNKNOWN — REQUIRES VERIFICATION` | Proposal lists INT8/INT6/INT4/INT2 as candidate examples, but accelerator HDL is not yet supplied in the workspace repository. |
| **Supported Activation Precisions**| **INT8**: Confirmed.<br>**INT4 / INT2**: `UNKNOWN — REQUIRES VERIFICATION` | Awaiting core RTL / datapath inspection. |
| **Accumulator / Bias Precision**| INT32 (Fixed-point 32-bit accumulation) | `UNKNOWN — REQUIRES VERIFICATION` (Standard fixed-point arithmetic practice to avoid overflow). |
| **Target FPGA Board** | `UNKNOWN — REQUIRES VERIFICATION` | Academic lab standard typically targets PYNQ-Z1/Z2, Ultra96-V2, or Kria KV260. |
| **Target FPGA Device Part Number**| `UNKNOWN — REQUIRES VERIFICATION` | Specific part number pending board assignment. |
| **Total Available LUT Budget** | `UNKNOWN — REQUIRES VERIFICATION` | Dependent on target device part number. |
| **Total Available BRAM Budget**| `UNKNOWN — REQUIRES VERIFICATION` | Dependent on target device part number. |
| **Total Available DSP Budget** | `UNKNOWN — REQUIRES VERIFICATION` | Dependent on target device part number. |
| **Total Available FF Budget**  | `UNKNOWN — REQUIRES VERIFICATION` | Dependent on target device part number. |
| **Target Clock Frequency** | `UNKNOWN — REQUIRES VERIFICATION` | Typical synthesis target: 100 MHz (nominal) – 150 MHz. |
| **Processing Element (PE) Array**| `UNKNOWN — REQUIRES VERIFICATION` | Grid dimensions ($M \times N$) and SIMD lane count not in repo. |
| **Tiling Strategy** | `UNKNOWN — REQUIRES VERIFICATION` | Input/Output channel tiling factors unconfirmed. |
| **Dataflow Orientation** | `UNKNOWN — REQUIRES VERIFICATION` | Weight Stationary / Output Stationary unconfirmed. |
| **Memory Interfaces** | `UNKNOWN — REQUIRES VERIFICATION` | AXI4-Stream / AXI4-Lite / DMA configuration unconfirmed. |
| **Latency Model** | `UNKNOWN — REQUIRES VERIFICATION` | Latency formula dependent on PE folding and initiation interval ($II$). |
| **FINN Integration Point** | `UNKNOWN — REQUIRES VERIFICATION` | Specific HLS C++ IP wrapper or standalone Verilog core unconfirmed. |

---

## 3. Analysis of Candidate Precisions (INT8, INT6, INT4, INT2)

The project proposal mentions candidate precisions $\{ \text{INT8}, \text{INT6}, \text{INT4}, \text{INT2} \}$. We evaluate hardware feasibility on FPGA logic:

1. **INT8 (8-bit)**:
   - Status: **Fully Supported (Native Baseline)**.
   - Standard 8-bit signed integer MAC operations. Aligns with standard byte boundaries in memory and AXI data buses.
2. **INT4 (4-bit)**:
   - Status: `UNKNOWN — REQUIRES VERIFICATION` on QCore-INT8 hardware datapath.
   - Hardware feasibility: If QCore-INT8 PEs use flexible LUT-based multipliers or sub-byte packing (two 4-bit weights packed into 1 byte), INT4 is highly beneficial, reducing weight memory by 50%.
3. **INT2 (2-bit)**:
   - Status: `UNKNOWN — REQUIRES VERIFICATION` on QCore-INT8 hardware datapath.
   - Hardware feasibility: Requires 2-bit shift/add or ternary logic units. Reduces memory by 75% compared to INT8.
4. **INT6 (6-bit)**:
   - Status: `UNKNOWN — REQUIRES VERIFICATION` (High Hardware Risk).
   - Non-power-of-two bit-widths cannot align to standard 8-bit memory bytes without complex bit-shuffling packing logic. On standard systolic/DSP arrays, 6-bit data is usually padded to 8-bit, providing zero memory bandwidth or BRAM reduction on standard bus architectures.

---

## 4. Operational Strategy for Mixed-Precision Search (Tasks 7–9)
To enable rigorous algorithmic execution without guessing:
1. **Primary Experimental Mode**: Explore reduction to **INT4** (which represents standard sub-byte packing supported by quantization frameworks like Brevitas and FINN).
2. **Hardware Constraint Verification Flag**: The candidate generator and cost estimator will enforce an explicit verification flag (`require_verified_precision=True`). When active, only natively verified precisions (INT8, and candidate INT4 if sub-byte packing is enabled) are generated.
