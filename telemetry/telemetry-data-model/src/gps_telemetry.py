from dataclasses import dataclass


@dataclass
class GPSTelemetry:
    latitude_deg: float
    longitude_deg: float
    speed_knots: float
    course_deg: float
    valid: bool