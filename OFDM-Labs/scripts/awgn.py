
import math
import numpy as np
import matplotlib.pyplot as plt

def qpsk_modulate(bits):
    bits = np.asarray(bits, dtype=np.uint8)
    pairs = bits.reshape(-1, 2)

    i = 1.0 - 2.0 * pairs[:, 0]
    q = 1.0 - 2.0 * pairs[:, 1]

    return (i + 1j * q) / np.sqrt(2.0)


def qpsk_demodulate(symbols):
    bits = np.empty(2 * len(symbols), dtype=np.uint8)

    # Inverse of the mapping used above
    bits[0::2] = (symbols.real < 0).astype(np.uint8)
    bits[1::2] = (symbols.imag < 0).astype(np.uint8)

    return bits


def ofdm_transmit(bits, n_subcarriers, cp_length):
    symbols = qpsk_modulate(bits)
    symbols = symbols.reshape(-1, n_subcarriers)

    # Each row is one OFDM symbol in frequency domain
    time_symbols = (
        np.fft.ifft(symbols, axis=1) * np.sqrt(n_subcarriers)
    )

    # Add a cyclic prefix to every OFDM symbol
    with_cp = np.concatenate(
        (time_symbols[:, -cp_length:], time_symbols),
        axis=1
    )

    return with_cp


def theoretical_qpsk_ber(es_n0_db):
    # Gray-coded QPSK in AWGN:
    # BER = 0.5 * erfc(sqrt(Es/N0 / 2))
    es_n0_linear = 10 ** (es_n0_db / 10.0)
    return 0.5 * math.erfc(math.sqrt(es_n0_linear / 2.0))


rng = np.random.default_rng(2026)

N = 64
CP = 16
number_of_ofdm_symbols = 1000

number_of_bits = 2 * N * number_of_ofdm_symbols
tx_bits = rng.integers(0, 2, number_of_bits, dtype=np.uint8)

tx_with_cp = ofdm_transmit(tx_bits, N, CP)

snr_db_values = np.array([0, 2, 4, 6, 8, 10])
measured_ber = []
theoretical_ber = []

print("OFDM-06: OFDM over AWGN")
print(f"Subcarriers       : {N}")
print(f"Cyclic prefix     : {CP} samples")
print(f"OFDM symbols      : {number_of_ofdm_symbols}")
print(f"Input bits        : {number_of_bits}\n")

for snr_db in snr_db_values:
    snr_linear = 10 ** (snr_db / 10.0)

    # Complex AWGN: total complex noise variance = 1/SNR
    noise_variance = 1.0 / snr_linear
    noise = np.sqrt(noise_variance / 2.0) * (
        rng.standard_normal(tx_with_cp.shape)
        + 1j * rng.standard_normal(tx_with_cp.shape)
    )

    rx_with_cp = tx_with_cp + noise

    # Remove CP from each received OFDM symbol
    rx_useful = rx_with_cp[:, CP:CP + N]

    # FFT receiver
    rx_symbols = np.fft.fft(rx_useful, axis=1) / np.sqrt(N)
    rx_symbols = rx_symbols.reshape(-1)

    rx_bits = qpsk_demodulate(rx_symbols)

    bit_errors = np.count_nonzero(tx_bits != rx_bits)
    ber = bit_errors / number_of_bits

    measured_ber.append(ber)
    theoretical_ber.append(theoretical_qpsk_ber(snr_db))

    print(
        f"Es/N0={snr_db:2d} dB | "
        f"errors={bit_errors:5d} | BER={ber:.6f}"
    )

# BER comparison plot
plt.figure()
measured = np.array(measured_ber)
theory = np.array(theoretical_ber)

# A zero measured BER cannot be displayed on a logarithmic axis.
measured_for_plot = np.where(measured == 0, np.nan, measured)

plt.semilogy(snr_db_values, measured_for_plot, "o-",
             label="Simulated OFDM")
plt.semilogy(snr_db_values, theory, "s--",
             label="Theoretical Gray-coded QPSK")

plt.xlabel("Es/N0 (dB)")
plt.ylabel("Bit error rate (BER)")
plt.title("OFDM-06: BER over AWGN")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()
