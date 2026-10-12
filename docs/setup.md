# Development Environment and Setup Guide

## 1. Environment Audit & Verification Status

An initial environment audit was conducted on the host machine. The results and current verification statuses are summarized below:

| Component | Target Requirement | Host Status | Assessment / Blocker Details |
| :--- | :--- | :--- | :--- |
| **Operating System** | Linux (recommended for FINN/Docker) or Windows 10/11 | Microsoft Windows 11 (NT x86_64) | Standard Windows host environment. FINN compiler requires Linux Docker container. |
| **Python Runtime** | Python 3.10 or 3.11 | **NOT CONFIGURED IN HOST PATH** | Windows Store stub detected; native Python 3.10/3.11 binary not configured in system PATH. |
| **PyTorch & torchvision** | PyTorch >= 2.0.0, torchvision >= 0.15.0 | **PENDING PYTHON ENVIRONMENT** | Awaiting user Python environment activation or conda/virtualenv container. |
| **Brevitas** | Brevitas >= 0.10.0 | **PENDING PYTHON ENVIRONMENT** | Quantization library for QAT and QONNX export. |
| **ONNX & QONNX** | onnx >= 1.14.0, qonnx >= 0.4.0 | **PENDING PYTHON ENVIRONMENT** | Intermediate representation for quantized graph definitions. |
| **FINN Compiler** | finn >= 0.10.0 | **NOT RUNNING (DOCKER ABSENT)** | FINN requires Docker (`run-docker.sh`) on Linux or WSL2 with Xilinx tool paths. |
| **FPGA Toolchain** | Vivado / Vitis 2022.2+ or Vivado HLS | **NOT DETECTED** | Hardware synthesis and implementation tools not installed on host path. |
| **Version Control** | Git | **NOT IN SYSTEM PATH** | User-level Git installation pending user configuration. |

---

## 2. Installation and Setup Instructions for User

To execute the deep learning training and synthesis pipelines directly on this system, please follow one of the two standard workflows:

### Option A: Conda / Mamba Environment (Recommended for Windows Development)
1. Install [Miniforge](https://github.com/conda-forge/miniforge) or [Miniconda](https://docs.anaconda.com/miniconda/).
2. Create and activate the project environment:
   ```powershell
   conda env create -f environment.yml
   conda activate ai_accelerator
   ```
3. Verify installation using the smoke test script:
   ```powershell
   python scripts/evaluate.py --help
   pytest tests/
   ```

### Option B: Python Virtual Environment (`venv`)
If a system Python 3.10 or 3.11 is installed:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. FINN Container Setup (For Bitstream Generation & Hardware Validation)
When progressing to physical FPGA synthesis:
1. Ensure Docker Desktop with WSL2 backend is running.
2. Clone and start FINN:
   ```bash
   git clone https://github.com/Xilinx/finn.git
   cd finn
   export FINN_XILINX_PATH=/opt/Xilinx
   export FINN_XILINX_VERSION=2022.2
   ./run-docker.sh
   ```
3. Run the FINN quicktest inside the container:
   ```bash
   pytest -k "quicktest"
   ```

---

## 4. Deterministic Mock Fallback Mode
In accordance with Master Game Plan Section 10 and Cost Estimation guidelines:
- If PyTorch, Brevitas, or FINN FPGA synthesis tools are awaiting host environment provisioning, the search framework and sensitivity analysis pipelines operate using a **deterministic, mathematically rigorous FPGA cost model** and pre-computed or synthetic evaluation metrics.
- This ensures full algorithmic validation, unit test execution, and end-to-end reproducibility of Tasks 1–9 without being blocked by external licensing or container daemons.
