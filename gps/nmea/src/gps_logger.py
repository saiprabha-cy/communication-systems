import csv
from pathlib import Path

import pynmea2


RMC_SENTENCES = [
    "$GPRMC,184353.07,A,1929.045,S,02410.506,E,000.0,000.0,120926,,,A*44",

    "$GPRMC,184354.07,A,1929.046,S,02410.507,E,001.2,045.0,120926,,,A*43",

    "$GPRMC,184355.07,A,1929.047,S,02410.508,E,002.0,045.0,120926,,,A*4D",

    "$GPRMC,184356.07,A,1929.048,S,02410.509,E,002.5,045.0,120926,,,A*45",

    "$GPRMC,184357.07,V,1929.050,S,02410.510,E,003.0,045.0,120926,,,A*47",
]


LOG_FILE = Path("gps_log.csv")


def parse_rmc(sentence: str):

    msg = pynmea2.parse(sentence)

    return {
        "date": msg.datestamp,
        "time": msg.timestamp,
        "status": msg.status,
        "latitude": msg.latitude,
        "longitude": msg.longitude,
        "speed_knots": msg.spd_over_grnd,
        "course_deg": msg.true_course,
    }


def log_positions(sentences):

    with LOG_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "date",
                "time",
                "status",
                "latitude",
                "longitude",
                "speed_knots",
                "course_deg",
            ]
        )

        writer.writeheader()

        logged = 0

        for sentence in sentences:

            try:
                data = parse_rmc(sentence)

            except pynmea2.ParseError as error:

                print("Rejected NMEA:", error)
                continue

            if data["status"] != "A":

                print(
                    "Rejected navigation fix:",
                    data["time"]
                )

                continue

            writer.writerow(data)

            logged += 1

    return logged


if __name__ == "__main__":

    count = log_positions(RMC_SENTENCES)

    print("=== GPS LOGGER ===")
    print("Valid positions logged:", count)
    print("Log file:", LOG_FILE.resolve())