
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import resample_poly

fs_in = 48_000
L, M = 2, 3
fs_out = fs_in * L / M

duration = 0.1
t = np.arange(int(fs_in * duration)) / fs_in
x = np.sin(2 * np.pi * 5_000 * t)

y = resample_poly(x, L, M)

print("Input sample rate:", fs_in)
print("Output sample rate:", fs_out)
print("Input samples:", len(x))
print("Output samples:", len(y))

plt.figure(figsize=(10, 4))
plt.plot(t[:100] * 1000, x[:100], label="Input")
t_out = np.arange(len(y)) / fs_out
plt.plot(t_out[:70] * 1000, y[:70], "o-", label="Resampled")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("48 kS/s to 32 kS/s resampling")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
