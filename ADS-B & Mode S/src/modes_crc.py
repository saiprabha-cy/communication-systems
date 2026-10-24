from typing import Tuple

POLY = 0xFFF409
CRC_MASK = 0xFFFFFF


def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        char not in "0123456789ABCDEF" for char in normalized
    ):
        raise ValueError("Invalid hexadecimal frame.")

    return "".join(f"{int(char, 16):04b}" for char in normalized)


def bits_to_int(bits: str) -> int:
    if not bits or any(bit not in "01" for bit in bits):
        raise ValueError("Expected a non-empty bit string.")
    return int(bits, 2)


def modes_crc(message_bits: str) -> int:
    """
    Compute the Mode S 24-bit CRC for message bits excluding the parity.

    The input is the data portion, normally 32 bits for a 56-bit frame
    or 88 bits for a 112-bit frame. The parity bits are not included.
    """
    if len(message_bits) not in (32, 88):
        raise ValueError(
            "Expected 32 data bits (short) or 88 data bits (long)."
        )

    if any(bit not in "01" for bit in message_bits):
        raise ValueError("Input contains non-binary characters.")

    crc = 0

    # Shift each message bit into the 24-bit CRC register.
    for bit_char in message_bits:
        top_bit = (crc >> 23) & 1
        crc = ((crc << 1) & CRC_MASK) | int(bit_char)

        if top_bit:
            crc ^= POLY

    return crc & CRC_MASK


def check_df17_crc(hex_frame: str) -> Tuple[bool, int, int]:
    bits = hex_to_bits(hex_frame)

    if len(bits) != 112:
        raise ValueError("DF17 CRC checker requires 112 bits.")

    df = int(bits[:5], 2)
    if df != 17:
        raise ValueError(f"Expected DF17, got DF={df}.")

    calculated = modes_crc(bits[:88])
    received = bits_to_int(bits[88:112])

    return calculated == received, calculated, received


def main() -> None:
    frame = "8D40621D58C382D690C8AC2863A7"
    valid, calculated, received = check_df17_crc(frame)

    print(f"Frame:      {frame}")
    print(f"Calculated: {calculated:06X}")
    print(f"Received:   {received:06X}")
    print(f"CRC valid:  {valid}")

    if not valid:
        print(
            "\nCRC mismatch. Verify the CRC convention and test vector "
            "against an independent Mode S decoder before proceeding."
        )

    # The published reference vector should be checked against pyModeS
    # in ADS-20 before using this implementation as a trusted decoder.
    print("\nCRC check complete.")


if __name__ == "__main__":
    main()