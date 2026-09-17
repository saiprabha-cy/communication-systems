import math


# WGS-84 constants
A = 6378137.0
E2 = 6.69437999014e-3


def geodetic_to_ecef(latitude_deg, longitude_deg, altitude_m):

    latitude = math.radians(latitude_deg)
    longitude = math.radians(longitude_deg)

    sin_lat = math.sin(latitude)
    cos_lat = math.cos(latitude)

    sin_lon = math.sin(longitude)
    cos_lon = math.cos(longitude)

    # Prime vertical radius of curvature
    N = A / math.sqrt(
        1 - E2 * sin_lat**2
    )

    x = (N + altitude_m) * cos_lat * cos_lon

    y = (N + altitude_m) * cos_lat * sin_lon

    z = (N * (1 - E2) + altitude_m) * sin_lat

    return x, y, z


if __name__ == "__main__":

    latitude = -19.484083333333334
    longitude = 24.1751
    altitude = 100.0

    x, y, z = geodetic_to_ecef(
        latitude,
        longitude,
        altitude
    )

    print("=== GEODETIC → ECEF ===")

    print(f"Latitude  : {latitude:.8f} deg")
    print(f"Longitude : {longitude:.8f} deg")
    print(f"Altitude  : {altitude:.2f} m")

    print("\nECEF Coordinates:")

    print(f"X = {x:.3f} m")
    print(f"Y = {y:.3f} m")
    print(f"Z = {z:.3f} m")