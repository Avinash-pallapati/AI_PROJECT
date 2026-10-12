# HAQ: Hardware-Aware Automated Quantization

## 1. Paper Reference and Background
- **Title**: *HAQ: Hardware-Aware Automated Quantization with Mixed Precision*
- **Authors**: Kuan Wang, Zhijian Liu, Yujun Lin, Ji Lin, Song Han
- **Venue**: IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2019)
- **Primary Thesis**: Quantization policies are hardware-dependent. Conventional quantization optimizes for proxy metrics (such as model size or FLOPs), but latency and energy do not scale linearly with FLOPs across different hardware platforms (e.g., systolic arrays vs. SIMD CPUs vs. GPUs).

---

## 2. Methodology of HAQ
1. **Reinforcement Learning Formulation**:
   - Uses an actor-critic RL agent (Deep Deterministic Policy Gradient, DDPG).
   - The environment is the neural network and the target hardware.
   - For layer $t$, the state vector includes: layer index, input dimensions, kernel size, stride, number of channels, weight count, and current FLOPs.
   - The action $a_t$ determines the bit-width (weight bit $b_w$ and activation bit $b_a$).
2. **Hardware Feedback in the Loop**:
   - Direct measurement or cycle-accurate simulation (e.g., BitFusion simulator, Edge TPU, mobile CPU/GPU).
   - Measures actual execution latency and energy consumption.
3. **Reward Function**:
   - $R = -\text{Loss} \cdot \log(\text{Hardware Metric})$ or constrained reward penalizing latency/energy overshoots.

---

## 3. Comparison with Our Approach

| Dimension | HAQ (Wang et al. 2019) | Our Custom FPGA Project |
| :--- | :--- | :--- |
| **Search Strategy** | Reinforcement Learning (DDPG agent) | Accelerator-Aware Greedy Search guided by Layer Sensitivity |
| **Search Cost** | Hundreds of rollout episodes; high training overhead | Deterministic, iterative step-by-step reduction; efficient |
| **Hardware Target** | Mobile CPU/GPU, ASIC accelerator (BitFusion) | Custom FPGA AI Accelerator (**QCore-INT8**) |
| **Hardware Feedback** | Measured/simulated latency and energy | FPGA resources (LUT, BRAM, DSP, FF) + estimated/measured latency |
| **Constraint Handling**| Penalty term inside RL reward | Hard constraint validation (accuracy gate + resource budget gates) |
| **Explainability** | Black-box neural network policy | Fully auditable step-by-step candidate logs with explicit accept/reject reasons |

---

## 4. Scope and Research Lineage

```
EXISTING WORK
  - HAQ pioneered the concept that mixed-precision search must receive feedback from the target hardware.
        ↓
OUR ADAPTATION
  - Adopt the hardware-in-the-loop principle, but replace RL with an accelerator-aware greedy search.
  - Specialize the cost feedback to FPGA hardware primitives (LUTs, BRAMs, DSP slices, FFs) for QCore-INT8.
  - Employ pre-computed layer sensitivity ranking to prioritize candidate exploration.
        ↓
OUR EXPERIMENTAL VALIDATION
  - Execute greedy search with explicit constraint checking (accuracy drop <= threshold, resources <= budgets).
  - Produce an auditable trace of every candidate evaluated and selected.
```
