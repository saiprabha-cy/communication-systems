import math


def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        char not in "0123456789ABCDEF" for char in normalized
    ):
        raise ValueError("Invalid hexadecimal frame.")

    return "".join(f"{int(char, 16):04b}" for char in normalized)


def parse_velocity(hex_frame: str) -> dict:
    bits = hex_to_bits(hex_frame)

    if len(bits) != 112:
        raise ValueError("Expected a 112-bit frame.")

    df = int(bits[0:5], 2)
    if df != 17:
        raise ValueError(f"Expected DF17, got DF={df}.")

    me = bits[32:88]
    type_code = int(me[0:5], 2)

    if type_code != 19:
        raise ValueError(f"Expected Type Code 19, got {type_code}.")

    subtype = int(me[5:8], 2)

    if subtype not in (1, 2):
        raise NotImplementedError(
            f"Velocity subtype {subtype} is not supported by this script."
        )

    # Subtype 1: velocity in 1-knot increments.
    # Subtype 2: velocity in 4-knot increments.
    scale = 1 if subtype == 1 else 4

    ew_sign = int(me[13], 2)
    ew_raw = int(me[14:24], 2)
    ns_sign = int(me[24], 2)
    ns_raw = int(me[25:35], 2)

    # Raw zero means the component is unavailable.
    east_west_knots = None
    north_south_knots = None

    if ew_raw != 0:
        ew_magnitude = (ew_raw - 1) * scale
        east_west_knots = -ew_magnitude if ew_sign else ew_magnitude

    if ns_raw != 0:
        ns_magnitude = (ns_raw - 1) * scale
        north_south_knots = -ns_magnitude if ns_sign else ns_magnitude

    speed_knots = None
    track_deg = None

    if east_west_knots is not None and north_south_knots is not None:
        speed_knots = math.hypot(east_west_knots, north_south_knots)
        track_deg = (
            math.degrees(
                math.atan2(east_west_knots, north_south_knots)
            ) + 360.0
        ) % 360.0

    vr_source = int(me[35], 2)
    vr_sign = int(me[36], 2)
    vr_raw = int(me[37:46], 2)
    vertical_rate_fpm = None

    if vr_raw != 0:
        vertical_rate_fpm = (vr_raw - 1) * 64
        if vr_sign:
            vertical_rate_fpm = -vertical_rate_fpm

    return {
        "type_code": type_code,
        "subtype": subtype,
        "east_west_knots": east_west_knots,
        "north_south_knots": north_south_knots,
        "ground_speed_knots": speed_knots,
        "track_degrees": track_deg,
        "vertical_rate_source": vr_source,
        "vertical_rate_fpm": vertical_rate_fpm,
    }


def main() -> None:
    # This reference frame is not a Type Code 19 velocity message.
    # Demonstrate the parser's explicit format check.
    frame = "8D40621D58C382D690C8AC2863A7"

    try:
        print(parse_velocity(frame))
    except ValueError as exc:
        print(f"Expected format check: {exc}")

    print("\nUse a verified TC19 frame to test the velocity field decoding.")


if __name__ == "__main__":
    main()