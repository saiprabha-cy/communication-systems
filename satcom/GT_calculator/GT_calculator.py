import math

rx_antenna_gain_dbi = 12.0
system_noise_temperature_k = 500.0

if system_noise_temperature_k <= 0:
    raise ValueError("Noise temperature must be positive.")

gt_db_per_k = (
    rx_antenna_gain_dbi
    - 10 * math.log10(system_noise_temperature_k)
)

print(f"Antenna gain: {rx_antenna_gain_dbi:.2f} dBi")
print(f"System noise temperature: {system_noise_temperature_k:.2f} K")
print(f"G/T: {gt_db_per_k:.2f} dB/K")