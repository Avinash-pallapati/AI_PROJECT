# FPGA Resource Budgets & Reference Hardware Platforms

## 1. Reference Device Specifications
Because the specific FPGA board part number for QCore-INT8 is currently marked `UNKNOWN — REQUIRES VERIFICATION`, we tabulate two canonical AMD/Xilinx FPGA devices widely used in academic AI accelerator research:

| Resource Metric | Reference Target A: PYNQ-Z2 (Zynq-7020)<br>`XC7Z020-1CLG400C` | Reference Target B: Kria KV260 (UltraScale+)<br>`XCK26-SFVC784-2LV-C` | Authoritative Source |
| :--- | :--- | :--- | :--- |
| **Logic Cells** | 85,000 | 256,200 | Xilinx DS190 (Zynq-7000) / DS890 (UltraScale+) |
| **Look-Up Tables (LUTs)** | 53,200 | 117,120 | Official AMD Data Sheet |
| **Flip-Flops (FFs)** | 106,400 | 234,240 | Official AMD Data Sheet |
| **Block RAM (BRAM_18K)** | 280 (140 $\times$ 36Kb / 280 $\times$ 18Kb) | 288 (144 $\times$ 36Kb / 288 $\times$ 18Kb) | Official AMD Data Sheet |
| **UltraRAM (URAM_288K)** | 0 | 64 blocks (18.0 Mb) | UltraScale+ Feature |
| **DSP Slices** | 220 (DSP48E1) | 1,248 (DSP48E2) | Official AMD Data Sheet |
| **Maximum Usable Budget (80%)** | 42,560 LUTs, 176 DSPs, 224 BRAM_18K | 93,696 LUTs, 998 DSPs, 230 BRAM_18K | 80% ceiling prevents routing congestion |

---

## 2. Default Search Constraints for QCore-INT8 Benchmarking

To ensure reproducible execution of Task 9 (Greedy Search), we establish baseline constraint budgets based on a typical mid-range FPGA deployment (Zynq-7020 usable budget ceiling):

```yaml
constraints:
  max_lut: 35000          # Maximum usable LUT threshold for core logic
  max_bram_18k: 200       # Maximum usable 18Kb BRAM blocks
  max_dsp: 150            # Maximum usable DSP slices
  max_ff: 70000           # Maximum usable Flip-Flop count
  max_latency_ms: 3.50    # Latency constraint (target: faster than baseline 3.85 ms)
  max_accuracy_drop: 1.50 # Maximum allowed top-1 accuracy degradation (percentage points)
```

> [!NOTE]
> If the course instructor or hardware team provides a specific board part number (e.g. ZCU102, ZedBoard, or PYNQ-Z1), these constraint numbers can be updated in `configs/greedy_search.yaml` without changing the search algorithm code.
