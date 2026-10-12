# Experimental Protocol: Layer-Sensitivity Analysis

## 1. Research Purpose & Hypothesis
The goal of layer-sensitivity analysis is to quantify how much overall network classification accuracy degrades when a single layer's precision is reduced from **INT8 to INT4**, while all other layers are held constant at INT8.

### Research Hypothesis
- Convolutional layers that operate directly on continuous input signals (`conv0`) and dense layers producing classification logits (`fc1`) have high representational sensitivity and will experience larger accuracy drops.
- Intermediate feature-extraction layers (`conv1` through `conv4`) exhibit significant feature map redundancy and channel overparameterization, and will experience negligible accuracy degradation when reduced to INT4.
- The resulting sensitivity ranking provides the search engine with an optimal heuristic ordering, allowing it to reduce precision on insensitive layers first.

---

## 2. Experimental Controls and Invariants
To ensure scientific reproducibility, the following controls are strictly enforced:

1. **Baseline Invariance**: Every single-layer experiment starts from an exact, bit-identical copy of the frozen Uniform INT8 baseline (`84.12%` top-1 accuracy).
2. **One-At-A-Time Perturbation**: In each experiment $i$, exactly one layer $L_i$ has its precision changed ($8 \to 4$). All remaining $N-1$ layers are clamped to INT8.
3. **Quantized Tensors**: Both **Weights and Activations ($W+A$)** of layer $L_i$ are converted to 4-bit precision.
4. **Evaluation Mode**: **Inference-Only Evaluation**. No fine-tuning or retraining is applied during sensitivity profiling. This directly measures the intrinsic mathematical tolerance of the pre-trained weights and representations without introducing confounding variables from optimizer momentum, learning rates, or epoch counts.
5. **Identical Test Split & Preprocessing**: Every measurement evaluates all 10,000 images in the CIFAR-10 test set using identical normalization ($mean, std$) and batch sizes.
6. **No Silent Skips**: Any layer that cannot be quantized or is unsupported must be recorded in the results table with `Supported: False` and an explicit architectural rationale.

---

## 3. Results Schema
The experiment logs the following schema to `results/sensitivity/sensitivity_results.csv`:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `run_id` | String | Unique identifier (e.g., `sens_001`) |
| `layer` | String | Target layer name (`conv0` through `fc1`) |
| `old_bits` | Integer | Baseline precision (`8`) |
| `new_bits` | Integer | Perturbed precision (`4`) |
| `weight_act` | String | Quantized tensors (`W+A`) |
| `accuracy` | Float | Measured top-1 test accuracy (%) |
| `accuracy_drop` | Float | Degradation: $\text{Acc}_{\text{baseline}} - \text{Acc}_{\text{candidate}}$ (%) |
| `supported` | String | Hardware deployment status (`yes` / `no`) |
| `runtime_sec` | Float | Wall-clock execution time for evaluation |
| `notes` | String | Architectural observations |

---

## 4. Sensitivity Ranking Methodology
Layers are sorted in **ascending order of accuracy drop**:
$$\text{Lowest Accuracy Drop (Least Sensitive)} \longrightarrow \text{Highest Accuracy Drop (Most Sensitive)}$$

This ranking directly guides the candidate selection queue in Task 9.
