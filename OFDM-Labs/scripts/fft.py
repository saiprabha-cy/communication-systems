
import numpy as np
import matplotlib.pyplot as plt

def qpsk_modulate(bits):
    bits = np.asarray(bits, dtype=np.uint8)
    if bits.ndim != 1 or len(bits) % 2 != 0:
        raise ValueError("Provide an even number of bits.")

    pairs = bits.reshape(-1, 2)
    i = 1.0 - 2.0 * pairs[:, 0]
    q = 1.0 - 2.0 * pairs[:, 1]

    return (i + 1j * q) / np.sqrt(2.0)


N = 8

tx_bits = np.array([
    0, 0, 0, 1, 1, 1, 1, 0,
    0, 0, 1, 1, 0, 1, 1, 0
], dtype=np.uint8)

tx_symbols = qpsk_modulate(tx_bits)

# Transmitter: frequency domain -> time domain
tx_time = np.fft.ifft(tx_symbols) * np.sqrt(N)

# Ideal channel: no noise, fading, or timing error
rx_time = tx_time.copy()

# Receiver: time domain -> frequency domain
rx_symbols = np.fft.fft(rx_time) / np.sqrt(N)

max_error = np.max(np.abs(tx_symbols - rx_symbols))

print("OFDM-04: FFT Receiver")
print("\nOriginal and recovered symbols:")

for k, (tx, rx) in enumerate(zip(tx_symbols, rx_symbols)):
    print(
        f"k={k}: TX={tx.real:+.3f}{tx.imag:+.3f}j, "
        f"RX={rx.real:+.3f}{rx.imag:+.3f}j"
    )

print(f"\nMaximum symbol error: {max_error:.3e}")

plt.figure()
plt.scatter(tx_symbols.real, tx_symbols.imag,
            marker="o", label="Transmitted")
plt.scatter(rx_symbols.real, rx_symbols.imag,
            marker="x", label="Received")
plt.xlabel("In-phase (I)")
plt.ylabel("Quadrature (Q)")
plt.title("OFDM-04: Transmitted versus Received Symbols")
plt.grid(True)
plt.axis("equal")
plt.legend()
plt.tight_layout()
plt.show()
