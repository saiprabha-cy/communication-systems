import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# LORA-06 — Simplified LoRa Link Simulation
# ============================================================

# ------------------------------------------------------------
# LoRa parameters
# ------------------------------------------------------------

SF = 7
M = 2 ** SF

bandwidth = 125_000       # 125 kHz
symbol_duration = M / bandwidth

sample_rate = bandwidth

noise_power = 0.05


# ------------------------------------------------------------
# Generate base upchirp
# ------------------------------------------------------------

num_samples = M

t = np.arange(num_samples) / sample_rate

k = bandwidth / symbol_duration

phase = 2 * np.pi * 0.5 * k * t**2

base_chirp = np.exp(1j * phase)


# ------------------------------------------------------------
# Data to transmit
# ------------------------------------------------------------

tx_symbols = np.array([10, 25, 50, 100])


print("========== LORA-06 ==========")

print(f"Spreading Factor : SF{SF}")
print(f"Number of symbols: {M}")
print(f"Bandwidth        : {bandwidth / 1000:.1f} kHz")
print(f"Symbol duration  : {symbol_duration * 1000:.3f} ms")

print("\nTransmitted symbols:")
print(tx_symbols)


# ------------------------------------------------------------
# Simplified CSS modulation
# ------------------------------------------------------------

def modulate_symbol(symbol):
    shift = symbol % M

    return np.roll(base_chirp, shift)


# ------------------------------------------------------------
# Transmitter
# ------------------------------------------------------------

tx_signal = np.concatenate(
    [modulate_symbol(symbol) for symbol in tx_symbols]
)


# ------------------------------------------------------------
# AWGN channel
# ------------------------------------------------------------

noise = np.sqrt(noise_power / 2) * (
    np.random.randn(len(tx_signal))
    + 1j * np.random.randn(len(tx_signal))
)

rx_signal = tx_signal + noise


# ------------------------------------------------------------
# Simplified receiver
# ------------------------------------------------------------

def demodulate_symbol(received_symbol):

    # Correlate received signal with every possible
    # cyclically shifted chirp.

    correlations = []

    for symbol in range(M):

        reference = modulate_symbol(symbol)

        correlation = abs(
            np.vdot(reference, received_symbol)
        )

        correlations.append(correlation)

    return np.argmax(correlations)


# ------------------------------------------------------------
# Receiver
# ------------------------------------------------------------

rx_symbols = []

for i in range(len(tx_symbols)):

    start = i * num_samples
    end = start + num_samples

    received_symbol = rx_signal[start:end]

    detected_symbol = demodulate_symbol(received_symbol)

    rx_symbols.append(detected_symbol)


rx_symbols = np.array(rx_symbols)


# ------------------------------------------------------------
# Results
# ------------------------------------------------------------

print("\nReceived symbols:")
print(rx_symbols)


if np.array_equal(tx_symbols, rx_symbols):

    print("\nRESULT: Transmission successful!")

else:

    print("\nRESULT: Symbol errors detected!")


# ------------------------------------------------------------
# Plot transmitted signal
# ------------------------------------------------------------

plt.figure(figsize=(10, 4))

plt.plot(
    np.real(tx_signal)
)

plt.xlabel("Sample")
plt.ylabel("Amplitude")

plt.title("Transmitted LoRa-like CSS Signal")

plt.grid()

plt.show()


# ------------------------------------------------------------
# Plot received signal
# ------------------------------------------------------------

plt.figure(figsize=(10, 4))

plt.plot(
    np.real(rx_signal)
)

plt.xlabel("Sample")
plt.ylabel("Amplitude")

plt.title("Received Signal with AWGN")

plt.grid()

plt.show()