import numpy as np
import matplotlib.pyplot as plt

bits = np.array([1, 0, 1, 1, 0, 0, 1, 0])

# BPSK mapping: 0 -> -1, 1 -> +1
symbols = 2 * bits - 1

print("Input bits:", bits)
print("BPSK symbols:", symbols)

plt.stem(np.arange(len(symbols)), symbols)
plt.xlabel("Symbol index")
plt.ylabel("BPSK amplitude")
plt.title("SAT-08: BPSK Symbol Mapping")
plt.ylim(-1.5, 1.5)
plt.grid(True)
plt.show()