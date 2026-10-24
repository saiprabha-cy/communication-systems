
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
N = 100_000
bits = rng.integers(0, 2, N)

# Map 0 -> -1 and 1 -> +1
symbols = 2 * bits - 1

eb_n0_db = 6
eb_n0 = 10 ** (eb_n0_db / 10)
noise_sigma = np.sqrt(1 / (2 * eb_n0))

received = symbols + rng.normal(0, noise_sigma, N)
decoded = (received >= 0).astype(int)

ber = np.mean(decoded != bits)
print("Eb/N0:", eb_n0_db, "dB")
print("Bits:", N)
print("Bit errors:", np.sum(decoded != bits))
print("Measured BER:", ber)

plt.figure(figsize=(8, 4))
plt.hist(received[::100], bins=80)
plt.xlabel("Received symbol value")
plt.ylabel("Count")
plt.title("BPSK symbol distributions with noise")
plt.grid(True)
plt.tight_layout()
plt.show()
