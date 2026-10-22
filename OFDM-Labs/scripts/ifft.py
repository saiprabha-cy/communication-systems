
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

# Two bits per QPSK symbol, one symbol per subcarrier
bits = np.array([
    0, 0, 0, 1, 1, 1, 1, 0,
    0, 0, 1, 1, 0, 1, 1, 0
], dtype=np.uint8)

frequency_symbols = qpsk_modulate(bits)

if len(frequency_symbols) != N:
    raise ValueError("Number of QPSK symbols must equal N.")

# Unitary-normalized IFFT
time_samples = np.fft.ifft(frequency_symbols) * np.sqrt(N)

print("OFDM-03: IFFT Transmitter")
print(f"Subcarriers: {N}")
print(f"Input QPSK symbols: {len(frequency_symbols)}")
print("\nTime-domain OFDM samples:")

for n, sample in enumerate(time_samples):
    print(f"x[{n}] = {sample.real:+.4f} "
          f"{sample.imag:+.4f}j")

print(f"\nAverage sample power: "
      f"{np.mean(np.abs(time_samples)**2):.4f}")

plt.figure()
plt.plot(np.arange(N), time_samples.real, marker="o",
         label="In-phase")
plt.plot(np.arange(N), time_samples.imag, marker="s",
         label="Quadrature")
plt.xlabel("Sample index")
plt.ylabel("Amplitude")
plt.title("OFDM-03: Time-Domain OFDM Symbol")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
