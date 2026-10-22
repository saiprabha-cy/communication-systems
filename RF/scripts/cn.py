
import math

def noise_power_dbm(bandwidth_hz, noise_figure_db):
    if bandwidth_hz <= 0:
        raise ValueError("Bandwidth must be positive.")

    thermal_noise_density_dbm_hz = -174.0
    return (
        thermal_noise_density_dbm_hz
        + 10 * math.log10(bandwidth_hz)
        + noise_figure_db
    )

received_power_dbm = -97.78
bandwidth_hz = 1_000_000
noise_figure_db = 3.0

noise_dbm = noise_power_dbm(bandwidth_hz, noise_figure_db)
cn_db = received_power_dbm - noise_dbm

print("RF-08: Carrier-to-Noise Ratio")
print(f"Received carrier : {received_power_dbm:.2f} dBm")
print(f"Bandwidth        : {bandwidth_hz:.0f} Hz")
print(f"Noise figure     : {noise_figure_db:.2f} dB")
print(f"Noise power      : {noise_dbm:.2f} dBm")
print(f"C/N              : {cn_db:.2f} dB")
