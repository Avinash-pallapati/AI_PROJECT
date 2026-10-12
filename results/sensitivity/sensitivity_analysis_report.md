# Layer-Sensitivity Analysis Report

## 1. Executive Summary
In accordance with **Tasks 7 and 8** of the Master Game Plan, we completed the single-layer precision sensitivity analysis on the frozen Uniform INT8 baseline (`84.12%` Top-1 accuracy). 

Each of the 8 quantizable layers in the CNV network was individually perturbed from **INT8 to INT4** (weights + activations, $W+A$), evaluated under inference-only conditions, and ranked by accuracy drop:
$$\text{Rank 1 (Least Sensitive / Smallest Degradation)} \longrightarrow \text{Rank 8 (Most Sensitive / Largest Degradation)}$$

---

## 2. Experimental Results Summary

| Rank | Layer Name | Layer Type | Parameter Count | Precision Change | Top-1 Accuracy (%) | Accuracy Drop ($\Delta$) | Sensitivity Classification |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | `conv3` | QuantConv2d | 147,456 | INT8 $\to$ INT4 | **83.84** | **+0.28%** | **LOW (Least sensitive)** |
| **2** | `conv2` | QuantConv2d | 73,728 | INT8 $\to$ INT4 | **83.81** | **+0.31%** | **LOW (Insensitive)** |
| **3** | `conv4` | QuantConv2d | 294,912 | INT8 $\to$ INT4 | **83.77** | **+0.35%** | **LOW (Insensitive)** |
| **4** | `conv1` | QuantConv2d | 36,864 | INT8 $\to$ INT4 | **83.70** | **+0.42%** | **MODERATE (Robust)** |
| **5** | `fc0` | QuantLinear | 2,097,152 | INT8 $\to$ INT4 | **83.67** | **+0.45%** | **MODERATE (High Memory Benefit)** |
| **6** | `conv5` | QuantConv2d | 589,824 | INT8 $\to$ INT4 | **83.34** | **+0.78%** | **MODERATE (Noticeable penalty)** |
| **7** | `conv0` | QuantConv2d | 1,728 | INT8 $\to$ INT4 | **80.27** | **+3.85%** | **HIGH (Sensitive — Retain INT8)** |
| **8** | `fc1` | QuantLinear | 5,130 | INT8 $\to$ INT4 | **79.92** | **+4.20%** | **HIGH (Most sensitive — Retain INT8)** |

---

## 3. Key Architectural Observations
1. **Extreme Boundary Sensitivity (`conv0` & `fc1`)**:
   - `conv0` directly filters raw continuous RGB signals; 4-bit quantization creates severe quantization noise that cascades through the entire network, causing a **3.85% accuracy drop**.
   - `fc1` produces the unnormalized logits for the 10 classes; collapsing its bit-width causes misclassification of subtle inter-class boundaries, resulting in a **4.20% drop**.
   - **Conclusion**: Boundary layers must be protected and maintained at high bit-width (INT8).
2. **Intermediate Resilience (`conv1` through `conv4`)**:
   - The intermediate convolutional layers exhibit remarkable noise tolerance, with accuracy drops under $0.45\%$.
   - These layers represent prime targets for precision reduction.
3. **The High-Yield Opportunity of `fc0`**:
   - `fc0` contains $2,097,152$ parameters, which constitutes **64.6% of the entire model's parameters**.
   - Reducing `fc0` to INT4 yields an instantaneous **1.0 MB memory reduction** on-chip with only a modest **0.45% accuracy drop**.

---

## 4. Visual Artifacts
- Sequential Layer Drop Chart: `results/sensitivity/plots/layer_vs_drop.svg`
- Sorted Sensitivity Chart: `results/sensitivity/plots/sorted_sensitivity.svg`
- Raw Measurements CSV: `results/sensitivity/sensitivity_results.csv`
- Machine-Readable Ranking JSON: `results/sensitivity/sensitivity_ranking.json`
