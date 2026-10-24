import math

CPR_SCALE = 131072.0  # 2^17


def cpr_nl(latitude: float) -> int:
    """Number of longitude zones at the given latitude."""
    lat = abs(latitude)

    if lat >= 87.0:
        return 1
    if lat > 90.0:
        raise ValueError("Latitude must be within [-90, 90].")
    if lat == 0.0:
        return 59

    numerator = 1.0 - math.cos(math.pi / 30.0)
    denominator = math.cos(math.radians(lat)) ** 2
    argument = 1.0 - numerator / denominator

    # Guard against small floating-point excursions outside [-1, 1].
    argument = min(1.0, max(-1.0, argument))
    result = math.floor(2.0 * math.pi / math.acos(argument))
    return max(1, min(59, result))


def decode_global_airborne_cpr(
    even_lat: int,
    even_lon: int,
    odd_lat: int,
    odd_lon: int,
    even_timestamp: float,
    odd_timestamp: float,
) -> tuple[float, float]:
    """
    Decode a matched even/odd airborne CPR pair.

    Encoded coordinates must be integers in [0, 131071].
    Timestamps must use the same time base.
    """
    values = (even_lat, even_lon, odd_lat, odd_lon)

    if any(not isinstance(value, int) for value in values):
        raise TypeError("CPR coordinates must be integers.")

    if any(value < 0 or value >= 131072 for value in values):
        raise ValueError("CPR fields must be 17-bit unsigned values.")

    j = math.floor(
        (59 * even_lat / CPR_SCALE - 60 * odd_lat / CPR_SCALE) + 0.5
    )

    lat_even = 6.0 * ((j % 60) + even_lat / CPR_SCALE)
    lat_odd = (360.0 / 59.0) * ((j % 59) + odd_lat / CPR_SCALE)

    if lat_even >= 270.0:
        lat_even -= 360.0
    if lat_odd >= 270.0:
        lat_odd -= 360.0

    if abs(lat_even) > 90.0 or abs(lat_odd) > 90.0:
        raise ValueError("Decoded latitude is outside the valid range.")

    if cpr_nl(lat_even) != cpr_nl(lat_odd):
        raise ValueError("Even/odd CPR latitude zones are inconsistent.")

    use_odd = odd_timestamp > even_timestamp
    latitude = lat_odd if use_odd else lat_even

    nl = cpr_nl(latitude)
    ni = max(nl - 1, 1) if use_odd else max(nl, 1)

    m = math.floor(
        (
            even_lon * (nl - 1) / CPR_SCALE
            - odd_lon * nl / CPR_SCALE
        ) + 0.5
    )

    if use_odd:
        longitude = (360.0 / ni) * ((m % ni) + odd_lon / CPR_SCALE)
    else:
        longitude = (360.0 / ni) * ((m % ni) + even_lon / CPR_SCALE)

    if longitude > 180.0:
        longitude -= 360.0

    return latitude, longitude


def main() -> None:
    # Synthetic encoded coordinates used to test ranges and execution.
    # These values are not a known aircraft position test vector.
    even_lat = 93000
    even_lon = 51372
    odd_lat = 74120
    odd_lon = 110234

    try:
        latitude, longitude = decode_global_airborne_cpr(
            even_lat=even_lat,
            even_lon=even_lon,
            odd_lat=odd_lat,
            odd_lon=odd_lon,
            even_timestamp=10.0,
            odd_timestamp=11.0,
        )
    except ValueError as exc:
        print(f"Pair rejected: {exc}")
        print("This is acceptable for an arbitrary synthetic pair.")
        return

    print(f"Latitude:  {latitude:.6f}")
    print(f"Longitude: {longitude:.6f}")
    assert -90 <= latitude <= 90
    assert -180 <= longitude <= 180


if __name__ == "__main__":
    main()