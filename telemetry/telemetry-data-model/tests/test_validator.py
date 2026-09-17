import sys
from pathlib import Path

# Add 'src' directory to Python module search path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from framer import frame_packet
from validator import validate_packet
from crc import crc16_ccitt


def add_crc(frame_without_crc: bytes) -> bytes:
    payload_length = frame_without_crc[2]

    payload = frame_without_crc[
        3:3 + payload_length
    ]

    crc = crc16_ccitt(payload)

    return frame_without_crc + crc.to_bytes(2, "little")


def test_valid_packet():

    payload = bytes.fromhex(
        "01 00 00 00 68 9E 00 73 01 52 00 E9 03"
    )

    frame = frame_packet(payload)

    frame_with_crc = add_crc(frame)

    assert validate_packet(frame_with_crc)

def test_corrupted_packet():

    payload = bytes.fromhex(
        "01 00 00 00 68 9E 00 73 01 52 00 E9 03"
    )

    frame = frame_packet(payload)
    frame_with_crc = add_crc(frame)

    corrupted = bytearray(frame_with_crc)

    corrupted[5] ^= 0x01

    assert not validate_packet(bytes(corrupted))

def test_wrong_length():

    payload = bytes.fromhex(
        "01 00 00 00 68 9E 00 73 01 52 00 E9 03"
    )

    frame = frame_packet(payload)
    frame_with_crc = add_crc(frame)

    corrupted = bytearray(frame_with_crc)

    corrupted[2] = 12

    assert not validate_packet(bytes(corrupted))

if __name__ == "__main__":
    test_valid_packet()
    test_corrupted_packet()
    test_wrong_length()
    print("All telemetry validation tests PASSED!")