import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from framer import frame_packet


def test_frame_structure():
    payload = b"\x01\x02\x03"

    frame = frame_packet(payload)

    assert frame[:2] == b"\xAA\x55"
    assert frame[2] == 3
    assert frame[3:] == payload


def test_frame_length():
    payload = b"\x10\x20\x30\x40"

    frame = frame_packet(payload)

    assert len(frame) == 2 + 1 + len(payload)