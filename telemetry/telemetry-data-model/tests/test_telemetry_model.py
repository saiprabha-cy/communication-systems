import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from telemetry_model import TelemetryData, create_telemetry


def test_telemetry_creation():
    telemetry = create_telemetry()

    assert telemetry.spacecraft_id == 1
    assert telemetry.temperature_c == 25.4
    assert telemetry.voltage_v == 3.71
    assert telemetry.current_a == 0.82
    assert telemetry.battery_percent == 87.5
    assert telemetry.sequence == 1001


def test_telemetry_types():
    telemetry = create_telemetry()

    assert isinstance(telemetry.spacecraft_id, int)
    assert isinstance(telemetry.temperature_c, float)
    assert isinstance(telemetry.voltage_v, float)
    assert isinstance(telemetry.current_a, float)
    assert isinstance(telemetry.battery_percent, float)
    assert isinstance(telemetry.sequence, int)