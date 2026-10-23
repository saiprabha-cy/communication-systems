
import numpy as np
import matplotlib.pyplot as plt

fs = 1_000_000
f_in = 100_000
f_lo = 99_000
duration = 0.002

t = np.arange(int(fs * duration)) / fs
x = np.exp(1j * 2 * np.pi * f_in * t)
lo = np.exp(-1j * 2 * np.pi * f_lo * t)

y = x * lo

print("Input frequency:", f_in, "Hz")
print("LO frequency:", f_lo, "Hz")
print("Expected translated frequency:", f_in - f_lo, "Hz")
print("Output mean magnitude:", np.mean(np.abs(y)))

fig, ax = plt.subplots(2, 1, figsize=(10, 6))
ax[0].plot(t[:200] * 1e6, x.real[:200])
ax[0].set_title("Input real component")
ax[0].set_ylabel("Amplitude")
ax[0].grid(True)

ax[1].plot(t[:200] * 1e6, y.real[:200])
ax[1].set_title("After complex frequency translation")
ax[1].set_xlabel("Time (µs)")
ax[1].set_ylabel("Amplitude")
ax[1].grid(True)

plt.tight_layout()
plt.show()
