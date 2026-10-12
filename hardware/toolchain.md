# Hardware and Toolchain Environment Status

## 1. Host Operating System
- **Host OS**: Microsoft Windows (NT kernel x86_64)
- **Shell**: PowerShell 5.1
- **Package Manager**: Windows Package Manager (`winget` v1.29.380)

---

## 2. FPGA Toolchain & Synthesis Software

| Software / Tool | Expected Role | Status on Host | Evidence / Notes |
| :--- | :--- | :--- | :--- |
| **Xilinx Vivado** | FPGA bitstream synthesis, implementation, and timing analysis | **NOT DETECTED ON HOST PATH** | `vivado` command not found in host PATH; standard directories (`C:\Xilinx`) not present on host C: drive. |
| **Vitis / Vivado HLS** | C++ High-Level Synthesis of streaming custom hardware IP blocks | **NOT DETECTED ON HOST PATH** | Requires Xilinx installation. |
| **Docker Desktop** | Linux containerization required by FINN compiler (`run-docker.sh`) | **NOT INSTALLED / RUNNING** | `docker` command not recognized in PATH. |
| **Target FPGA Board** | Target hardware deployment platform | **PENDING SPECIFICATION** | `UNKNOWN — REQUIRES VERIFICATION` (to be established via QCore-INT8 documentation). |

---

## 3. FINN Framework Requirements and Execution Model
FINN (Fast, Scalable Binarized/Quantized Neural Network Inference) operates predominantly in a **Dockerized Linux environment** due to hard dependencies on Linux-native shared libraries, PyEDA, and the Xilinx Vivado HLS toolflow.

### Standard FINN Compilation Flow:
1. Model authored and trained with Brevitas in Python.
2. Exported to QONNX (`brevitas.export.onnx.qonnx.manager.QONNXManager.export(...)`).
3. Imported into FINN container (`finn.transformation...`).
4. Graph transformations: Streamlining, Tidy-up, MVTU mapping.
5. Resource and latency estimation passes executed (`estimate_layer_resources`).
6. Vivado HLS IP stitching and bitstream generation.

### Development Strategy under Host Constraints:
Because the host environment is Windows without native Vivado or Docker pre-installed:
1. **Algorithm Validation First**: Implement the accelerator-aware greedy search with transparent, deterministic analytical FPGA cost modeling (LUT/BRAM/DSP/FF/latency) adhering to published Xilinx/FINN equations.
2. **QONNX Export Compatibility**: Implement Brevitas QAT models strictly complying with FINN/QONNX export standards.
3. **Hardware Synthesis Milestone**: When deploying to actual hardware or running full Vivado synthesis, run within a FINN Docker container or pass generated QONNX graphs to the laboratory synthesis server.
