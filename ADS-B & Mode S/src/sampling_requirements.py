SLOT_SECONDS = 0.5e-6
BIT_SECONDS = 1.0e-6
PREAMBLE_SECONDS = 8.0e-6


def samples_per_interval(sample_rate: int, interval_seconds: float) -> float:
    if sample_rate <= 0:
        raise ValueError("Sample rate must be positive.")
    return sample_rate * interval_seconds


def describe_rate(sample_rate: int) -> None:
    slot_samples = samples_per_interval(sample_rate, SLOT_SECONDS)
    bit_samples = samples_per_interval(sample_rate, BIT_SECONDS)
    preamble_samples = samples_per_interval(sample_rate, PREAMBLE_SECONDS)

    print(f"\nSample rate: {sample_rate / 1e6:.3f} MS/s")
    print(f"Samples per 0.5 µs slot: {slot_samples:g}")
    print(f"Samples per 1 µs bit:    {bit_samples:g}")
    print(f"Samples per preamble:    {preamble_samples:g}")

    if slot_samples < 1:
        print("WARNING: less than one sample per slot.")
    elif not slot_samples.is_integer():
        print("NOTE: a fixed-grid slicer needs timing/interpolation care.")
    else:
        print("Fixed-grid slot slicing is straightforward for this rate.")


def main() -> None:
    for rate in (1_000_000, 2_000_000, 4_000_000, 8_000_000, 12_000_000):
        describe_rate(rate)


if __name__ == "__main__":
    main()