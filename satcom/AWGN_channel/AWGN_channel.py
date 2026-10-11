import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(10)

N = 2000
ebn0_db = 4.0

bits = rng.integers(0, 2, N)
tx = 2 * bits - 1  # 0 -> -1, 1 -> +1

ebn0 = 10 ** (ebn0_db / 10)
noise_sigma = np.sqrt(1 / (2 * ebn0))

noise = noise_sigma * rng.standard_normal(N)
rx = tx + noise

detected_bits = (rx >= 0).astype(int)
errors = np.count_nonzero(detected_bits != bits)
measured_ber = errors / N

print("SAT-10: AWGN CHANNEL")
print(f"Eb/N0: {ebn0_db:.2f} dB")
print(f"Noise standard deviation: {noise_sigma:.5f}")
print(f"Bit errors: {errors} of {N}")
print(f"Measured BER: {measured_ber:.6f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

axes[0].stem(np.arange(40), tx[:40])
axes[0].set_title("Transmitted BPSK symbols")
axes[0].set_xlabel("Symbol index")
axes[0].set_ylabel("Amplitude")
axes[0].grid(True)

axes[1].scatter(rx[:500], np.zeros(500), s=12)
axes[1].set_title("Received symbols after AWGN")
axes[1].set_xlabel("Received in-phase value")
axes[1].set_ylabel("Quadrature value")
axes[1].grid(True)

plt.tight_layout()
plt.show()