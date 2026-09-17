import struct
from telemetry_model import TelemetryData, create_telemetry
from serializer import FORMAT, serialize_telemetry


def parse_telemetry(packet: bytes) -> TelemetryData:
    expected_size = struct.calcsize(FORMAT)

    if len(packet) != expected_size:
        raise ValueError(
            f"Invalid packet size: expected {expected_size}, got {len(packet)}"
        )

    (
        spacecraft_id,
        timestamp,
        temperature_raw,
        voltage_raw,
        current_raw,
        sequence,
    ) = struct.unpack(FORMAT, packet)

    return TelemetryData(
        spacecraft_id=spacecraft_id,
        timestamp=timestamp,
        temperature_c=temperature_raw / 10.0,
        voltage_v=voltage_raw / 100.0,
        current_a=current_raw / 100.0,
        battery_percent=0.0,
        sequence=sequence,
    )


if __name__ == "__main__":
    telemetry = create_telemetry()
    packet = serialize_telemetry(telemetry)
    decoded = parse_telemetry(packet)

    print("Packet bytes:", packet.hex())
    print("Decoded telemetry:")
    print(decoded)