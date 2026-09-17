import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from telemetry_model import TelemetryData
from serializer import serialize_telemetry
from deserializer import deserialize_telemetry


def test_round_trip():
    original = TelemetryData(
        spacecraft_id=1,
        timestamp = 1757412000,
        temperature_c=25.4,
        voltage_v=3.71,
        current_a=0.82,
        battery_percent=87.5,
        sequence=1001,
    )

    packet = serialize_telemetry(original)
    decoded = deserialize_telemetry(packet)

    assert decoded.spacecraft_id == original.spacecraft_id
    assert decoded.timestamp == original.timestamp
    assert decoded.temperature_c == 25.4
    assert decoded.voltage_v == 3.71
    assert decoded.current_a == 0.82
    assert decoded.sequence == 1001