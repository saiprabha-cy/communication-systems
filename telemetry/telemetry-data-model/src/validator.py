from framer import SYNC
from crc import crc16_ccitt


MIN_FRAME_SIZE = 2 + 1 + 2


def validate_packet(frame: bytes) -> bool:

    # Check minimum size
    if len(frame) < MIN_FRAME_SIZE:
        return False

    # Check synchronization bytes
    if frame[:2] != SYNC:
        return False

    # Extract declared payload length
    payload_length = frame[2]

    expected_length = 2 + 1 + payload_length + 2

    # Check total frame length
    if len(frame) != expected_length:
        return False

    # Extract payload
    payload_start = 3
    payload_end = payload_start + payload_length

    payload = frame[payload_start:payload_end]

    # Extract received CRC
    received_crc = int.from_bytes(
        frame[payload_end:payload_end + 2],
        byteorder="little"
    )

    # Calculate CRC
    calculated_crc = crc16_ccitt(payload)

    # Validate CRC
    if received_crc != calculated_crc:
        return False

    return True