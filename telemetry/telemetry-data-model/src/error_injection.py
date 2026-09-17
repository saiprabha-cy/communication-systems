from crc import crc16_ccitt
payload = bytes.fromhex(
    "01 9E 00 73 01 52 00 E9 03"
)

crc = crc16_ccitt(payload)

packet = payload + crc.to_bytes(2, "little")

print("Original:")
print(packet.hex(" "))

corrupted = bytearray(packet)

# Flip one bit
corrupted[4] ^= 0x01

print("\nCorrupted:")
print(bytes(corrupted).hex(" "))

received_payload = bytes(corrupted[:-2])
received_crc = int.from_bytes(corrupted[-2:], "little")

calculated_crc = crc16_ccitt(received_payload)

print(f"\nReceived CRC : 0x{received_crc:04X}")
print(f"Calculated CRC: 0x{calculated_crc:04X}")

if received_crc == calculated_crc:
    print("CRC PASS")
else:
    print("CRC FAIL")