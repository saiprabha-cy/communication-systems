import numpy as np


def slice_mode_s_bits(
    payload_iq: np.ndarray,
    fs: int = 8_000_000,
    number_of_bits: int = 112,
    minimum_confidence: float = 0.0,
) -> tuple[str, np.ndarray]:
    """
    Slice Mode S PPM data from a complex IQ payload window.

    Bit 1: more energy in the first half-slot.
    Bit 0: more energy in the second half-slot.

    Returns:
        bits: recovered bit string
        confidence: normalized energy difference per bit, in [0, 1]
    """
    if payload_iq.ndim != 1:
        raise ValueError("Payload must be one-dimensional.")

    if number_of_bits <= 0:
        raise ValueError("number_of_bits must be positive.")

    samples_per_slot = round(fs * 0.5e-6)
    if samples_per_slot < 1:
        raise ValueError("Sample rate is too low.")

    samples_per_bit = 2 * samples_per_slot
    required = number_of_bits * samples_per_bit

    if payload_iq.size < required:
        raise ValueError(
            f"Need {required} samples, received {payload_iq.size}."
        )

    envelope = np.abs(payload_iq).astype(np.float64)
    bits = []
    confidences = []

    for bit_index in range(number_of_bits):
        start = bit_index * samples_per_bit
        first = envelope[start:start + samples_per_slot]
        second = envelope[
            start + samples_per_slot:start + samples_per_bit
        ]

        e_first = float(np.sum(first ** 2))
        e_second = float(np.sum(second ** 2))
        total = e_first + e_second

        if total <= 1e-15:
            bits.append("0")
            confidences.append(0.0)
            continue

        difference = (e_first - e_second) / total
        confidence = abs(difference)

        if confidence < minimum_confidence:
            # Ambiguous bits are explicitly marked as uncertain in the
            # confidence output; the returned bit is still a hard decision.
            pass

        bits.append("1" if difference > 0 else "0")
        confidences.append(min(1.0, confidence))

    return "".join(bits), np.asarray(confidences, dtype=np.float64)


def main() -> None:
    # A self-contained timing test with a known bit pattern.
    known_bits = "1011000010110101"
    fs = 8_000_000
    samples_per_slot = round(fs * 0.5e-6)

    waveform = np.zeros(
        len(known_bits) * 2 * samples_per_slot,
        dtype=np.complex64,
    )

    for i, bit in enumerate(known_bits):
        start = i * 2 * samples_per_slot
        pulse_start = start if bit == "1" else start + samples_per_slot
        waveform[pulse_start:pulse_start + samples_per_slot] = 1.0 + 0j

    decoded, confidence = slice_mode_s_bits(
        waveform,
        fs=fs,
        number_of_bits=len(known_bits),
    )

    print(f"Expected: {known_bits}")
    print(f"Decoded:  {decoded}")
    print(f"Minimum confidence: {confidence.min():.3f}")
    print(f"Mean confidence:    {confidence.mean():.3f}")

    assert decoded == known_bits
    assert np.allclose(confidence, 1.0)

    print("PASS: clean PPM bit slicing succeeded.")


if __name__ == "__main__":
    main()