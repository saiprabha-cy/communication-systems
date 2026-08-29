import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# LoRa CSS parameters
# ============================================================

start_frequency = 5_000       # 5 kHz
end_frequency = 20_000        # 20 kHz
duration = 0.02               # 20 ms

sample_rate = 200_000         # 200 kHz


# ============================================================
# Time vector
# ============================================================

t = np.arange(0, duration, 1 / sample_rate)


# ============================================================
# Generate instantaneous frequency
# ============================================================

k = (end_frequency - start_frequency) / duration

instantaneous_frequency = start_frequency + k * t


# ============================================================
# Generate phase
# ============================================================

phase = (
    2 * np.pi *
    (
        start_frequency * t
        + 0.5 * k * t**2
    )
)


# ============================================================
# Generate complex baseband chirp
# ============================================================

chirp = np.exp(1j * phase)


# ============================================================
# Generate AWGN
# ============================================================

noise_power = 0.5

noise = np.sqrt(noise_power / 2) * (
    np.random.randn(len(t))
    + 1j * np.random.randn(len(t))
)


# ============================================================
# Add noise to chirp
# ============================================================

noisy_chirp = chirp + noise


# ============================================================
# Plot 1 — Clean chirp
# ============================================================

plt.figure(figsize=(10, 4))

plt.plot(t * 1000, np.real(chirp))

plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("Clean LoRa-style CSS Chirp")
plt.grid()

plt.show()


# ============================================================
# Plot 2 — Noisy chirp
# ============================================================

plt.figure(figsize=(10, 4))

plt.plot(t * 1000, np.real(noisy_chirp))

plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("LoRa-style CSS Chirp with AWGN")
plt.grid()

plt.show()


# ============================================================
# Print parameters
# ============================================================

print("========== LORA-05 NOISE ROBUSTNESS ==========")

print(f"Start frequency : {start_frequency / 1000:.1f} kHz")
print(f"End frequency   : {end_frequency / 1000:.1f} kHz")
print(f"Duration        : {duration * 1000:.1f} ms")
print(f"Bandwidth       : {(end_frequency - start_frequency) / 1000:.1f} kHz")
print(f"Sweep rate      : {k / 1000:.1f} kHz/s")
print(f"Noise power     : {noise_power}")