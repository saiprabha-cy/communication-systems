from dataclasses import dataclass


@dataclass
class TelemetryData:
    spacecraft_id: int
    timestamp: int
    temperature_c: float
    voltage_v: float
    current_a: float
    battery_percent: float
    sequence: int


def create_telemetry() -> TelemetryData:
    return TelemetryData(
        spacecraft_id=1,
        timestamp=1757412000,
        temperature_c=25.4,
        voltage_v=3.71,
        current_a=0.82,
        battery_percent=87.5,
        sequence=1001,
    )


def print_telemetry(data: TelemetryData) -> None:
    print("=== Spacecraft Telemetry ===")
    print(f"Spacecraft ID : {data.spacecraft_id}")
    print(f"TimeStamp :     {telemetry.timestamp}")
    print(f"Temperature   : {data.temperature_c:.2f} °C")
    print(f"Voltage       : {data.voltage_v:.2f} V")
    print(f"Current       : {data.current_a:.2f} A")
    print(f"Battery       : {data.battery_percent:.1f} %")
    print(f"Sequence      : {data.sequence}")


if __name__ == "__main__":
    telemetry = create_telemetry()
    print_telemetry(telemetry)