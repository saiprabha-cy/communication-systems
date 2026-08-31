SYNC = 0xAA

TYPE_TELEMETRY = 0x01
TYPE_COMMAND = 0x02
TYPE_STATUS = 0x03


def calculate_checksum(data):
    """
    Simple educational checksum.

    This is NOT a production CRC.
    """
    return sum(data) & 0xFF


def build_packet(packet_type, payload):
    if not 0 <= packet_type <= 0xFF:
        raise ValueError("Packet type must fit in one byte")

    if len(payload) > 255:
        raise ValueError("Payload too large")

    length = len(payload)

    packet_without_crc = [
        SYNC,
        packet_type,
        length,
        *payload
    ]

    crc = calculate_checksum(packet_without_crc[1:])

    packet = packet_without_crc + [crc]

    return packet


# Example telemetry payload
payload = [42, 16, 5, 127]

packet = build_packet(
    TYPE_TELEMETRY,
    payload
)

print("Telemetry payload:")
print(payload)

print("\nEncoded packet:")
print(" ".join(f"{byte:02X}" for byte in packet))