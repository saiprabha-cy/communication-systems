import socket
import time

from framer import frame_packet
from crc import crc16_ccitt


def build_packet(sequence: int) -> bytes:

    payload = bytes.fromhex(
        "01 00 00 00 68 9E 00 73 01 52 00"
    )

    sequence_bytes = sequence.to_bytes(
        2,
        byteorder="little"
    )

    payload += sequence_bytes

    frame = frame_packet(payload)

    crc = crc16_ccitt(payload)

    return frame + crc.to_bytes(
        2,
        byteorder="little"
    )


sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

for sequence in range(100, 110):

    if sequence == 105:
        print("Simulating loss of packet:", sequence)
        continue

    packet = build_packet(sequence)

    sock.sendto(
        packet,
        ("127.0.0.1", 5005)
    )

    print("Sent:", sequence)

    time.sleep(0.2)

sock.close()