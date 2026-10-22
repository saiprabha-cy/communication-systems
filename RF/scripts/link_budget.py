
import math

def fspl_db(f_ghz, d_km):
    if f_ghz <= 0 or d_km <= 0:
        raise ValueError("Frequency and distance must be positive.")
    return 92.45 + 20 * math.log10(f_ghz) + 20 * math.log10(d_km)

# Hypothetical link parameters
tx_power_w = 10.0
tx_gain_dbi = 8.0
tx_feeder_loss_db = 1.0

rx_gain_dbi = 12.0
rx_feeder_loss_db = 1.5

frequency_ghz = 2.2
distance_km = 500.0

# Combined atmospheric, pointing, polarization, and other losses
other_losses_db = 2.0

tx_power_dbw = 10 * math.log10(tx_power_w)
tx_power_dbm = tx_power_dbw + 30

eirp_dbw = tx_power_dbw + tx_gain_dbi - tx_feeder_loss_db
eirp_dbm = eirp_dbw + 30

path_loss_db = fspl_db(frequency_ghz, distance_km)

received_dbm = (
    eirp_dbm
    + rx_gain_dbi
    - rx_feeder_loss_db
    - path_loss_db
    - other_losses_db
)

received_dbw = received_dbm - 30

print("RF-07: Satellite Link Budget")
print("-" * 42)
print(f"Transmit power       : {tx_power_dbm:8.2f} dBm")
print(f"Transmit antenna gain: {tx_gain_dbi:8.2f} dBi")
print(f"Transmit feeder loss : {-tx_feeder_loss_db:8.2f} dB")
print(f"EIRP                 : {eirp_dbm:8.2f} dBm")
print(f"Receive antenna gain : {rx_gain_dbi:8.2f} dBi")
print(f"Receive feeder loss  : {-rx_feeder_loss_db:8.2f} dB")
print(f"Free-space path loss : {-path_loss_db:8.2f} dB")
print(f"Other losses         : {-other_losses_db:8.2f} dB")
print("-" * 42)
print(f"Received power       : {received_dbm:8.2f} dBm")
print(f"Received power       : {received_dbw:8.2f} dBW")
