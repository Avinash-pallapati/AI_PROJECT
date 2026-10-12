# Quantization Fundamentals

## 1. Overview and Core Mathematical Principles
Quantization is the mapping of continuous (or high-precision floating-point, e.g., 32-bit IEEE 754 float) tensors to a finite set of discrete values (e.g., 8-bit, 4-bit, or 2-bit integers). In neural networks, quantization dramatically reduces memory footprint, memory bandwidth pressure, and computational resource requirements.

### Mathematical Formulation
For a real-valued tensor $X$ (weights or activations), uniform affine (asymmetric) quantization to a $b$-bit integer representation is given by:

$$q = \text{clamp}\left( \left\lfloor \frac{X}{S} \right\rceil + Z, \; q_{\min}, \; q_{\max} \right)$$

where:
- $S$ is the positive real-valued **scale factor**: $S = \frac{\max(X) - \min(X)}{q_{\max} - q_{\min}}$
- $Z$ is the integer **zero-point** ensuring that the real value zero is represented exactly: $Z = \text{round}\left( - \frac{\min(X)}{S} \right) + q_{\min}$
- $\lfloor \cdot \rceil$ denotes the nearest integer rounding operator.
- $[q_{\min}, q_{\max}]$ denotes the integer representable range. For signed $b$-bit integers, typically $[-2^{b-1}, 2^{b-1}-1]$ or symmetric range $[-2^{b-1}+1, 2^{b-1}-1]$; for unsigned, $[0, 2^b-1]$.

De-quantization maps the integer representation back to real-valued domain for floating-point simulation:
$$\hat{X} = S \cdot (q - Z)$$

### Symmetric vs. Asymmetric Quantization
- **Symmetric Quantization**: $Z = 0$. $S = \frac{\max(|X|)}{q_{\max}}$. Greatly simplifies FPGA hardware arithmetic because zero-point cross-terms vanish in matrix multiplication ($\sum W \cdot X = S_w S_x \sum q_w q_x$).
- **Asymmetric Quantization**: $Z \neq 0$. Better fits skewed activation distributions (such as post-ReLU activations) but incurs extra subtraction logic on hardware.

---

## 2. Post-Training Quantization (PTQ) vs. Quantization-Aware Training (QAT)

### Post-Training Quantization (PTQ)
- In PTQ, a pre-trained FP32 network is quantized directly using calibration data to estimate dynamic ranges ($S$ and $Z$).
- Advantages: Zero training time, no gradients needed.
- Limitations: At low bit-widths ($\le 4$ bits), PTQ frequently induces severe accuracy collapse due to accumulated quantization noise and clipping error.

### Quantization-Aware Training (QAT)
- In QAT, quantization is modeled during the training/fine-tuning forward pass using "fake-quantization" operators.
- **Straight-Through Estimator (STE)**: Because the rounding function $\lfloor \cdot \rceil$ has zero derivative almost everywhere, standard gradient descent cannot compute gradients. STE approximates the gradient during backpropagation as an identity pass-through within the valid dynamic range:

$$\frac{\partial \hat{X}}{\partial X} \approx \begin{cases} 1 & \text{if } X \in [X_{\min}, X_{\max}] \\ 0 & \text{otherwise} \end{cases}$$

- This enables weights to adapt to discrete representations, recovering accuracy even at low bit-widths.

---

## 3. Scope and Research Lineage

```
EXISTING WORK
  - Standard quantization theory (Jacob et al. 2018, Nagel et al. 2021).
  - Brevitas library for PyTorch QAT with configurable bit-widths and STE.
        ↓
OUR ADAPTATION
  - Train a well-converged uniform INT8 model as our frozen reference baseline.
  - Implement dynamic precision reconfiguration for individual layers using Brevitas primitives.
        ↓
OUR EXPERIMENTAL VALIDATION
  - Empirically measure degradation across bit-widths (INT8 -> INT4).
  - Validate accuracy retention under QCore-INT8 hardware constraints.
```

---

## 4. Hardware Implications for FPGA
On FPGA hardware (e.g., Xilinx 7-Series / UltraScale+), multiplier implementations scale with bit-width:
- Standard DSP48E1/E2 slices have hardwired $18 \times 25$ or $18 \times 27$ multipliers. An 8-bit $\times$ 8-bit multiplication easily packs into a DSP slice.
- When bit-widths drop to 4-bit or 2-bit, multiple multiplications can be packed into a single DSP slice, or implemented with extreme efficiency inside 6-input LUTs (Look-Up Tables) as distributed logic, drastically reducing hardware footprint.
