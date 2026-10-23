
import numpy as np
import matplotlib.pyplot as plt

f_signal = 7_000
fs = 10_000
t = np.arange(100) / fs
x = np.sin(2 * np.pi * f_signal * t)

# Aliased frequency for this example: 3 kHz
f_alias = abs(f_signal - fs)
x_alias = np.sin(2 * np.pi * f_alias * t)

plt.figure(figsize=(10, 4))
plt.plot(t * 1000, x, "o-", label="7 kHz sampled signal")
plt.plot(t * 1000, x_alias, "--", label="3 kHz alias")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("Aliasing: identical samples for these two tones")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print("Sample rate:", fs, "samples/s")
print("Original frequency:", f_signal, "Hz")
print("Alias frequency:", f_alias, "Hz")
print("Maximum real-signal Nyquist frequency:", fs / 2, "Hz")
