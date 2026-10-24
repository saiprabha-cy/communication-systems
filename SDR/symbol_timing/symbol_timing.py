
import numpy as np
import matplotlib.pyplot as plt

fs = 100_000
f_offset = 250
duration = 0.02

t = np.arange(int(fs * duration)) / fs
tx = np.exp(1j * 2 * np.pi * 5_000 * t)
rx = tx * np.exp(1j * (2 * np.pi * f_offset * t + 0.5))

plt.figure(figsize=(10, 4))
plt.plot(t * 1000, np.unwrap(np.angle(rx)))
plt.xlabel("Time (ms)")
plt.ylabel("Unwrapped phase (rad)")
plt.title("Phase drift from carrier frequency offset")
plt.grid(True)
plt.tight_layout()
plt.show()

# Estimate the offset from consecutive phase differences
phase_step = np.angle(rx[1:] * np.conj(rx[:-1]))
estimated_offset = np.mean(phase_step) * fs / (2 * np.pi)

print(f"True frequency offset: {f_offset} Hz")
print(f"Estimated frequency offset: {estimated_offset:.2f} Hz")
