from framer import frame_packet
from crc import crc16_ccitt
from validator import validate_packet


def add_crc(frame_without_crc: bytes) -> bytes:
    payload_length = frame_without_crc[2]

    payload = frame_without_crc[
        3:3 + payload_length
    ]

    crc = crc16_ccitt(payload)

    return frame_without_crc + crc.to_bytes(2, "little")


def create_packet() -> bytes:
    payload = bytes.fromhex(
        "01 00 00 00 68 9E 00 73 01 52 00 E9 03"
    )

    frame = frame_packet(payload)

    return add_crc(frame)


def corrupt_packet(packet: bytes, index: int, mask: int) -> bytes:
    corrupted = bytearray(packet)

    corrupted[index] ^= mask

    return bytes(corrupted)


if __name__ == "__main__":

    packet = create_packet()

    print("Original packet:")
    print(packet.hex(" "))

    print("\nOriginal validation:")
    print(validate_packet(packet))

    corrupted = corrupt_packet(
        packet,
        index=5,
        mask=0x01
    )

    print("\nCorrupted packet:")
    print(corrupted.hex(" "))

    print("\nCorrupted validation:")
    print(validate_packet(corrupted))