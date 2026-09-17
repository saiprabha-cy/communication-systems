import socket

from framer import frame_packet


payload = bytes.fromhex(
    "01 9E 00 73 01 52 00 E9 03"
)

frame = frame_packet(payload)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(
    frame,
    ("127.0.0.1", 5005)
)

sock.close()

print("Sent:", frame.hex(" "))