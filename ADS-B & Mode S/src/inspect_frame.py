HEX_FRAME = "8D40621D58C382D690C8AC2863A7"


def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()

    if not normalized:
        raise ValueError("Frame is empty.")

    if any(ch not in "0123456789ABCDEF" for ch in normalized):
        raise ValueError("Frame contains a non-hexadecimal character.")

    return "".join(f"{int(ch, 16):04b}" for ch in normalized)


def main() -> None:
    bits = hex_to_bits(HEX_FRAME)

    if len(bits) != 112:
        raise ValueError(
            f"Expected 112 bits for this reference DF17 frame, got {len(bits)}."
        )

    df = int(bits[0:5], 2)
    ca = int(bits[5:8], 2)
    icao = int(bits[8:32], 2)
    me = bits[32:88]
    parity = bits[88:112]

    print(f"Hex frame:       {HEX_FRAME}")
    print(f"Frame length:    {len(bits)} bits")
    print(f"DF:              {df}")
    print(f"CA:              {ca}")
    print(f"ICAO address:    {icao:06X}")
    print(f"ME field:        {me} ({len(me)} bits)")
    print(f"Parity field:    {parity} (0x{int(parity, 2):06X})")

    assert df == 17
    assert len(me) == 56
    print("\nPASS: DF17 structure extracted.")


if __name__ == "__main__":
    main()