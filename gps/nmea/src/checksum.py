import pynmea2


sentence = (
    "$GPGGA,184353.07,1929.045,S,"
    "02410.506,E,1,04,2.6,100.00,M,"
    "-33.9,M,,0000*6D"
)

msg = pynmea2.parse(sentence)

print("Sentence:")
print(sentence)

print("\nChecksum:")
print(msg.checksum)

print("\nParsed successfully:")
print(msg)