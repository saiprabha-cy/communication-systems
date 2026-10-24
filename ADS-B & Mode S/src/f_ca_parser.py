def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        char not in "0123456789ABCDEF" for char in normalized
    ):
        raise ValueError("Frame must be hexadecimal.")

    return "".join(f"{int(char, 16):04b}" for char in normalized)


def parse_df17_header(hex_frame: str) -> dict:
    bits = hex_to_bits(hex_frame)

    if len(bits) != 112:
        raise ValueError(f"Expected 112 bits; got {len(bits)}.")

    df = int(bits[0:5], 2)
    ca = int(bits[5:8], 2)

    if df != 17:
        raise ValueError(f"Expected DF17, got DF={df}.")

    return {
        "df": df,
        "ca": ca,
        "icao": f"{int(bits[8:32], 2):06X}",
        "me_bits": bits[32:88],
        "parity": f"{int(bits[88:112], 2):06X}",
    }


def main() -> None:
    frame = "8D40621D58C382D690C8AC2863A7"
    result = parse_df17_header(frame)

    for key, value in result.items():
        print(f"{key:10s}: {value}")

    assert result["df"] == 17
    assert len(result["me_bits"]) == 56
    print("\nPASS: DF17 header parsed.")


if __name__ == "__main__":
    main()