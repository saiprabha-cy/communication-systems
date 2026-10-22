
import numpy as np

def qpsk_modulate(bits):
    bits = np.asarray(bits, dtype=np.uint8)
    pairs = bits.reshape(-1, 2)
    return (
        (1.0 - 2.0 * pairs[:, 0])
        + 1j * (1.0 - 2.0 * pairs[:, 1])
    ) / np.sqrt(2.0)


N = 64
CP = 16

bits = np.random.default_rng(7).integers(0, 2, 2 * N)
tx_symbols = qpsk_modulate(bits)

# Generate one OFDM symbol using unitary normalization
tx_time = np.fft.ifft(tx_symbols) * np.sqrt(N)

# Copy the last CP samples to the front
tx_with_cp = np.concatenate((tx_time[-CP:], tx_time))

# Simple multipath channel
h = np.array([
    1.0 + 0.0j,
    0.3 + 0.2j,
    0.1 - 0.1j
])

# Linear convolution models delayed channel paths
rx_with_channel = np.convolve(tx_with_cp, h)

# Extract the N useful samples after the prefix
rx_useful = rx_with_channel[CP:CP + N]

# Transform the received useful samples to frequency domain
rx_frequency = np.fft.fft(rx_useful) / np.sqrt(N)

# Channel frequency response for the N subcarriers
channel_frequency = np.fft.fft(h, N)

# One-tap zero-forcing equalization
rx_symbols = rx_frequency / channel_frequency

max_error = np.max(np.abs(tx_symbols - rx_symbols))

print("OFDM-05: Cyclic Prefix and Multipath")
print(f"Useful symbol samples : {N}")
print(f"Prefix samples        : {CP}")
print(f"Transmitted samples   : {len(tx_with_cp)}")
print(f"Channel taps          : {len(h)}")
print(f"Required CP for model : {len(h) - 1}")
print(f"Maximum symbol error  : {max_error:.3e}")

print("\nFirst five recovered symbols:")
for k in range(5):
    print(
        f"k={k}: TX={tx_symbols[k]:+.4f}, "
        f"RX={rx_symbols[k]:+.4f}"
    )
