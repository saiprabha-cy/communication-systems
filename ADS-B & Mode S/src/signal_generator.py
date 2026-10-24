from pathlib import Path

import numpy as np

FS = 8_000_000
SLOT_SECONDS = 0.5e-6
SAMPLES_PER_SLOT = round(FS * SLOT_SECONDS)
SAMPLES_PER_BIT = 2 * SAMPLES_PER_SLOT

# Mode S preamble pulses occupy these time windows, in microseconds:
# 0.0–0.5, 1.0–1.5, 3.5–4.0, and 4.5–5.0.
PREAMBLE_PULSE_WINDOWS_US = (
    (0.0, 0.5),
    (1.0, 1.5),
    (3.5, 4.0),
    (4.5, 5.0),
)


def make_preamble(fs: int = FS) -> np.ndarray:
    """Return an 8-microsecond real-valued envelope."""
    samples = round(fs * 8e-6)
    preamble = np.zeros(samples, dtype=np.float32)

    for start_us, end_us in PREAMBLE_PULSE_WINDOWS_US:
        start = round(start_us * 1e-6 * fs)
        end = round(end_us * 1e-6 * fs)
        preamble[start:end] = 1.0

    return preamble


def encode_ppm_bits(bits: str, fs: int = FS) -> np.ndarray:
    """
    Encode Mode S PPM bits as a real-valued envelope.

    Bit 1: pulse in the first half-microsecond slot.
    Bit 0: pulse in the second half-microsecond slot.
    """
    if any(bit not in "01" for bit in bits):
        raise ValueError("Input must contain only '0' and '1'.")

    samples_per_slot = round(fs * 0.5e-6)
    if samples_per_slot < 1:
        raise ValueError("Sample rate is too low for this representation.")

    output = np.zeros(len(bits) * 2 * samples_per_slot, dtype=np.float32)

    for index, bit in enumerate(bits):
        start = index * 2 * samples_per_slot
        pulse_start = start if bit == "1" else start + samples_per_slot
        output[pulse_start:pulse_start + samples_per_slot] = 1.0

    return output


def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        ch not in "0123456789ABCDEF" for ch in normalized
    ):
        raise ValueError("Frame must be a non-empty hexadecimal string.")

    return "".join(f"{int(ch, 16):04b}" for ch in normalized)


def make_frame_envelope(hex_frame: str, fs: int = FS) -> np.ndarray:
    bits = hex_to_bits(hex_frame)

    if len(bits) not in (56, 112):
        raise ValueError("Mode S frame must contain 56 or 112 bits.")

    preamble = make_preamble(fs)
    payload = encode_ppm_bits(bits, fs)

    # The preamble is 8 us, followed by the encoded message.
    return np.concatenate([preamble, payload])


def main() -> None:
    output_path = Path("data/iq/synthetic_df17.c64")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Reference frame used for the signal-processing exercise.
    frame_hex = "8D40621D58C382D690C8AC2863A7"
    envelope = make_frame_envelope(frame_hex)

    # A real, nonnegative envelope is a valid simple complex-baseband test
    # signal with Q=0. It is not a realistic RF channel model.
    iq = envelope.astype(np.complex64)

    iq.tofile(output_path)

    expected_samples = len(envelope)
    actual_bytes = output_path.stat().st_size

    print(f"Sample rate:       {FS:,} samples/s")
    print(f"Samples:           {expected_samples:,}")
    print(f"Complex dtype:     {iq.dtype}")
    print(f"Bytes per sample:  {np.dtype(np.complex64).itemsize}")
    print(f"File size:         {actual_bytes:,} bytes")
    print(f"Saved:             {output_path}")

    assert actual_bytes == expected_samples * 8


if __name__ == "__main__":
    main()