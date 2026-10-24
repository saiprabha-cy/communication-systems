
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin, freqz

fs = 100_000
tap_counts = [21, 51, 101, 201]

plt.figure(figsize=(10, 5))

for n in tap_counts:
    taps = firwin(n, 8_000, fs=fs)
    f, H = freqz(taps, worN=4096, fs=fs)
    db = 20 * np.log10(np.maximum(np.abs(H), 1e-12))
    plt.plot(f / 1000, db, label=f"{n} taps")

    delay_ms = (n - 1) / (2 * fs) * 1000
    print(f"{n:3d} taps: group delay = {delay_ms:.3f} ms")

plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude (dB)")
plt.title("Effect of FIR filter length")
plt.xlim(0, 30)
plt.ylim(-100, 5)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
