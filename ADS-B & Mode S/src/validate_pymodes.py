import json
import sys

import pyModeS as pms


def normalize_frame(frame: str) -> str:
    normalized = frame.strip().replace(" ", "").upper()

    if len(normalized) not in (14, 28):
        raise ValueError("Mode S frame must be 14 or 28 hex characters.")

    if any(char not in "0123456789ABCDEF" for char in normalized):
        raise ValueError("Invalid hexadecimal character.")

    return normalized


def decode_with_pymodes(frame: str) -> dict:
    frame = normalize_frame(frame)

    result = {
        "frame": frame,
        "df": pms.df(frame),
        "crc_result": pms.crc(frame),
    }

    if result["df"] in (17, 18):
        result["icao"] = pms.adsb.icao(frame)
        result["type_code"] = pms.adsb.typecode(frame)

        type_code = result["type_code"]

        if type_code == 19:
            result["velocity"] = pms.adsb.velocity(frame)

        elif 9 <= type_code <= 18 or 20 <= type_code <= 22:
            result["altitude_ft"] = pms.adsb.altitude(frame)

    return result


def main() -> None:
    frames = sys.argv[1:] or [
        "8D40621D58C382D690C8AC2863A7",
    ]

    for frame in frames:
        try:
            result = decode_with_pymodes(frame)
            print(json.dumps(result, indent=2, default=str))
        except Exception as exc:
            print(
                f"ERROR for {frame}: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )

    print(
        "\nCheck your installed pyModeS version's API if a function name "
        "is unavailable; package APIs can differ between versions."
    )


if __name__ == "__main__":
    main()