
import numpy as np
import matplotlib.pyplot as plt

def qpsk_modulate(bits):
    bits = np.asarray(bits, dtype=np.uint8)

    if bits.ndim != 1 or len(bits) % 2 != 0:
        raise ValueError("QPSK needs a 1D array with an even number of bits.")

    if np.any(bits > 1):
        raise ValueError("Bits must contain only 0 or 1.")

    bit_pairs = bits.reshape(-1, 2)

    # Gray-coded mapping:
    # 00 -> (+1,+1)
    # 01 -> (+1,-1)
    # 10 -> (-1,+1)
    # 11 -> (-1,-1)
    i_component = 1.0 - 2.0 * bit_pairs[:, 0]
    q_component = 1.0 - 2.0 * bit_pairs[:, 1]

    return (i_component + 1j * q_component) / np.sqrt(2.0)


bits = np.array([
    0, 0,
    0, 1,
    1, 1,
    1, 0
], dtype=np.uint8)

symbols = qpsk_modulate(bits)

print("OFDM-02: QPSK Modulation")
print(f"Input bits: {bits.tolist()}")
print(f"Number of input bits: {len(bits)}")
print(f"Number of QPSK symbols: {len(symbols)}\n")

for i, symbol in enumerate(symbols):
    print(f"Symbol {i}: {symbol.real:+.3f} "
          f"{symbol.imag:+.3f}j")

plt.figure()
plt.scatter(symbols.real, symbols.imag)
plt.axhline(0)
plt.axvline(0)
plt.xlabel("In-phase (I)")
plt.ylabel("Quadrature (Q)")
plt.title("OFDM-02: QPSK Constellation")
plt.grid(True)
plt.axis("equal")
plt.tight_layout()
plt.show()
