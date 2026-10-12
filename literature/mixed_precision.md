# Mixed-Precision Quantization

## 1. Concept and Motivation
Mixed-precision quantization assigns different bit-widths to different layers in a neural network rather than enforcing a uniform bit-width (e.g., all INT8) across the entire model.

### Sub-optimality of Uniform Precision
In uniform quantization:
- Setting bit-width high (e.g., INT8 across all layers) preserves accuracy but wastes hardware area, DSP blocks, and on-chip memory on layers that exhibit high redundancy.
- Setting bit-width low (e.g., uniform INT4 or INT2) reduces area and memory but often causes catastrophic accuracy loss because critical, sensitive layers cannot tolerate high quantization noise.

Mixed precision breaks this trade-off by allocating high bit-widths to sensitive layers and low bit-widths to robust, redundant layers.

---

## 2. Layer Sensitivity and Trade-Offs

### What Makes a Layer Sensitive?
1. **First Convolutional Layer**: Operates directly on continuous 3-channel input signals (RGB). Quantization error here distorts all downstream feature representations.
2. **Final Linear / Classification Layer**: Generates output logits. Quantization error directly shifts class probability boundaries.
3. **Bottleneck / Dimension-Reduced Layers**: Layers with fewer channels or compressed parameter counts have higher information density and less redundancy.
4. **Intermediate Deep Layers**: Often exhibit high parameter counts and channel redundancy. Lowering their bit-width yields large hardware memory and area savings with negligible accuracy degradation.

### Search Space Complexity
If a neural network contains $N$ quantizable layers and each layer can choose from a set of $K$ supported precision levels, the discrete search space contains:

$$\Omega = K^N \text{ candidate configurations}$$

For an 8-layer network with 4 precision options ($\{8, 6, 4, 2\}$ bits), $|\Omega| = 4^8 = 65,536$. For a 18-layer network, $|\Omega| = 4^{18} \approx 6.87 \times 10^{10}$. Exhaustive evaluation is computationally impossible. Automated, intelligent search strategies are mandatory.

---

## 3. Scope and Research Lineage

```
EXISTING WORK
  - Theoretical mixed-precision quantization across layers (e.g., Zhou et al., Dong et al. HAWQ).
  - Search heuristics (RL in HAQ, Hessian analysis in HAWQ, integer programming).
        ↓
OUR ADAPTATION
  - Develop an accelerator-aware greedy search strategy guided by empirical layer sensitivity.
  - Constrain candidate precisions strictly to those supported by the QCore-INT8 architecture.
  - Formulate hardware resource constraints (LUT, BRAM, DSP, FF) and latency checks directly in the decision loop.
        ↓
OUR EXPERIMENTAL VALIDATION
  - Measure accuracy-resource Pareto frontiers against the Uniform INT8 baseline.
  - Verify that no constraint is violated throughout search progression.
```
