import numpy as np
import matplotlib.pyplot as plt

bits = np.array([0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0])

if len(bits) % 2:
    raise ValueError("QPSK requires an even number of bits.")

pairs = bits.reshape(-1, 2)
symbols = []

for b1, b2 in pairs:
    i_component = 1 - 2 * b2
    q_component = 1 - 2 * b1
    symbols.append((i_component + 1j*q_component) / np.sqrt(2))

symbols = np.array(symbols)

print("Bit pairs:\n", pairs)
print("QPSK symbols:\n", symbols)

plt.scatter(symbols.real, symbols.imag)
plt.xlabel("In-phase (I)")
plt.ylabel("Quadrature (Q)")
plt.title("SAT-09: QPSK Constellation")
plt.axis("equal")
plt.xlim(-1.5, 1.5)
plt.ylim(-1.5, 1.5)
plt.grid(True)
plt.show()