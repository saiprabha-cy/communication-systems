import math
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(11)

ebn0_db = np.arange(0, 13, 2)
n_bits = 200_000

ber_bpsk = []
ber_qpsk = []
ber_theory = []

for db in ebn0_db:
    gamma = 10 ** (db / 10)

    # BPSK
    bits_b = rng.integers(0, 2, n_bits)
    tx_b = 2 * bits_b - 1

    sigma_b = math.sqrt(1 / (2 * gamma))
    rx_b = tx_b + sigma_b * rng.standard_normal(n_bits)

    detected_b = (rx_b >= 0).astype(int)
    ber_bpsk.append(np.mean(detected_b != bits_b))

    # QPSK: same Gray mapping as SAT-09
    bits_q = rng.integers(0, 2, n_bits)
    pairs = bits_q.reshape(-1, 2)

    i_component = 1 - 2 * pairs[:, 1]
    q_component = 1 - 2 * pairs[:, 0]
    tx_q = (i_component + 1j * q_component) / math.sqrt(2)

    # Unit symbol energy, two bits per symbol
    sigma_q = math.sqrt(1 / (4 * gamma))
    noise = sigma_q * (
        rng.standard_normal(len(tx_q))
        + 1j * rng.standard_normal(len(tx_q))
    )
    rx_q = tx_q + noise

    detected_pairs = np.empty_like(pairs)
    detected_pairs[:, 1] = (rx_q.real < 0).astype(int)
    detected_pairs[:, 0] = (rx_q.imag < 0).astype(int)

    detected_q = detected_pairs.reshape(-1)
    ber_qpsk.append(np.mean(detected_q != bits_q))

    # Ideal coherent BPSK/QPSK BER over AWGN
    ber_theory.append(
        0.5 * math.erfc(math.sqrt(gamma))
    )

print("Eb/N0(dB)   BPSK BER       QPSK BER       Theory BER")

for db, b, q, theory in zip(
    ebn0_db, ber_bpsk, ber_qpsk, ber_theory
):
    print(f"{db:8.1f}   {b:12.6g}   {q:12.6g}   {theory:12.6g}")

plt.semilogy(ebn0_db, ber_bpsk, "o-", label="BPSK simulated")
plt.semilogy(ebn0_db, ber_qpsk, "s-", label="QPSK simulated")
plt.semilogy(ebn0_db, ber_theory, "--", label="Ideal theory")

plt.xlabel("Eb/N0 (dB)")
plt.ylabel("Bit Error Rate (BER)")
plt.title("SAT-11: BER vs Eb/N0 over AWGN")
plt.grid(True, which="both")
plt.legend()
plt.ylim(1e-6, 1)
plt.show()