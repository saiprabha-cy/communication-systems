from pathlib import Path
import json

import numpy as np

from preamble_detector import detect_preambles

IQ_PATH = Path("data/iq/synthetic_df17.c64")
FS = 8_000_000


def analyze_capture(path: Path, fs: int) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Generate a test recording first."
        )

    if fs <= 0:
        raise ValueError("Sample rate must be positive.")

    iq = np.fromfile(path, dtype=np.complex64)
    if iq.size == 0:
        raise ValueError("IQ recording is empty.")

    envelope = np.abs(iq)
    starts, scores = detect_preambles(iq, fs=fs)

    result = {
        "file": str(path),
        "sample_rate_hz": fs,
        "sample_count": int(iq.size),
        "duration_seconds": float(iq.size / fs),
        "bytes_on_disk": int(path.stat().st_size),
        "dtype": "complex64",
        "peak_amplitude": float(np.max(envelope)),
        "mean_power": float(np.mean(envelope ** 2)),
        "preamble_candidates": int(starts.size),
        "candidate_indices": starts.tolist(),
        "candidate_scores": scores.tolist(),
    }

    return result


def main() -> None:
    result = analyze_capture(IQ_PATH, FS)

    print(json.dumps(result, indent=2))

    report_path = Path("reports/capture_analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"\nSaved report: {report_path}")


if __name__ == "__main__":
    main()