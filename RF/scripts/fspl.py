
import math

def fspl_db(frequency_ghz: float, distance_km: float) -> float:
    if frequency_ghz <= 0 or distance_km <= 0:
        raise ValueError("Frequency and distance must be positive.")

    return (
        92.45
        + 20 * math.log10(frequency_ghz)
        + 20 * math.log10(distance_km)
    )

frequency_ghz = 2.2
distance_km = 500.0

loss = fspl_db(frequency_ghz, distance_km)

print("RF-01: Free-Space Path Loss")
print(f"Frequency : {frequency_ghz:.3f} GHz")
print(f"Distance  : {distance_km:.1f} km")
print(f"FSPL      : {loss:.2f} dB")
