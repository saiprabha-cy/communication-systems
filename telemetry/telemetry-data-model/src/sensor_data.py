from dataclasses import dataclass


@dataclass
class TemperatureSensor:
    sensor_id: int
    temperature_c: float


@dataclass
class VoltageSensor:
    sensor_id: int
    voltage_v: float


@dataclass
class CurrentSensor:
    sensor_id: int
    current_a: float


@dataclass
class SensorData:
    temperature: TemperatureSensor
    voltage: VoltageSensor
    current: CurrentSensor
def create_sensor_data() -> SensorData:
    return SensorData(
        temperature=TemperatureSensor(
            sensor_id=1,
            temperature_c=25.4
        ),
        voltage=VoltageSensor(
            sensor_id=2,
            voltage_v=3.71
        ),
        current=CurrentSensor(
            sensor_id=3,
            current_a=0.82
        )
    )


def print_sensor_data(data: SensorData) -> None:
    print("=== Sensor Data ===")
    print(
        f"Temperature Sensor {data.temperature.sensor_id}: "
        f"{data.temperature.temperature_c:.2f} °C"
    )

    print(
        f"Voltage Sensor {data.voltage.sensor_id}: "
        f"{data.voltage.voltage_v:.2f} V"
    )

    print(
        f"Current Sensor {data.current.sensor_id}: "
        f"{data.current.current_a:.2f} A"
    )


if __name__ == "__main__":
    sensor_data = create_sensor_data()
    print_sensor_data(sensor_data)