import pynmea2
import folium


RMC_SENTENCES = [
    "$GPRMC,184353.07,A,1929.045,S,02410.506,E,000.0,000.0,120926,,,A*44",

    "$GPRMC,184354.07,A,1929.046,S,02410.507,E,001.2,045.0,120926,,,A*43",

    "$GPRMC,184355.07,A,1929.047,S,02410.508,E,002.0,045.0,120926,,,A*4D",

    "$GPRMC,184356.07,A,1929.048,S,02410.509,E,002.5,045.0,120926,,,A*45",
]

def parse_valid_position(sentence: str):

    msg = pynmea2.parse(sentence)

    if msg.status != "A":
        return None

    return {
        "latitude": msg.latitude,
        "longitude": msg.longitude,
        "speed_knots": msg.spd_over_grnd,
        "course_deg": msg.true_course,
        "timestamp": msg.timestamp,
    }


def build_track(sentences):

    track = []

    for sentence in sentences:

        position = parse_valid_position(sentence)

        if position is not None:
            track.append(position)

    return track


def create_map(track):

    first = track[0]

    gps_map = folium.Map(
        location=[
            first["latitude"],
            first["longitude"]
        ],
        zoom_start=15,
        tiles=None
    )

    coordinates = []

    for point in track:

        coordinate = [
            point["latitude"],
            point["longitude"]
        ]

        coordinates.append(coordinate)

        folium.CircleMarker(
            location=coordinate,
            radius=5,
            popup=(
                f"Time: {point['timestamp']}<br>"
                f"Speed: {point['speed_knots']} knots<br>"
                f"Course: {point['course_deg']}°"
            )
        ).add_to(gps_map)

    folium.PolyLine(
        coordinates,
        weight=4
    ).add_to(gps_map)

    gps_map.save("track.html")


if __name__ == "__main__":

    track = build_track(RMC_SENTENCES)

    print("=== GPS TRACK ===")

    for point in track:

        print(
            point["timestamp"],
            point["latitude"],
            point["longitude"],
            point["speed_knots"],
            point["course_deg"]
        )

    create_map(track)

    print("\nTrack points:", len(track))
    print("Map saved to: track.html")