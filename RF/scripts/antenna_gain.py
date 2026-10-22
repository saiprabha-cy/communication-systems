
import numpy as np
import matplotlib.pyplot as plt

def fspl_db(f_ghz, d_km):
    return 92.45 + 20 * np.log10(f_ghz) + 20 * np.log10(d_km)

tx_power_dbm = 30.0       # 1 W
tx_gain_dbi = 6.0
distance_km = 500.0
frequency_ghz = 2.2
other_losses_db = 2.0

rx_gains_dbi = np.array([0, 3, 6, 9, 12, 15])
path_loss_db = fspl_db(frequency_ghz, distance_km)

rx_power_dbm = (
    tx_power_dbm
    + tx_gain_dbi
    + rx_gains_dbi
    - path_loss_db
    - other_losses_db
)

print("RF-04: Receive Antenna Gain Effect")
print(f"FSPL: {path_loss_db:.2f} dB\n")

for gain, power in zip(rx_gains_dbi, rx_power_dbm):
    print(f"Rx gain = {gain:2.0f} dBi -> Pr = {power:.2f} dBm")

plt.figure()
plt.plot(rx_gains_dbi, rx_power_dbm, marker="o")
plt.xlabel("Receive antenna gain (dBi)")
plt.ylabel("Received power (dBm)")
plt.title("RF-04: Antenna Gain versus Received Power")
plt.grid(True)
plt.tight_layout()
plt.show()
