import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from telemetry_model import TelemetryData
from serializer import serialize_telemetry


def test_serialization_size():
    telemetry = TelemetryData(
        spacecraft_id=1,
        timestamp = 1757412000,
        temperature_c=25.4,
        voltage_v=3.71,
        current_a=0.82,
        battery_percent=87.5,
        sequence=1001,
    )

    packet = serialize_telemetry(telemetry)

    assert len(packet) == 13


def test_serialization_returns_bytes():
    telemetry = TelemetryData(
        spacecraft_id=1,
        timestamp = 1757412000,
        temperature_c=25.4,
        voltage_v=3.71,
        current_a=0.82,
        battery_percent=87.5,
        sequence=1001,
    )

    packet = serialize_telemetry(telemetry)

    assert isinstance(packet, bytes)