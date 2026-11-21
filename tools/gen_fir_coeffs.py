"""產生 FIR 低通係數（fs=100Hz, 31 taps, cutoff=10Hz）並寫入 Core/Inc/fir_coeffs.h"""
import os
import numpy as np
from scipy.signal import firwin

NUM_TAPS, CUTOFF, FS = 31, 10, 100

def main():
    h = firwin(NUM_TAPS, CUTOFF, fs=FS)  # 對稱，不需時間反轉
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "Core", "Inc", "fir_coeffs.h")
    lines = [
        "/* 自動產生：tools/gen_fir_coeffs.py，請勿手動修改 */",
        "#ifndef FIR_COEFFS_H",
        "#define FIR_COEFFS_H",
        "",
        "#define NUM_TAPS %d" % NUM_TAPS,
        "#define FIR_FS_HZ %d" % FS,
        "#define FIR_CUTOFF_HZ %d" % CUTOFF,
        "",
        "static const float firCoeffs[NUM_TAPS] = {",
    ]
    for i in range(0, NUM_TAPS, 4):
        lines.append("    " + ", ".join("%.8ff" % c for c in h[i:i + 4]) + ("," if i + 4 < NUM_TAPS else ""))
    lines += ["};", "", "#endif /* FIR_COEFFS_H */", ""]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("wrote", out, "sum=%.6f" % h.sum())

    # 主機端預估 max error（與韌體相同流程）
    n = np.arange(300)
    x = np.sin(2*np.pi*5*n/FS) + 0.5*np.sin(2*np.pi*40*n/FS)
    y = np.convolve(x, h.astype(np.float32))[:300]
    ideal = np.sin(2*np.pi*5*(n-15)/FS)
    print("host max error = %.6f" % np.max(np.abs(y[NUM_TAPS:] - ideal[NUM_TAPS:])))

if __name__ == "__main__":
    main()
