import math

tx_power_w = 1.0
antenna_gain_dbi = 2.0
feeder_loss_db = 1.0
pointing_loss_db = 0.0

tx_power_dbw = 10 * math.log10(tx_power_w)

eirp_dbw = (
    tx_power_dbw
    + antenna_gain_dbi
    - feeder_loss_db
    - pointing_loss_db
)

eirp_dbm = eirp_dbw + 30
eirp_w_equivalent = 10 ** (eirp_dbw / 10)

print(f"EIRP: {eirp_dbw:.2f} dBW")
print(f"EIRP: {eirp_dbm:.2f} dBm")
print(f"Equivalent isotropic power: {eirp_w_equivalent:.3f} W")