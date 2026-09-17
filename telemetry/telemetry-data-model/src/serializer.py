import struct
from telemetry_model import TelemetryData


FORMAT = "<BIhHHH"


def serialize_telemetry(data: TelemetryData) -> bytes:
    temperature_raw = round(data.temperature_c * 10)
    voltage_raw = round(data.voltage_v * 100)
    current_raw = round(data.current_a * 100)

    return struct.pack(
        FORMAT,
        data.spacecraft_id,
        data.timestamp,
        temperature_raw,
        voltage_raw,
        current_raw,
        data.sequence,
    )


if __name__ == "__main__":
    telemetry = TelemetryData(
        spacecraft_id=1,
        timestamp= 1757412000,
        temperature_c=25.4,
        voltage_v=3.71,
        current_a=0.82,
        battery_percent=87.5,
        sequence=1001,
    )

    packet = serialize_telemetry(telemetry)

    print("Serialized packet:")
    print(packet)
    print("Hex:")
    print(packet.hex(" "))
    print("Size:", len(packet), "bytes")