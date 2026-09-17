def nmea_checksum(sentence: str) -> str:

    start = sentence.find("$")
    end = sentence.find("*")

    if start == -1 or end == -1:
        raise ValueError("Invalid NMEA sentence")

    data = sentence[start + 1:end]

    checksum = 0

    for char in data:
        checksum ^= ord(char)

    return f"{checksum:02X}"


sentence = (
    "$GPGGA,184353.07,1929.045,S,"
    "02410.506,E,1,04,2.6,100.00,M,"
    "-33.9,M,,0000*6D"
)

calculated = nmea_checksum(sentence)

print("Expected checksum :", sentence.split("*")[1])
print("Calculated checksum:", calculated)

if calculated == sentence.split("*")[1]:
    print("CHECKSUM PASS")
else:
    print("CHECKSUM FAIL")