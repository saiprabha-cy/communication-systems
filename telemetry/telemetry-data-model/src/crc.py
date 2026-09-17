def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF

    for byte in data:
        crc ^= byte << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    return crc


if __name__ == "__main__":
    data = b"123456789"

    crc = crc16_ccitt(data)

    print(f"CRC = 0x{crc:04X}")

    