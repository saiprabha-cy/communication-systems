import math

f_mhz = 437.0
range_km = 1000.0

tx_power_w = 1.0
tx_gain_dbi = 2.0
tx_feeder_loss_db = 1.0

rx_gain_dbi = 12.0
rx_feeder_loss_db = 1.0
other_losses_db = 2.0

tx_power_dbw = 10 * math.log10(tx_power_w)

eirp_dbw = (
    tx_power_dbw
    + tx_gain_dbi
    - tx_feeder_loss_db
)

f_ghz = f_mhz / 1000.0

fspl_db = (
    92.45
    + 20 * math.log10(f_ghz)
    + 20 * math.log10(range_km)
)

received_dbw = (
    eirp_dbw
    - fspl_db
    + rx_gain_dbi
    - rx_feeder_loss_db
    - other_losses_db
)

received_dbm = received_dbw + 30

print(f"FSPL: {fspl_db:.2f} dB")
print(f"EIRP: {eirp_dbw:.2f} dBW")
print(f"Received power: {received_dbw:.2f} dBW")
print(f"Received power: {received_dbm:.2f} dBm")