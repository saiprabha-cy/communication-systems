import pynmea2
from gps_telemetry import GPSTelemetry


def parse_gps_telemetry(sentence: str) -> GPSTelemetry:
    msg = pynmea2.parse(sentence)

    # Handle optional/empty fields from pynmea2 safely
    speed = float(msg.spd_over_grnd) if msg.spd_over_grnd else 0.0
    course = float(msg.true_course) if msg.true_course else 0.0

    return GPSTelemetry(
        latitude_deg=float(msg.latitude),
        longitude_deg=float(msg.longitude),
        speed_knots=speed,
        course_deg=course,
        valid=(msg.status == "A"),
    )