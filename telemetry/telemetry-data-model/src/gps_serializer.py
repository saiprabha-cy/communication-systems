import struct
from gps_telemetry import GPSTelemetry

# Little-Endian: int32 (4B), int32 (4B), uint16 (2B), uint16 (2B), uint8 (1B) = 13 Bytes
GPS_FORMAT = "<iiHHB"


def serialize_gps(gps: GPSTelemetry) -> bytes:
    latitude_raw = round(gps.latitude_deg * 1_000_000)
    longitude_raw = round(gps.longitude_deg * 1_000_000)

    speed_raw = round(gps.speed_knots * 100)
    course_raw = round(gps.course_deg * 100)

    valid_raw = 1 if gps.valid else 0

    return struct.pack(
        GPS_FORMAT,
        latitude_raw,
        longitude_raw,
        speed_raw,
        course_raw,
        valid_raw,
    )