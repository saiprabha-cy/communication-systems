from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

IQ_PATH = Path("data/iq/synthetic_df17.c64")
FS = 8_000_000


def main() -> None:
    if not IQ_PATH.exists():
        raise FileNotFoundError("Run src/signal_generator.py first.")

    iq = np.fromfile(IQ_PATH, dtype=np.complex64)
    time_us = np.arange(iq.size) / FS * 1e6
    amplitude = np.abs(iq)

    # Show the preamble and a short part of the data field.
    display_end = min(iq.size, round(20e-6 * FS))

    plt.figure(figsize=(12, 4))
    plt.step(
        time_us[:display_end],
        amplitude[:display_end],
        where="post",
        label="Magnitude |IQ|",
    )
    plt.axvline(8.0, linestyle="--", label="Payload begins (8 µs)")
    plt.xlabel("Time (µs)")
    plt.ylabel("Amplitude")
    plt.title("Synthetic Mode S preamble and payload")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    output = Path("plots/preamble.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=160)
    plt.show()

    print(f"Saved plot: {output}")


if __name__ == "__main__":
    main()