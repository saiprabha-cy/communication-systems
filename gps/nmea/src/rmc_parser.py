import pynmea2

sentence = (
    "$GPRMC,184353.07,A,"
    "1929.045,S,02410.506,E,"
    "000.0,000.0,120926,,,A*44"
)

msg = pynmea2.parse(sentence)

print("=== RMC NAVIGATION DATA ===")

print("Message type :", type(msg).__name__)
print("UTC time     :", msg.timestamp)

print("Status       :", msg.status)

print("Latitude     :", msg.latitude)
print("Longitude    :", msg.longitude)

# Convert speed in knots to km/h manually
speed_knots = float(msg.spd_over_grnd) if msg.spd_over_grnd else 0.0
speed_kmph = speed_knots * 1.852

print("Speed        :", speed_knots, "knots |", speed_kmph, "km/h")
print("Course       :", msg.true_course)

print("Date         :", msg.datestamp)