# Hardware-Aware AI Acceleration & FPGA Resource-Aware Optimization

## 1. FPGA Hardware Fabric Realities
Deploying Deep Neural Networks (DNNs) on Field-Programmable Gate Arrays (FPGAs) requires balancing four discrete, heterogeneous hardware resource categories:

1. **Look-Up Tables (LUTs)**:
   - Primary reconfigurable combinational logic cells (e.g., 6-input LUTs in modern AMD/Xilinx FPGAs).
   - In low-bit arithmetic (e.g., INT4 or INT2), multiplications can be synthesized entirely into LUT logic instead of consuming dedicated DSP slices.
   - Also utilized for multiplexing, activation thresholding, and distributed RAM (LUTRAM).
2. **Flip-Flops (FFs)**:
   - Synchronous register storage used for deep pipelining to maintain high clock frequencies (e.g., 100–300 MHz).
3. **Block RAMs (BRAMs / URAMs)**:
   - Embedded dual-port SRAM blocks (typically 18Kb or 36Kb per BRAM block).
   - Constrained resource used for buffering layer parameters (weights) and intermediate feature maps (activations) on-chip.
   - Reducing precision from INT8 to INT4 immediately halves BRAM footprint for weight storage, often allowing entire layers to reside on-chip without DRAM thrashing.
4. **DSP Slices (DSP48E1 / DSP48E2)**:
   - Dedicated hardwired arithmetic blocks featuring $25 \times 18$ or $27 \times 18$ multipliers and 48-bit accumulators.
   - An 8-bit $\times$ 8-bit multiplier comfortably consumes 1 DSP slice.
   - DSP availability is strictly limited on mid-range FPGAs (e.g., Zynq-7020 has 220 DSPs). Excessive reliance on INT8 exhausts DSP budgets rapidly.

---

## 2. Latency, Throughput, and Architectural Constraints
- **Initiation Interval ($II$)**: The number of clock cycles between consecutive inputs. For a balanced streaming pipeline, $II = \max_l (II_l)$.
- **PE Parallelism & Tiling**:
  - Processing Elements (PEs) compute matrix tiles.
  - Tiling decisions determine on-chip buffer requirements and memory transfer latency.
- **Dataflow Patterns**:
  - **Weight Stationary**: Weights are held in PE local registers; activations stream through.
  - **Output Stationary**: Partial sums accumulate locally; weights and inputs stream.

---

## 3. Cost Scaling with Bit-Width on FPGAs

| Precision Level | Relative Memory Footprint | Multiplier Implementation | DSP Consumption | LUT Consumption |
| :--- | :--- | :--- | :--- | :--- |
| **FP32** | $4.0\times$ (relative to INT8) | Multi-DSP floating point | High (~2-4 DSPs/MAC) | High |
| **INT8** | $1.0\times$ (Baseline) | Standard fixed-point MAC | 1 DSP / MAC | Low |
| **INT4** | $0.5\times$ (50% reduction) | Packed DSP or Pure LUT logic | $\le 0.5$ DSP / MAC | Moderate (~16 LUTs/MAC) |
| **INT2** | $0.25\times$ (75% reduction) | Pure LUT / Shift-Add logic | 0 DSP | Minimal (~4 LUTs/MAC) |

---

## 4. Scope and Research Lineage

```
EXISTING WORK
  - FPGA accelerator architectures (Eyeriss, DLA, FINN dataflow, systolic arrays).
  - General understanding of FPGA LUT/DSP trade-offs.
        ↓
OUR ADAPTATION
  - Formulate multi-dimensional resource constraint checks (LUT, BRAM, DSP, FF, Latency).
  - Couple these checks directly into the greedy search decision criteria for the custom QCore-INT8 architecture.
        ↓
OUR EXPERIMENTAL VALIDATION
  - Evaluate resource reduction percentages and Pareto efficiency against the uniform INT8 baseline.
  - Provide an auditable candidate selection log demonstrating constraint compliance at every iteration.
```
