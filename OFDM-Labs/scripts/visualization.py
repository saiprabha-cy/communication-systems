
import numpy as np
import matplotlib.pyplot as plt

def qpsk_modulate(bits):
    bits = np.asarray(bits, dtype=np.uint8)
    pairs = bits.reshape(-1, 2)

    i = 1.0 - 2.0 * pairs[:, 0]
    q = 1.0 - 2.0 * pairs[:, 1]

    return (i + 1j * q) / np.sqrt(2.0)


rng = np.random.default_rng(7)

N = 8
subcarrier_spacing_hz = 1000.0
useful_symbol_duration_s = 1.0 / subcarrier_spacing_hz

# One QPSK symbol per subcarrier
bits = rng.integers(0, 2, 2 * N, dtype=np.uint8)
symbols = qpsk_modulate(bits)

# IFFT: construct the discrete-time OFDM symbol
x = np.fft.ifft(symbols) * np.sqrt(N)

# Oversampled baseband waveform for visualization
samples_per_symbol = 128
t = np.arange(N * samples_per_symbol) * (
    useful_symbol_duration_s / (N * samples_per_symbol)
)

# Complex exponential representation of the same OFDM symbol
subcarrier_indices = np.arange(N)
frequencies_hz = subcarrier_indices * subcarrier_spacing_hz

waveform = np.zeros_like(t, dtype=complex)

for k, symbol in enumerate(symbols):
    waveform += (
        symbol
        * np.exp(2j * np.pi * frequencies_hz[k] * t)
    )

waveform /= np.sqrt(N)

# Analytical magnitude response of rectangularly windowed carriers
frequency_axis_hz = np.linspace(
    -4.5 * subcarrier_spacing_hz,
    (N + 0.5) * subcarrier_spacing_hz,
    6000
)

individual_spectra = []
for k, symbol in enumerate(symbols):
    offset = (
        frequency_axis_hz - frequencies_hz[k]
    ) * useful_symbol_duration_s

    individual_spectra.append(
        np.abs(symbol) * np.abs(np.sinc(offset))
    )

# Composite spectrum of the finite-duration OFDM symbol
composite_spectrum = np.zeros_like(
    frequency_axis_hz, dtype=complex
)

for k, symbol in enumerate(symbols):
    offset = (
        frequency_axis_hz - frequencies_hz[k]
    ) * useful_symbol_duration_s

    phase = np.exp(-1j * np.pi * offset)

    composite_spectrum += (
        symbol
        * useful_symbol_duration_s
        * phase
        * np.sinc(offset)
    )

print("OFDM-07: Subcarrier Visualization")
print(f"Subcarriers: {N}")
print(f"Spacing: {subcarrier_spacing_hz:.0f} Hz")
print(f"Useful symbol duration: "
      f"{useful_symbol_duration_s * 1e3:.3f} ms")

# Plot 1: frequency-domain subcarrier allocation
plt.figure()
plt.stem(
    frequencies_hz / 1000,
    np.abs(symbols),
    basefmt=" "
)
plt.xlabel("Baseband frequency (kHz)")
plt.ylabel("Subcarrier symbol magnitude")
plt.title("OFDM-07: Allocated Subcarriers")
plt.grid(True)
plt.tight_layout()

# Plot 2: overlapping individual spectra and composite spectrum
plt.figure()
for k, spectrum in enumerate(individual_spectra):
    plt.plot(
        frequency_axis_hz / 1000,
        spectrum,
        linestyle="--",
        alpha=0.5,
        label=f"Carrier {k}" if k < 4 else None
    )

plt.plot(
    frequency_axis_hz / 1000,
    np.abs(composite_spectrum),
    label="Composite OFDM spectrum",
    linewidth=2
)
plt.xlabel("Baseband frequency (kHz)")
plt.ylabel("Relative magnitude")
plt.title("OFDM-07: Overlapping Subcarrier Spectra")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Plot 3: time-domain I and Q waveforms
plt.figure()
plt.plot(t * 1e3, waveform.real, label="I component")
plt.plot(t * 1e3, waveform.imag, label="Q component")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("OFDM-07: Time-Domain Waveform")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Plot 4: frequency-domain QPSK constellation
plt.figure()
plt.scatter(symbols.real, symbols.imag)
for k, symbol in enumerate(symbols):
    plt.annotate(str(k), (symbol.real, symbol.imag))

plt.xlabel("In-phase (I)")
plt.ylabel("Quadrature (Q)")
plt.title("OFDM-07: QPSK Symbols on Subcarriers")
plt.grid(True)
plt.axis("equal")
plt.tight_layout()

plt.show()
