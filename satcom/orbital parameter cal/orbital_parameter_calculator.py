import math

# SAT-01: Orbital Parameter Calculator
# Model: Ideal two-body orbit around Earth
# Units: km, seconds, radians

MU = 398600.4418  # Earth gravitational parameter (km^3/s^2)
RE = 6378.137     # Reference equatorial radius (km)


def calculate_orbit(perigee_altitude_km, eccentricity):
    if perigee_altitude_km <= 0:
        raise ValueError("Altitude must be greater than zero.")

    if not 0 <= eccentricity < 1:
        raise ValueError("Use an eccentricity between 0 and 1.")

    # Perigee radius
    rp = RE + perigee_altitude_km

    # Semi-major axis
    a = rp / (1 - eccentricity)

    # Apogee radius
    ra = a * (1 + eccentricity)

    # Altitudes above the reference Earth radius
    hp = rp - RE
    ha = ra - RE

    # Orbital period
    period_s = 2 * math.pi * math.sqrt(a**3 / MU)

    # Vis-viva equation
    vp = math.sqrt(MU * (2 / rp - 1 / a))
    va = math.sqrt(MU * (2 / ra - 1 / a))

    # Mean motion
    mean_motion_rad_s = math.sqrt(MU / a**3)
    mean_motion_rev_day = mean_motion_rad_s * 86400 / (2 * math.pi)

    # Specific orbital energy
    energy = -MU / (2 * a)

    return {
        "semi_major_axis_km": a,
        "eccentricity": eccentricity,
        "perigee_altitude_km": hp,
        "apogee_altitude_km": ha,
        "period_seconds": period_s,
        "period_minutes": period_s / 60,
        "perigee_velocity_km_s": vp,
        "apogee_velocity_km_s": va,
        "mean_motion_rad_s": mean_motion_rad_s,
        "mean_motion_rev_day": mean_motion_rev_day,
        "specific_energy_km2_s2": energy,
    }


if __name__ == "__main__":
    result = calculate_orbit(
        perigee_altitude_km=550,
        eccentricity=0.0,
    )

    print("\nSAT-01: ORBITAL PARAMETER CALCULATOR")
    print("-" * 42)

    for name, value in result.items():
        print(f"{name:30s}: {value:.6f}")