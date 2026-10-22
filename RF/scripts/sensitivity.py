import numpy as np
import matplotlib.pyplot as plt

def fspl_db(f_ghz, d_km):
    f = np.asarray(f_ghz)
    d = np.asarray(d_km)
    if np.any(f <= 0) or np.any(d <= 0):
        raise ValueError("Frequency and distance must be positive.")
    return 92.45 + 20 * np.log10(f) + 20 * np.log10(d)

def received_power_dbm(
    tx_power_dbm, tx_gain_dbi, rx_gain_dbi,
    tx_loss_db, rx_loss_db, f_ghz, d_km, other_loss_db
):
    return (
        tx_power_dbm
        + tx_gain_dbi
        + rx_gain_dbi
        - tx_loss_db
        - rx_loss_db
        - fspl_db(f_ghz, d_km)
        - other_loss_db
    )

# Baseline scenario
tx_power_dbm = 40.0
tx_gain_dbi = 8.0
rx_gain_dbi = 12.0
tx_loss_db = 1.0
rx_loss_db = 1.5
frequency_ghz = 2.2
distance_km = 500.0
other_loss_db = 2.0

baseline = received_power_dbm(
    tx_power_dbm, tx_gain_dbi, rx_gain_dbi,
    tx_loss_db, rx_loss_db,
    frequency_ghz, distance_km, other_loss_db
)

print("RF-10: Parameter Sensitivity")
print(f"Baseline received power: {baseline:.2f} dBm")

# 1. Frequency sweep
frequencies = np.linspace(0.5, 10.0, 150)
power_frequency = received_power_dbm(
    tx_power_dbm, tx_gain_dbi, rx_gain_dbi,
    tx_loss_db, rx_loss_db,
    frequencies, distance_km, other_loss_db
)

plt.figure()
plt.plot(frequencies, power_frequency)
plt.xlabel("Frequency (GHz)")
plt.ylabel("Received power (dBm)")
plt.title("Sensitivity to Frequency")
plt.grid(True)
plt.tight_layout()

# 2. Distance sweep
distances = np.linspace(100, 2000, 150)
power_distance = received_power_dbm(
    tx_power_dbm, tx_gain_dbi, rx_gain_dbi,
    tx_loss_db, rx_loss_db,
    frequency_ghz, distances, other_loss_db
)

plt.figure()
plt.plot(distances, power_distance)
plt.xlabel("Distance (km)")
plt.ylabel("Received power (dBm)")
plt.title("Sensitivity to Distance")
plt.grid(True)
plt.tight_layout()

# 3. Transmit power sweep
tx_powers = np.linspace(20, 45, 100)
power_tx = received_power_dbm(
    tx_powers, tx_gain_dbi, rx_gain_dbi,
    tx_loss_db, rx_loss_db,
    frequency_ghz, distance_km, other_loss_db
)

plt.figure()
plt.plot(tx_powers, power_tx)
plt.xlabel("Transmit power (dBm)")
plt.ylabel("Received power (dBm)")
plt.title("Sensitivity to Transmit Power")
plt.grid(True)
plt.tight_layout()

# 4. Receive antenna gain sweep
rx_gains = np.linspace(0, 20, 100)
power_gain = received_power_dbm(
    tx_power_dbm, tx_gain_dbi, rx_gains,
    tx_loss_db, rx_loss_db,
    frequency_ghz, distance_km, other_loss_db
)

plt.figure()
plt.plot(rx_gains, power_gain)
plt.xlabel("Receive antenna gain (dBi)")
plt.ylabel("Received power (dBm)")
plt.title("Sensitivity to Receive Antenna Gain")
plt.grid(True)
plt.tight_layout()

plt.show()