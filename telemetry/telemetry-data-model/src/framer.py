SYNC = b"\xAA\x55"


def frame_packet(payload: bytes) -> bytes:
    length = len(payload)

    if length > 255:
        raise ValueError("Payload too large")

    return SYNC + bytes([length]) + payload


if __name__ == "__main__":
    payload = bytes.fromhex(
        "01 9E 00 73 01 52 00 E9 03"
    )

    frame = frame_packet(payload)

    print("Payload:")
    print(payload.hex(" "))

    print("\nFramed packet:")
    print(frame.hex(" "))

    print("\nFrame length:", len(frame))