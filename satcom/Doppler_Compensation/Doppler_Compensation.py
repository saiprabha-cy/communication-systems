import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(13)

Fs = 100e3
Npre = 256
Ndata = 4000
cfo_hz = 1500.0
ebn0_db = 12.0

preamble_bits = np.ones(Npre, dtype=int)
data_bits = rng.integers(0, 2, Ndata)
bits = np.concatenate([preamble_bits, data_bits])

tx = 2 * bits - 1
n = np.arange(len(tx))

# Apply frequency offset
rx_cfo = tx * np.exp(1j * 2 * np.pi * cfo_hz * n / Fs)

# Add complex AWGN
gamma = 10 ** (ebn0_db / 10)
sigma = np.sqrt(1 / (2 * gamma))
noise = sigma * (
    rng.standard_normal(len(tx))
    + 1j * rng.standard_normal(len(tx))
)
rx = rx_cfo + noise

# Estimate using known preamble
pre = rx[:Npre]
phase_products = pre[1:] * np.conj(pre[:-1])
estimated_cfo = Fs / (2 * np.pi) * np.angle(np.sum(phase_products))

# Correct frequency offset
rx_corrected = rx * np.exp(-1j * 2 * np.pi * estimated_cfo * n / Fs)

payload = rx_corrected[Npre:]
detected_bits = (payload.real >= 0).astype(int)
ber = np.mean(detected_bits != data_bits)

print("SAT-13: DOPPLER COMPENSATION")
print(f"Actual offset:    {cfo_hz:.2f} Hz")
print(f"Estimated offset: {estimated_cfo:.2f} Hz")
print(f"Estimation error: {estimated_cfo - cfo_hz:.2f} Hz")
print(f"Payload BER:      {ber:.6g}")

fig, axes = plt.subplots(2, 1, figsize=(9, 6))

axes[0].plot(n[:500] / Fs, np.unwrap(np.angle(rx[:500])))
axes[0].set_title("Received Phase Before Compensation")
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Phase (rad)")
axes[0].grid(True)

axes[1].plot(n[:500] / Fs, np.unwrap(np.angle(rx_corrected[:500])))
axes[1].set_title("Received Phase After Compensation")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Phase (rad)")
axes[1].grid(True)

plt.tight_layout()
plt.show()