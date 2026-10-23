
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
N = 100_000
fs = 100_000
t = np.arange(N) / fs

signal = np.cos(2 * np.pi * 5_000 * t)
noise = 0.3 * rng.standard_normal(N)
received = signal + noise

signal_power = np.mean(signal**2)
noise_power = np.mean(noise**2)
snr_db = 10 * np.log10(signal_power / noise_power)

print(f"Signal power: {signal_power:.4f}")
print(f"Noise power: {noise_power:.4f}")
print(f"Measured SNR: {snr_db:.2f} dB")

plt.figure(figsize=(10, 4))
plt.plot(t[:500] * 1000, received[:500], label="Signal + noise")
plt.plot(t[:500] * 1000, signal[:500], label="Original signal", alpha=0.8)
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("Noisy received signal")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
