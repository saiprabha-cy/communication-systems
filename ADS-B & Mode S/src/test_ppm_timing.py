import numpy as np

from signal_generator import encode_ppm_bits

FS = 8_000_000


def decode_clean_ppm(envelope: np.ndarray, fs: int = FS) -> str:
    samples_per_slot = round(fs * 0.5e-6)
    samples_per_bit = 2 * samples_per_slot

    if envelope.size % samples_per_bit != 0:
        raise ValueError("Envelope length is not an integer number of bits.")

    recovered = []

    for start in range(0, envelope.size, samples_per_bit):
        first = envelope[start:start + samples_per_slot]
        second = envelope[
            start + samples_per_slot:start + samples_per_bit
        ]

        first_energy = float(np.sum(first ** 2))
        second_energy = float(np.sum(second ** 2))

        recovered.append("1" if first_energy > second_energy else "0")

    return "".join(recovered)


def main() -> None:
    transmitted = "1011000010110101"
    waveform = encode_ppm_bits(transmitted, FS)
    received = decode_clean_ppm(waveform, FS)

    print(f"Transmitted bits: {transmitted}")
    print(f"Received bits:    {received}")

    assert received == transmitted
    print("PASS: PPM bit timing and bit order match.")


if __name__ == "__main__":
    main()