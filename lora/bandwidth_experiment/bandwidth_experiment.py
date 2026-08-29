import numpy as np
import matplotlib.pyplot as plt


# --------------------------------------------------
# LoRa CSS Bandwidth Experiment
# --------------------------------------------------

# Common parameters
sf = 7
duration = 0.01          # 10 ms
sample_rate = 2_000_000  # 2 MHz


# Bandwidths to compare
bandwidths = [
    125_000,   # 125 kHz
    250_000,   # 250 kHz
    500_000    # 500 kHz
]


# Time vector
t = np.arange(0, duration, 1 / sample_rate)


plt.figure(figsize=(12, 7))


for bw in bandwidths:

    # Frequency sweep from -BW/2 to +BW/2
    f_start = -bw / 2
    f_end = bw / 2

    # Linear frequency sweep
    instantaneous_frequency = (
        f_start
        + (f_end - f_start) * (t / duration)
    )

    # Chirp rate
    k = bw / duration

    # Phase:
    # phi(t) = 2*pi*(f_start*t + 0.5*k*t^2)
    phase = 2 * np.pi * (
        f_start * t
        + 0.5 * k * t**2
    )

    # Complex baseband chirp
    chirp = np.exp(1j * phase)

    # Plot real component
    plt.plot(
        t * 1000,
        np.real(chirp),
        label=f"BW = {bw / 1000:.0f} kHz"
    )


plt.title("LoRa CSS Chirp — Bandwidth Comparison")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")

plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()


# --------------------------------------------------
# Numerical comparison
# --------------------------------------------------

print("\nBandwidth Experiment")
print("--------------------")

for bw in bandwidths:

    chirp_rate = bw / duration

    print(
        f"BW = {bw / 1000:.0f} kHz"
        f" -> Chirp rate = {chirp_rate / 1e6:.2f} MHz/s"
    )