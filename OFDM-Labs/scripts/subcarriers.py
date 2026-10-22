
import numpy as np
import matplotlib.pyplot as plt

# OFDM parameters
N = 8
carrier_frequency_hz = 100_000.0
subcarrier_spacing_hz = 1_000.0

# Generate N equally spaced frequencies
k = np.arange(N)
frequencies_hz = (
    carrier_frequency_hz + k * subcarrier_spacing_hz
)

# Useful OFDM symbol duration
useful_symbol_duration_s = 1.0 / subcarrier_spacing_hz

print("OFDM-01: Generate Subcarriers")
print(f"Number of subcarriers : {N}")
print(f"Subcarrier spacing    : {subcarrier_spacing_hz:.0f} Hz")
print(f"Useful symbol duration: "
      f"{useful_symbol_duration_s * 1e3:.3f} ms")
print("\nSubcarrier frequencies:")

for index, frequency in enumerate(frequencies_hz):
    print(f"Subcarrier {index}: {frequency / 1000:.3f} kHz")

# Visualize subcarrier locations
plt.figure()
plt.stem(frequencies_hz / 1000, np.ones(N))
plt.xlabel("Frequency (kHz)")
plt.ylabel("Relative amplitude")
plt.title("OFDM-01: Subcarrier Frequency Locations")
plt.grid(True)
plt.tight_layout()
plt.show()
