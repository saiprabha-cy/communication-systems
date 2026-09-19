import sys
import os

# Add src/ folder to Python's import path
sys.path.append(os.path.abspath("src"))

from gps_parser import parse_gps_telemetry
from gps_serializer import serialize_gps


def main():
    sentence = (
        "$GPRMC,184354.07,A,1929.046,S,"
        "02410.507,E,001.2,045.0,120926,,,A*43"
    )

    # 1. Parse NMEA Sentence
    gps_data = parse_gps_telemetry(sentence)
    print("--- Decoded GPSTelemetry Object ---")
    print(f"Latitude  : {gps_data.latitude_deg:.6f}°")
    print(f"Longitude : {gps_data.longitude_deg:.6f}°")
    print(f"Speed     : {gps_data.speed_knots} knots")
    print(f"Course    : {gps_data.course_deg}°")
    print(f"Valid     : {gps_data.valid}")

    # 2. Serialize to Fixed-Point Binary
    packet = serialize_gps(gps_data)
    print("\n--- Binary Payload Output ---")
    print("GPS Payload Length :", len(packet), "bytes")
    print("GPS Payload (Hex)  :", packet.hex())


if __name__ == "__main__":
    main()