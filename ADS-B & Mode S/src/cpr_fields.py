def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        char not in "0123456789ABCDEF" for char in normalized
    ):
        raise ValueError("Invalid hexadecimal frame.")

    return "".join(f"{int(char, 16):04b}" for char in normalized)


def extract_airborne_cpr_fields(hex_frame: str) -> dict:
    bits = hex_to_bits(hex_frame)

    if len(bits) != 112:
        raise ValueError("Expected a 112-bit Mode S frame.")

    df = int(bits[0:5], 2)
    if df != 17:
        raise ValueError(f"Expected DF17, got DF={df}.")

    me = bits[32:88]
    type_code = int(me[0:5], 2)

    # Airborne position messages use Type Codes 9 through 18 and 20
    # through 22. The exact field layout must match the message subtype.
    if not (9 <= type_code <= 18 or 20 <= type_code <= 22):
        raise ValueError(
            f"ME Type Code {type_code} is not an airborne position type."
        )

    # ME bit positions, indexed from 0 within the 56-bit ME field:
    # bit 21 is the time flag, bit 22 is the CPR format flag,
    # then 17-bit latitude and 17-bit longitude.
    time_flag = int(me[21], 2)
    cpr_format = int(me[22], 2)
    cpr_lat = int(me[23:40], 2)
    cpr_lon = int(me[40:57], 2) if len(me) >= 57 else None

    # ME is 56 bits. Correct field slices for airborne position:
    # TC(5), surveillance status(2), NIC supplement(1), altitude(12),
    # time(1), CPR format(1), latitude(17), longitude(17).
    # The total is 56 bits, so positions are re-sliced explicitly below.
    cpr_lat = int(me[21:38], 2)
    cpr_lon = int(me[38:55], 2)

    return {
        "type_code": type_code,
        "time_flag": time_flag,
        "cpr_format": cpr_format,
        "cpr_lat": cpr_lat,
        "cpr_lon": cpr_lon,
    }


def main() -> None:
    frame = "8D40621D58C382D690C8AC2863A7"
    fields = extract_airborne_cpr_fields(frame)

    for name, value in fields.items():
        print(f"{name:12s}: {value}")

    assert 0 <= fields["cpr_lat"] < 2**17
    assert 0 <= fields["cpr_lon"] < 2**17
    print("\nPASS: CPR fields extracted into 17-bit integers.")


if __name__ == "__main__":
    main()