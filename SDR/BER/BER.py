
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

rng = np.random.default_rng(2026)

N = 200_000
bits = rng.integers(0, 2, N)
symbols = 2.0 * bits - 1.0

ebn0_db_values = np.arange(0, 11, 2)
measured_ber = []
theoretical_ber = []

for ebn0_db in ebn0_db_values:
    ebn0 = 10 ** (ebn0_db / 10)

    # Real AWGN variance for unit-energy BPSK
    sigma = np.sqrt(1 / (2 * ebn0))
    received = symbols + rng.normal(0, sigma, N)

    decoded = (received >= 0).astype(int)
    errors = np.count_nonzero(decoded != bits)
    measured_ber.append(errors / N)

    # Theoretical coherent BPSK BER in AWGN
    theoretical_ber.append(0.5 * erfc(np.sqrt(ebn0)))

    print(
        f"Eb/N0={ebn0_db:2d} dB | "
        f"errors={errors:5d} | BER={errors/N:.6g}"
    )

plt.figure(figsize=(8, 5))
plt.semilogy(ebn0_db_values, measured_ber, "o-", label="Simulation")
plt.semilogy(
    ebn0_db_values, theoretical_ber, "s--",
    label="Theory: coherent BPSK in AWGN"
)
plt.xlabel("Eb/N0 (dB)")
plt.ylabel("BER")
plt.title("BPSK bit-error performance")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()
