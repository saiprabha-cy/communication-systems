def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        char not in "0123456789ABCDEF" for char in normalized
    ):
        raise ValueError("Invalid hexadecimal frame.")

    return "".join(f"{int(char, 16):04b}" for char in normalized)


def extract_icao_df17(hex_frame: str) -> str:
    bits = hex_to_bits(hex_frame)

    if len(bits) != 112:
        raise ValueError("DF17 must be exactly 112 bits.")

    df = int(bits[:5], 2)
    if df != 17:
        raise ValueError(f"Expected DF17, got DF={df}.")

    address_value = int(bits[8:32], 2)
    return f"{address_value:06X}"


def main() -> None:
    examples = [
        "8D40621D58C382D690C8AC2863A7",
    ]

    for frame in examples:
        address = extract_icao_df17(frame)
        print(f"Frame:   {frame}")
        print(f"Address: {address}")

    assert extract_icao_df17(examples[0]) == "40621D"
    print("\nPASS: ICAO address extraction succeeded.")


if __name__ == "__main__":
    main()