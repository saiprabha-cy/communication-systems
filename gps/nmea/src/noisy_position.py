import random
import folium


TRUE_LATITUDE = -19.484000
TRUE_LONGITUDE = 24.175000

NUM_POINTS = 50

NOISE_DEG = 0.00005


def generate_noisy_positions():

    positions = []

    for _ in range(NUM_POINTS):

        latitude = (
            TRUE_LATITUDE
            + random.uniform(-NOISE_DEG, NOISE_DEG)
        )

        longitude = (
            TRUE_LONGITUDE
            + random.uniform(-NOISE_DEG, NOISE_DEG)
        )

        positions.append(
            (latitude, longitude)
        )

    return positions


def create_map(positions):

    gps_map = folium.Map(
        location=[
            TRUE_LATITUDE,
            TRUE_LONGITUDE
        ],
        zoom_start=15,
        tiles=None
    )

    # True position
    folium.Marker(
        location=[
            TRUE_LATITUDE,
            TRUE_LONGITUDE
        ],
        popup="True Position"
    ).add_to(gps_map)

    # Noisy GPS measurements
    for index, position in enumerate(positions):

        folium.CircleMarker(
            location=position,
            radius=4,
            popup=f"GPS Measurement {index + 1}"
        ).add_to(gps_map)

    gps_map.save("noisy_position.html")


if __name__ == "__main__":

    positions = generate_noisy_positions()

    print("=== NOISY GPS POSITIONS ===")

    for index, position in enumerate(positions):

        print(
            f"{index + 1:02d}: "
            f"lat={position[0]:.8f}, "
            f"lon={position[1]:.8f}"
        )

    create_map(positions)

    print("\nMeasurements:", len(positions))
    print("Map saved to: noisy_position.html")