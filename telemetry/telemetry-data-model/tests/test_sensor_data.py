import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from sensor_data import (
    SensorData,
    TemperatureSensor,
    VoltageSensor,
    CurrentSensor,
    create_sensor_data,
)


def test_sensor_data_creation():
    data = create_sensor_data()

    assert isinstance(data, SensorData)

    assert data.temperature.sensor_id == 1
    assert data.temperature.temperature_c == 25.4

    assert data.voltage.sensor_id == 2
    assert data.voltage.voltage_v == 3.71

    assert data.current.sensor_id == 3
    assert data.current.current_a == 0.82


def test_sensor_types():
    data = create_sensor_data()

    assert isinstance(data.temperature, TemperatureSensor)
    assert isinstance(data.voltage, VoltageSensor)
    assert isinstance(data.current, CurrentSensor)