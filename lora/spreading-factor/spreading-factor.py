import numpy as np
import matplotlib.pyplot as plt


# --------------------------------------------------
# LoRa Spreading Factor Experiment
# --------------------------------------------------

BANDWIDTH = 125_000       # 125 kHz
SAMPLE_RATE = 1_000_000   # 1 MHz


def generate_chirp(sf, bandwidth, sample_rate):
    """
    Generate one simplified baseband upchirp.

    SF determines the number of chips/samples
    representing one symbol in this simplified model.
    """

    chips_per_symbol = 2 ** sf

    # Symbol duration:
    symbol_duration = chips_per_symbol / bandwidth

    # Number of samples for visualization
    num_samples = int(symbol_duration * sample_rate)

    t = np.arange(num_samples) / sample_rate

    # Chirp frequency sweep
    f_start = -bandwidth / 2
    f_end = bandwidth / 2

    k = (f_end - f_start) / symbol_duration

    phase = 2 * np.pi * (
        f_start * t + 0.5 * k * t**2
    )

    chirp = np.exp(1j * phase)

    return t, chirp, symbol_duration


# --------------------------------------------------
# Compare different spreading factors
# --------------------------------------------------

spreading_factors = [7, 8, 9, 10, 11, 12]

for sf in spreading_factors:

    t, chirp, symbol_duration = generate_chirp(
        sf,
        BANDWIDTH,
        SAMPLE_RATE
    )

    chips = 2 ** sf

    symbol_rate = BANDWIDTH / chips

    print(
        f"SF{sf}: "
        f"chips/symbol = {chips}, "
        f"symbol duration = {symbol_duration * 1000:.3f} ms, "
        f"symbol rate = {symbol_rate:.2f} symbols/s"
    )


# --------------------------------------------------
# Visual comparison
# --------------------------------------------------

plt.figure(figsize=(12, 8))

for sf in [7, 9, 12]:

    t, chirp, symbol_duration = generate_chirp(
        sf,
        BANDWIDTH,
        SAMPLE_RATE
    )

    plt.plot(
        t * 1000,
        np.real(chirp),
        label=f"SF{sf}"
    )


plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("LoRa CSS Chirp — Spreading Factor Comparison")
plt.legend()
plt.grid(True)

plt.show()