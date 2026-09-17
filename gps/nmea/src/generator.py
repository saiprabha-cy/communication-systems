import pynmea2


msg = pynmea2.GGA(
    "GP",
    "GGA",
    (
        "184353.07",
        "1929.045",
        "S",
        "02410.506",
        "E",
        "1",
        "04",
        "2.6",
        "100.00",
        "M",
        "-33.9",
        "M",
        "",
        "0000",
    ),
)

sentence = str(msg)

print("Generated NMEA:")
print(sentence)