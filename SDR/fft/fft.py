
import numpy as np
import matplotlib.pyplot as plt

fs = 100_000
N = 100_000
t = np.arange(N) / fs

x = (
    1.0 * np.exp(1j * 2 * np.pi * 5_000 * t)
    + 0.5 * np.exp(1j * 2 * np.pi * 15_000 * t)
)

window = np.hanning(N)
X = np.fft.fftshift(np.fft.fft(x * window))
freq = np.fft.fftshift(np.fft.fftfreq(N, d=1/fs))

# Normalize amplitude approximately for a windowed sinusoid
magnitude = np.abs(X) / np.sum(window)
magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-12))

plt.figure(figsize=(10, 4))
plt.plot(freq / 1000, magnitude_db)
plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude (dB relative to full-scale tone)")
plt.title("Complex-baseband spectrum")
plt.xlim(-30, 30)
plt.ylim(-120, 5)
plt.grid(True)
plt.tight_layout()
plt.show()

print("FFT length:", N)
print("Frequency-bin spacing:", fs / N, "Hz")
