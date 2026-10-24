from dataclasses import dataclass


@dataclass(frozen=True)
class FrameInfo:
    downlink_format: int
    length_bits: int
    description: str


# This is a simplified table for the frame formats used in this exercise.
# A production decoder should implement the full applicable Mode S table.
FRAME_FORMATS = {
    0: FrameInfo(0, 56, "Short air-air surveillance"),
    4: FrameInfo(4, 56, "Surveillance altitude reply"),
    5: FrameInfo(5, 56, "Surveillance identity reply"),
    11: FrameInfo(11, 56, "Mode S all-call reply"),
    16: FrameInfo(16, 112, "Long air-air surveillance"),
    17: FrameInfo(17, 112, "ADS-B Extended Squitter"),
    18: FrameInfo(18, 112, "Extended Squitter, alternate context"),
    20: FrameInfo(20, 112, "Comm-B altitude reply"),
    21: FrameInfo(21, 112, "Comm-B identity reply"),
}


def hex_to_bits(hex_frame: str) -> str:
    normalized = hex_frame.strip().replace(" ", "").upper()
    if not normalized or any(
        char not in "0123456789ABCDEF" for char in normalized
    ):
        raise ValueError("Invalid hexadecimal frame.")

    return "".join(f"{int(char, 16):04b}" for char in normalized)


def inspect_frame(hex_frame: str) -> FrameInfo:
    bits = hex_to_bits(hex_frame)

    if len(bits) < 5:
        raise ValueError("Not enough bits to read DF.")

    df = int(bits[:5], 2)
    if df not in FRAME_FORMATS:
        raise ValueError(f"DF={df} is not supported by this exercise.")

    info = FRAME_FORMATS[df]

    if len(bits) != info.length_bits:
        raise ValueError(
            f"DF={df} expects {info.length_bits} bits; got {len(bits)}."
        )

    return info


def main() -> None:
    short_example = "5D484F"
    long_example = "8D40621D58C382D690C8AC2863A7"

    for frame in (short_example, long_example):
        info = inspect_frame(frame)
        print(
            f"{frame}: DF={info.downlink_format}, "
            f"{info.length_bits} bits, {info.description}"
        )

    print("\nPASS: supported frame lengths were checked.")


if __name__ == "__main__":
    main()