import csv
from pathlib import Path

from deserializer import deserialize_telemetry
from serializer import serialize_telemetry
from telemetry_model import create_telemetry

LOG_FILE = Path("telemetry_log.csv")


def log_telemetry_packets(packets):
    with LOG_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "spacecraft_id",
            "timestamp",
            "temperature_c",
            "voltage_v",
            "current_a",
            "battery_percent",
            "sequence",
        ])

        logged = 0

        for packet in packets:
            telemetry = deserialize_telemetry(packet)

            writer.writerow([
                telemetry.spacecraft_id,
                telemetry.timestamp,
                telemetry.temperature_c,
                telemetry.voltage_v,
                telemetry.current_a,
                telemetry.battery_percent,
                telemetry.sequence,
            ])

            logged += 1

    return logged


def generate_test_packets():
    packets = []

    for sequence in range(1001, 1006):
        telemetry = create_telemetry()

        telemetry.sequence = sequence
        telemetry.temperature_c += (sequence - 1001) * 0.1

        packet = serialize_telemetry(telemetry)
        packets.append(packet)

    return packets


if __name__ == "__main__":
    packets = generate_test_packets()

    count = log_telemetry_packets(packets)

    print("=== TELEMETRY LOGGER ===")
    print("Packets received :", len(packets))
    print("Packets logged   :", count)
    print("Log file         :", LOG_FILE.resolve())