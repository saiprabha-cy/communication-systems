import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# MOD-01 — Amplitude Shift Keying (ASK)
# ============================================================

# ------------------------------------------------------------
# Parameters
# ------------------------------------------------------------

bit_rate = 10
carrier_frequency = 50
amplitude = 1.0

bits = np.array([1, 0, 1, 1, 0])

samples_per_bit = 100


# ------------------------------------------------------------
# Time configuration
# ------------------------------------------------------------

bit_duration = 1 / bit_rate

total_duration = len(bits) * bit_duration

sample_rate = samples_per_bit / bit_duration

t = np.arange(
    0,
    total_duration,
    1 / sample_rate
)


# ------------------------------------------------------------
# Generate carrier
# ------------------------------------------------------------

carrier = amplitude * np.cos(
    2 * np.pi * carrier_frequency * t
)


# ------------------------------------------------------------
# Generate ASK signal
# ------------------------------------------------------------

ask_signal = np.zeros_like(t)


for i, bit in enumerate(bits):

    start = i * samples_per_bit
    end = (i + 1) * samples_per_bit

    if bit == 1:

        ask_signal[start:end] = carrier[start:end]

    else:

        ask_signal[start:end] = 0


# ------------------------------------------------------------
# Plot carrier
# ------------------------------------------------------------

plt.figure(figsize=(10, 4))

plt.plot(t, carrier)

plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.title("Carrier Signal")

plt.grid()

plt.show()


# ------------------------------------------------------------
# Plot ASK signal
# ------------------------------------------------------------

plt.figure(figsize=(10, 4))

plt.plot(t, ask_signal)

plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.title("Binary ASK Signal")

plt.grid()

plt.show()


# ------------------------------------------------------------
# Display information
# ------------------------------------------------------------

print("========== MOD-01 ASK ==========")

print(f"Bit rate            : {bit_rate} bits/s")
print(f"Carrier frequency   : {carrier_frequency} Hz")
print(f"Carrier amplitude   : {amplitude}")
print(f"Bits                : {bits}")
print(f"Bit duration        : {bit_duration:.3f} s")