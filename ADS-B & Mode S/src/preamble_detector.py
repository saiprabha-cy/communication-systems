from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

FS = 8_000_000
IQ_PATH = Path("data/iq/synthetic_df17.c64")

PREAMBLE_US = 8.0
SLOT_S = 0.5e-6
BIT_S = 1.0e-6

PULSE_WINDOWS_US = (
    (0.0, 0.5),
    (1.0, 1.5),
    (3.5, 4.0),
    (4.5, 5.0),
)


def make_preamble_template(fs: int) -> np.ndarray:
    count = round(PREAMBLE_US * 1e-6 * fs)
    template = np.zeros(count, dtype=np.float32)

    for start_us, end_us in PULSE_WINDOWS_US:
        start = round(start_us * 1e-6 * fs)
        end = round(end_us * 1e-6 * fs)
        template[start:end] = 1.0

    return template


def detect_preambles(
    iq: np.ndarray,
    fs: int = FS,
    threshold: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (candidate_start_indices, normalized_scores).

    The score is template correlation divided by the maximum possible
    correlation for a unit-amplitude ideal preamble. This is a teaching
    detector, not a calibrated probability of a valid Mode S frame.
    """
    if iq.ndim != 1:
        raise ValueError("IQ data must be a one-dimensional array.")

    envelope = np.abs(iq).astype(np.float32)
    template = make_preamble_template(fs)
    template_energy = float(np.sum(template))

    if envelope.size < template.size:
        return np.array([], dtype=int), np.array([], dtype=float)

    correlation = np.correlate(envelope, template, mode="valid")
    scores = correlation / max(template_energy, 1e-12)

    # One preamble lasts 8 us; use a spacing that avoids many detections
    # on the same pulse pattern.
    minimum_distance = max(1, round(6e-6 * fs))
    peaks, properties = find_peaks(
        scores,
        height=threshold,
        distance=minimum_distance,
    )

    # Include index 0 if it is a peak-like candidate. scipy.find_peaks
    # does not consider endpoints.
    if scores[0] >= threshold and (
        peaks.size == 0 or peaks[0] != 0
    ):
        peaks = np.insert(peaks, 0, 0)

    peak_scores = scores[peaks]
    return peaks.astype(int), peak_scores


def extract_candidate_frames(
    iq: np.ndarray,
    start_indices: np.ndarray,
    fs: int = FS,
    frame_bits: int = 112,
) -> list[np.ndarray]:
    preamble_samples = round(PREAMBLE_US * 1e-6 * fs)
    samples_per_bit = round(BIT_S * fs)
    frame_samples = frame_bits * samples_per_bit
    candidates = []

    for start in start_indices:
        payload_start = int(start) + preamble_samples
        payload_end = payload_start + frame_samples

        if payload_end <= iq.size:
            candidates.append(iq[payload_start:payload_end])

    return candidates


def main() -> None:
    if not IQ_PATH.exists():
        raise FileNotFoundError(
            "Run python src/signal_generator.py first."
        )

    iq = np.fromfile(IQ_PATH, dtype=np.complex64)
    starts, scores = detect_preambles(iq)

    print(f"Input samples: {iq.size:,}")
    print(f"Candidate preambles: {len(starts)}")

    for index, score in zip(starts, scores):
        print(
            f"Candidate at sample {index:8d} "
            f"({index / FS * 1e6:8.3f} µs), score={score:.3f}"
        )

    frames = extract_candidate_frames(iq, starts)

    print(f"Complete 112-bit-sized payload windows: {len(frames)}")
    for i, frame in enumerate(frames):
        print(f"Candidate {i}: {frame.size:,} complex samples")

    if starts.size:
        print("Preamble candidates found; parity validation is still required.")


if __name__ == "__main__":
    main()