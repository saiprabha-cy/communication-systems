from altitude_parser import parse_airborne_position
from velocity_parser import parse_velocity


def normalize_frame(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()

    if not normalized:
        raise ValueError("Frame is empty.")

    if any(char not in "0123456789ABCDEF" for char in normalized):
        raise ValueError("Frame contains non-hexadecimal characters.")

    if len(normalized) != 28:
        raise ValueError(
            f"DF17 must have 28 hexadecimal characters; got {len(normalized)}."
        )

    return normalized


def hex_to_bits(hex_frame: str) -> str:
    return "".join(f"{int(char, 16):04b}" for char in hex_frame)


def parse_adsb_message(hex_frame: str) -> dict:
    frame = normalize_frame(hex_frame)
    bits = hex_to_bits(frame)

    df = int(bits[:5], 2)
    if df != 17:
        return {
            "frame": frame,
            "df": df,
            "supported": False,
            "reason": "This parser currently supports DF17 only.",
        }

    icao = f"{int(bits[8:32], 2):06X}"
    me = bits[32:88]
    type_code = int(me[:5], 2)

    result = {
        "frame": frame,
        "df": df,
        "icao": icao,
        "type_code": type_code,
        "supported": True,
        "message_type": "unknown",
    }

    if 9 <= type_code <= 18 or 20 <= type_code <= 22:
        result["message_type"] = "airborne_position"
        result.update(parse_airborne_position(frame))

    elif type_code == 19:
        result["message_type"] = "velocity"
        result.update(parse_velocity(frame))

    else:
        result["message_type"] = "other_or_unsupported"
        result["supported_fields_only"] = True

    return result


def main() -> None:
    frames = [
        "8D40621D58C382D690C8AC2863A7",
    ]

    for frame in frames:
        try:
            result = parse_adsb_message(frame)
            print("\n--- Decoded message ---")
            for key, value in result.items():
                print(f"{key:24s}: {value}")
        except (ValueError, NotImplementedError) as exc:
            print(f"Could not parse {frame}: {exc}")

    print("\nParser run complete.")


if __name__ == "__main__":
    main()