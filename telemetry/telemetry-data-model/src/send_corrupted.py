import socket

from corrupt_packet import create_packet, corrupt_packet


packet = create_packet()

corrupted = corrupt_packet(
    packet,
    index=5,
    mask=0x01
)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(
    corrupted,
    ("127.0.0.1", 5005)
)

sock.close()

print("Sent corrupted packet:")
print(corrupted.hex(" "))