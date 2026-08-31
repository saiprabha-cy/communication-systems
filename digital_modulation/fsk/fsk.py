import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# MOD-02 — FSK
# ============================================================

# -----------------------------
# Digital data
# -----------------------------

bits = np.array([1, 0, 1, 1, 0])


# -----------------------------
# FSK parameters
# -----------------------------

A = 1.0

f0 = 5_000       # Frequency for bit 0: 5 kHz
f1 = 10_000      # Frequency for bit 1: 10 kHz

Tb = 1e-3        # Bit duration = 1 ms

samples_per_bit = 1000

fs = samples_per_bit / Tb

print("Sampling frequency:", fs, "Hz")


# -----------------------------
# Time vector
# -----------------------------

t_bit = np.arange(0, Tb, 1 / fs)


# -----------------------------
# Generate FSK signal
# -----------------------------

fsk_signal = []

time = []

for bit_index, bit in enumerate(bits):

    if bit == 0:
        frequency = f0
    else:
        frequency = f1

    signal = A * np.cos(2 * np.pi * frequency * t_bit)

    fsk_signal.extend(signal)

    time.extend(
        t_bit + bit_index * Tb
    )


fsk_signal = np.array(fsk_signal)
time = np.array(time)


# -----------------------------
# Plot FSK waveform
# -----------------------------

plt.figure(figsize=(12, 4))

plt.plot(time * 1000, fsk_signal)

plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")

plt.title("MOD-02 — Binary FSK")

plt.grid(True)

plt.tight_layout()

plt.show()


# -----------------------------
# Display information
# -----------------------------

print("\n========== FSK PARAMETERS ==========")

print("Bits              :", bits)

print("Bit duration      :", Tb, "seconds")

print("Frequency for 0   :", f0, "Hz")

print("Frequency for 1   :", f1, "Hz")

print("Amplitude          :", A)

print("====================================")