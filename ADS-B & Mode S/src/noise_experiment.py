import numpy as np


def encode_ppm(bits: str, samples_per_slot: int = 4) -> np.ndarray:
    envelope = np.zeros(
        len(bits) * 2 * samples_per_slot,
        dtype=np.float64,
    )

    for i, bit in enumerate(bits):
        if bit not in "01":
            raise ValueError("Bits must contain only 0 and 1.")

        start = i * 2 * samples_per_slot
        pulse_start = start if bit == "1" else start + samples_per_slot
        envelope[pulse_start:pulse_start + samples_per_slot] = 1.0

    return envelope


def slice_ppm(
    samples: np.ndarray,
    number_of_bits: int,
    samples_per_slot: int = 4,
) -> str:
    samples_per_bit = 2 * samples_per_slot
    required = number_of_bits * samples_per_bit

    if samples.size < required:
        raise ValueError("Signal is too short.")

    bits = []

    for i in range(number_of_bits):
        start = i * samples_per_bit
        first = samples[start:start + samples_per_slot]
        second = samples[
            start + samples_per_slot:start + samples_per_bit
        ]

        first_energy = np.sum(first ** 2)
        second_energy = np.sum(second ** 2)

        bits.append("1" if first_energy > second_energy else "0")

    return "".join(bits)


def add_awgn(
    signal: np.ndarray,
    noise_std: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if noise_std < 0:
        raise ValueError("Noise standard deviation cannot be negative.")

    noise = rng.normal(0.0, noise_std, size=signal.size)
    return signal + noise


def main() -> None:
    rng = np.random.default_rng(20261024)

    transmitted = (
        "10110010100101101001010110100101"
        "11100010101011010100100101101010"
    )
    clean = encode_ppm(transmitted)

    print(f"Bits tested: {len(transmitted)}")
    print("Noise std | Bit errors | BER")
    print("--------------------------------")

    for noise_std in (0.0, 0.1, 0.25, 0.5, 0.8, 1.2):
        noisy = add_awgn(clean, noise_std, rng)
        recovered = slice_ppm(noisy, len(transmitted))

        errors = sum(a != b for a, b in zip(transmitted, recovered))
        ber = errors / len(transmitted)

        print(f"{noise_std:8.2f} | {errors:10d} | {ber:.4f}")

        if noise_std == 0.0:
            assert errors == 0

    print("\nPASS: the clean signal is decoded without bit errors.")


if __name__ == "__main__":
    main()