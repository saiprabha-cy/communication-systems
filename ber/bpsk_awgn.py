import numpy as np

# -----------------------------
# Configuration
# -----------------------------
NUM_BITS = 100_000
EB_N0_DB = -2

# Reproducible random numbers
rng = np.random.default_rng(42)

# -----------------------------
# 1. Generate random bits
# -----------------------------
bits_tx = rng.integers(0, 2, NUM_BITS)

# -----------------------------
# 2. BPSK modulation
#    0 -> -1
#    1 -> +1
# -----------------------------
symbols = 2 * bits_tx - 1

# -----------------------------
# 3. Convert Eb/N0 from dB
# -----------------------------
eb_n0 = 10 ** (EB_N0_DB / 10)

# BPSK with Eb = 1
noise_std = np.sqrt(1 / (2 * eb_n0))

# -----------------------------
# 4. Generate AWGN
# -----------------------------
noise = rng.normal(
    0,
    noise_std,
    NUM_BITS
)

# -----------------------------
# 5. Channel
# -----------------------------
received = symbols + noise

# -----------------------------
# 6. BPSK decision
# -----------------------------
bits_rx = (received >= 0).astype(int)

# -----------------------------
# 7. Count errors
# -----------------------------
errors = np.sum(bits_tx != bits_rx)

ber = errors / NUM_BITS

print("\nFirst 10 transmitted bits:")
print(bits_tx[:10])

print("\nFirst 10 BPSK symbols:")
print(symbols[:10])

print("\nFirst 10 noise samples:")
print(noise[:10])

print("\nFirst 10 received symbols:")
print(received[:10])

print("\nFirst 10 received bits:")
print(bits_rx[:10])

# -----------------------------
# 8. Display results
# -----------------------------
print("----- BPSK over AWGN -----")
print(f"Eb/N0       : {EB_N0_DB} dB")
print(f"Total bits  : {NUM_BITS}")
print(f"Errors      : {errors}")
print(f"BER         : {ber:.6f}")
