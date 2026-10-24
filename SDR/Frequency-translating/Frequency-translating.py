
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin, lfilter

fs = 200_000
duration = 0.05
t = np.arange(int(fs * duration)) / fs

x = (
    np.exp(1j * 2 * np.pi * 20_000 * t)
    + 0.7 * np.exp(1j * 2 * np.pi * 35_000 * t)
)

center = 20_000
mixed = x * np.exp(-1j * 2 * np.pi * center * t)

taps = firwin(201, 5_000, fs=fs)
filtered = lfilter(taps, 1.0, mixed)

def peak_frequencies(signal, fs):
    n = len(signal)
    spectrum = np.fft.fftshift(np.fft.fft(signal * np.hanning(n)))
    freqs = np.fft.fftshift(np.fft.fftfreq(n, 1/fs))
    return freqs, 20 * np.log10(
        np.maximum(np.abs(spectrum) / n, 1e-12)
    )

freqs, before_db = peak_frequencies(mixed, fs)
freqs, after_db = peak_frequencies(filtered, fs)

plt.figure(figsize=(10, 4))
plt.plot(freqs / 1000, before_db, label="After mixing")
plt.plot(freqs / 1000, after_db, label="After filtering")
plt.xlim(-50, 50)
plt.xlabel("Baseband frequency (kHz)")
plt.ylabel("Relative magnitude (dB)")
plt.title("Channel selection by frequency translation")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
