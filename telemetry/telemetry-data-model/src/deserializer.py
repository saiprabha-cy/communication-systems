import struct
from telemetry_model import TelemetryData
from serializer import FORMAT


def deserialize_telemetry(packet: bytes) -> TelemetryData:
    spacecraft_id,timestamp, temperature_raw, voltage_raw, current_raw, sequence = (
        struct.unpack(FORMAT, packet)
    )

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
    packet = bytes.fromhex("01 a0 fa bf 68 fe 00 73 01 52 00 e9 03")

    telemetry = deserialize_telemetry(packet)

    print("=== Decoded Telemetry ===")
    print(f"Spacecraft ID : {telemetry.spacecraft_id}")
    print(f"TimeStamp :     {telemetry.timestamp}")
    print(f"Temperature   : {telemetry.temperature_c:.2f} °C")
    print(f"Voltage       : {telemetry.voltage_v:.2f} V")
    print(f"Current       : {telemetry.current_a:.2f} A")
    print(f"Sequence      : {telemetry.sequence}")