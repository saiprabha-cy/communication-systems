from datetime import datetime, timezone
from pathlib import Path
import json

import numpy as np

from preamble_detector import detect_preambles
from bit_slicer import slice_mode_s_bits
from modes_crc import check_df17_crc

FS = 8_000_000
IQ_PATH = Path("data/iq/synthetic_df17.c64")
OUTPUT_PATH = Path("reports/decoded_frames.jsonl")


def bits_to_hex(bits: str) -> str:
    if len(bits) % 4 != 0:
        raise ValueError("Bit string length must be a multiple of four.")
    return "".join(
        f"{int(bits[i:i + 4], 2):X}"
        for i in range(0, len(bits), 4)
    )


def decode_candidate(
    iq: np.ndarray,
    start_index: int,
    score: float,
    fs: int = FS,
) -> dict:
    preamble_samples = round(8e-6 * fs)
    samples_per_bit = round(1e-6 * fs)
    payload_start = start_index + preamble_samples
    payload_end = payload_start + 112 * samples_per_bit

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "start_sample": int(start_index),
        "start_time_seconds": float(start_index / fs),
        "preamble_score": float(score),
        "sample_rate_hz": fs,
        "frame_bits": 112,
        "frame_hex": None,
        "df": None,
        "icao": None,
        "crc_valid": False,
        "status": "rejected",
        "error": None,
    }

    if payload_end > iq.size:
        record["error"] = "Truncated payload"
        return record

    payload = iq[payload_start:payload_end]

    try:
        bits, confidence = slice_mode_s_bits(
            payload,
            fs=fs,
            number_of_bits=112,
        )

        frame = bits_to_hex(bits)
        record["frame_hex"] = frame
        record["minimum_bit_confidence"] = float(np.min(confidence))
        record["mean_bit_confidence"] = float(np.mean(confidence))

        df = int(bits[:5], 2)
        record["df"] = df

        if df != 17:
            record["status"] = "unsupported_df"
            record["error"] = f"DF={df}; this pipeline currently checks DF17"
            return record

        record["icao"] = f"{int(bits[8:32], 2):06X}"

        valid, calculated, received = check_df17_crc(frame)
        record["crc_calculated"] = f"{calculated:06X}"
        record["crc_received"] = f"{received:06X}"
        record["crc_valid"] = bool(valid)

        if valid:
            record["status"] = "crc_valid"
        else:
            record["status"] = "crc_failed"
            record["error"] = "DF17 CRC mismatch"

    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"

    return record


def main() -> None:
    if not IQ_PATH.exists():
        raise FileNotFoundError(
            "Run python src/signal_generator.py first."
        )

    iq = np.fromfile(IQ_PATH, dtype=np.complex64)
    starts, scores = detect_preambles(iq, fs=FS)

    records = [
        decode_candidate(iq, int(start), float(score), fs=FS)
        for start, score in zip(starts, scores)
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    valid_count = sum(record["crc_valid"] for record in records)

    print(f"Input: {IQ_PATH}")
    print(f"Candidates: {len(records)}")
    print(f"CRC-valid DF17: {valid_count}")
    print(f"Output: {OUTPUT_PATH}")

    for record in records:
        print(
            f"{record['status']:16s} "
            f"t={record['start_time_seconds']:.6f}s "
            f"DF={record['df']} "
            f"ICAO={record['icao']} "
            f"frame={record['frame_hex']}"
        )


if __name__ == "__main__":
    main()