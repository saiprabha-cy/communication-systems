def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        char not in "0123456789ABCDEF" for char in normalized
    ):
        raise ValueError("Invalid hexadecimal frame.")

    return "".join(f"{int(char, 16):04b}" for char in normalized)


def parse_airborne_position(hex_frame: str) -> dict:
    bits = hex_to_bits(hex_frame)

    if len(bits) != 112:
        raise ValueError("Expected a 112-bit frame.")

    df = int(bits[0:5], 2)
    if df != 17:
        raise ValueError(f"Expected DF17, got DF={df}.")

    me = bits[32:88]
    type_code = int(me[0:5], 2)

    if not (9 <= type_code <= 18 or 20 <= type_code <= 22):
        raise ValueError(f"Not an airborne position message: TC={type_code}")

    # ME layout:
    # TC[0:5], surveillance status[5:7], NIC supplement[7],
    # altitude[8:20], time flag[20], CPR format[21],
    # latitude[22:39], longitude[39:56].
    altitude_code = int(me[8:20], 2)
    time_flag = int(me[20], 2)
    cpr_format = int(me[21], 2)
    cpr_lat = int(me[22:39], 2)
    cpr_lon = int(me[39:56], 2)

    q_bit = (altitude_code >> 4) & 1
    altitude_ft = None

    if q_bit == 1:
        # Remove the Q bit and join the remaining encoded bits.
        n = ((altitude_code & 0x0FE0) >> 1) | (altitude_code & 0x000F)
        altitude_ft = n * 25 - 1000

    return {
        "df": df,
        "type_code": type_code,
        "altitude_code": altitude_code,
        "q_bit": q_bit,
        "barometric_altitude_ft": altitude_ft,
        "time_flag": time_flag,
        "cpr_format": cpr_format,
        "cpr_lat": cpr_lat,
        "cpr_lon": cpr_lon,
    }


def main() -> None:
    frame = "8D40621D58C382D690C8AC2863A7"
    result = parse_airborne_position(frame)

    for key, value in result.items():
        print(f"{key:26s}: {value}")

    print(
        "\nIf barometric_altitude_ft is None, this implementation does not "
        "decode the Q=0 altitude coding."
    )


if __name__ == "__main__":
    main()