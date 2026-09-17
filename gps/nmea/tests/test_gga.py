import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

import pynmea2


def test_gga_fields():

    sentence = (
        "$GPGGA,184353.07,1929.045,S,"
        "02410.506,E,1,04,2.6,100.00,M,"
        "-33.9,M,,0000*6D"
    )

    msg = pynmea2.parse(sentence)

    assert type(msg).__name__ == "GGA"
    assert msg.gps_qual == 1
    assert msg.num_sats == "04"
    assert msg.altitude == 100.0


def test_gga_coordinates():

    sentence = (
        "$GPGGA,184353.07,1929.045,S,"
        "02410.506,E,1,04,2.6,100.00,M,"
        "-33.9,M,,0000*6D"
    )

    msg = pynmea2.parse(sentence)

    assert abs(msg.latitude - (-19.4840833333)) < 1e-6
    assert abs(msg.longitude - 24.1751) < 1e-6