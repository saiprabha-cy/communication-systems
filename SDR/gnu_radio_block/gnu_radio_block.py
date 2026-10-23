
import numpy as np
import matplotlib.pyplot as plt

fs = 100_000
f = 5_000
N = 2_000

t = np.arange(N) / fs
x = np.exp(1j * 2 * np.pi * f * t)

fig, ax = plt.subplots(2, 1, figsize=(10, 6))

ax[0].plot(t[:200] * 1000, x.real[:200], label="I")
ax[0].plot(t[:200] * 1000, x.imag[:200], label="Q")
ax[0].set_title("Time-domain display")
ax[0].set_ylabel("Amplitude")
ax[0].legend()
ax[0].grid(True)

freq = np.fft.fftshift(np.fft.fftfreq(N, 1/fs))
spec = np.fft.fftshift(np.fft.fft(x * np.hanning(N)))
db = 20 * np.log10(np.maximum(np.abs(spec) / np.sum(np.hanning(N)), 1e-12))

ax[1].plot(freq / 1000, db)
ax[1].set_title("Frequency-domain display")
ax[1].set_xlabel("Frequency (kHz)")
ax[1].set_ylabel("Magnitude (dB)")
ax[1].grid(True)

plt.tight_layout()
plt.show()
