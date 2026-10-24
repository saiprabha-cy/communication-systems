
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, sosfiltfilt

fs = 200_000
t = np.arange(int(fs * 0.05)) / fs
fm, fc, mu = 1_000, 20_000, 0.6

message = np.cos(2 * np.pi * fm * t)
am = (1 + mu * message) * np.cos(2 * np.pi * fc * t)

envelope = np.abs(hilbert(am))
sos = butter(4, 3_000, fs=fs, output="sos")
recovered = sosfiltfilt(sos, envelope)
recovered = (recovered - np.mean(recovered)) / mu

plt.figure(figsize=(10, 4))
plt.plot(t[:1000] * 1000, message[:1000], label="Original message")
plt.plot(t[:1000] * 1000, recovered[:1000], label="Recovered message")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("AM envelope demodulation")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
