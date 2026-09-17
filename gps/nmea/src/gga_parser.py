import pynmea2

sentence = (
    "$GPGGA,184353.07,1929.045,S,"
    "02410.506,E,1,04,2.6,100.00,M,"
    "-33.9,M,,0000*6D"
)

msg = pynmea2.parse(sentence)

print("=== GGA FIX DATA ===")

print("Message type :", type(msg).__name__)
print("UTC time     :", msg.timestamp)

print("Latitude     :", msg.latitude)
print("Longitude    :", msg.longitude)

print("Fix quality  :", msg.gps_qual)
print("Satellites   :", msg.num_sats)
print("HDOP         :", msg.horizontal_dil)

print("Altitude     :", msg.altitude, msg.altitude_units)