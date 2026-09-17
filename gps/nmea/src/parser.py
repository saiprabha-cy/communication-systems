import pynmea2


sentence = (
    "$GPGGA,184353.07,1929.045,S,02410.506,E,"
    "1,04,2.6,100.00,M,-33.9,M,,0000*6D"
)

msg = pynmea2.parse(sentence)

print("=== NMEA Message ===")
print("Type       :", type(msg).__name__)
print("Timestamp  :", msg.timestamp)
print("Latitude   :", msg.latitude)
print("Longitude  :", msg.longitude)
print("GPS Quality:", msg.gps_qual)
print("Satellites :", msg.num_sats)
print("Altitude   :", msg.altitude, msg.altitude_units)