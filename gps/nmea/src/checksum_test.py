import pynmea2


valid_sentence = (
    "$GPGGA,184353.07,1929.045,S,"
    "02410.506,E,1,04,2.6,100.00,M,"
    "-33.9,M,,0000*6D"
)

corrupted_sentence = valid_sentence.replace(
    "184353.07",
    "184353.08"
)

print("Valid:")
print(valid_sentence)

print("\nCorrupted:")
print(corrupted_sentence)

print("\nParsing valid sentence:")

try:
    msg = pynmea2.parse(valid_sentence)
    print("VALID")
except pynmea2.ParseError as e:
    print("INVALID:", e)


print("\nParsing corrupted sentence:")

try:
    msg = pynmea2.parse(corrupted_sentence)
    print("VALID")
except pynmea2.ParseError as e:
    print("INVALID:", e)