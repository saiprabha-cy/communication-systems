
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin, lfilter, freqz

fs = 100_000
duration = 0.05
t = np.arange(int(fs * duration)) / fs

# Wanted 5 kHz tone + unwanted 20 kHz tone
x = (
    np.sin(2 * np.pi * 5_000 * t)
    + 0.7 * np.sin(2 * np.pi * 20_000 * t)
)

# FIR low-pass: pass below 8 kHz
taps = firwin(101, 8_000, fs=fs)
y = lfilter(taps, 1.0, x)

f, H = freqz(taps, worN=4096, fs=fs)
response_db = 20 * np.log10(np.maximum(np.abs(H), 1e-12))

fig, ax = plt.subplots(2, 1, figsize=(10, 7))

ax[0].plot(t[:250] * 1000, x[:250], label="Input")
ax[0].plot(t[:250] * 1000, y[:250], label="Filtered")
ax[0].set_title("Time-domain comparison")
ax[0].set_ylabel("Amplitude")
ax[0].legend()
ax[0].grid(True)

ax[1].plot(f / 1000, response_db)
ax[1].axvline(8, linestyle="--", label="Cutoff")
ax[1].set_title("FIR low-pass frequency response")
ax[1].set_xlabel("Frequency (kHz)")
ax[1].set_ylabel("Gain (dB)")
ax[1].set_ylim(-100, 5)
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()
