"""擷取已知訊號驗證輸出，存成 results/known_signal.csv 與 .png
用法：python tools/capture_plot.py COM5
韌體每 3 秒重複輸出一次；本程式等到 'n,x,y' 標頭後開始記錄，遇到 'max error' 結束。
"""
import os
import sys
import serial
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DELAY = 15
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "COM5"
    os.makedirs(RES, exist_ok=True)
    ser = serial.Serial(port, 115200, timeout=10)
    print("等待標頭 n,x,y ...")
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            sys.exit("逾時：沒有收到資料，請確認 COM 埠與板子是否在執行")
        if line == "n,x,y":
            break
    rows, max_err = [], None
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            sys.exit("逾時：資料不完整")
        if line.startswith("max error"):
            max_err = line
            break
        try:
            n, x, y = line.split(",")
            rows.append((int(n), float(x), float(y)))
        except ValueError:
            continue  # 略過雜訊行
    ser.close()
    print(max_err, "| 收到", len(rows), "點")

    csv_path = os.path.join(RES, "known_signal.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("n,x,y\n")
        for n, x, y in rows:
            f.write("%d,%.6f,%.6f\n" % (n, x, y))

    n = [r[0] for r in rows]
    x = [r[1] for r in rows]
    y = [r[2] for r in rows]
    plt.figure(figsize=(10, 4.5))
    plt.plot(n, x, label="input: 5 Hz + 0.5 x 40 Hz", alpha=0.6)
    plt.plot(n, y, label="FIR output (31 taps, fc=10 Hz)", linewidth=2)
    plt.axvline(31, color="gray", linestyle="--", label="transient ends (n=31)")
    plt.xlabel("sample n (fs = 100 Hz)")
    plt.ylabel("amplitude")
    plt.title("Known signal test - %s" % max_err)
    plt.legend(loc="upper right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "known_signal.png"), dpi=150)
    print("已存到 results/known_signal.csv 與 known_signal.png")

if __name__ == "__main__":
    main()
