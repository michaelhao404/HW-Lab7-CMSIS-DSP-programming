"""擷取真實加速度計資料（輸入 vs FIR 輸出），存成 results/<name>.csv 與 .png
用法：python tools/capture_plot_real.py COM8 [秒數=10] [名稱=real_data]
例：  python tools/capture_plot_real.py COM8 10 real_still
      python tools/capture_plot_real.py COM8 10 real_shake
"""
import os
import sys
import time
import serial
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
HEADER = "in_x,in_y,in_z,out_x,out_y,out_z"

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "COM8"
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 10
    name = sys.argv[3] if len(sys.argv) > 3 else "real_data"
    os.makedirs(RES, exist_ok=True)
    ser = serial.Serial(port, 115200, timeout=5)
    ser.reset_input_buffer()
    print("開始錄製 %.0f 秒 ..." % secs)
    rows, t0 = [], time.time()
    while time.time() - t0 < secs:
        line = ser.readline().decode(errors="ignore").strip()
        parts = line.split(",")
        if len(parts) != 6 or line == HEADER:
            continue
        try:
            rows.append([float(p) for p in parts])
        except ValueError:
            continue
    ser.close()
    if not rows:
        sys.exit("沒有收到資料，請確認 COM 埠與韌體模式 (USE_KNOWN_SIGNAL=0)")
    dur = time.time() - t0
    print("收到 %d 筆，實際取樣率約 %.1f Hz" % (len(rows), len(rows) / dur))

    with open(os.path.join(RES, name + ".csv"), "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for r in rows:
            f.write("%.1f,%.1f,%.1f,%.3f,%.3f,%.3f\n" % tuple(r))

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for i, ax_name in enumerate("XYZ"):
        axes[i].plot([r[i] for r in rows], alpha=0.6, label="input")
        axes[i].plot([r[i + 3] for r in rows], linewidth=2, label="FIR output")
        axes[i].set_ylabel("%s (mg)" % ax_name)
        axes[i].grid(alpha=0.3)
        axes[i].legend(loc="upper right")
    axes[2].set_xlabel("sample (~100 Hz)")
    fig.suptitle("Accelerometer FIR low-pass (31 taps, fc=10 Hz) - %s" % name)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, name + ".png"), dpi=150)
    print("已存到 results/%s.csv 與 .png" % name)

if __name__ == "__main__":
    main()
