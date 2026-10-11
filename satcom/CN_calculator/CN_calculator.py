import math

# Link parameters
f_mhz = 437.0
range_km = 1000.0

tx_power_w = 1.0
tx_gain_dbi = 2.0
tx_feeder_loss_db = 1.0

rx_gain_dbi = 12.0
rx_feeder_loss_db = 1.0
other_losses_db = 2.0

# Receiver parameters
tsys_k = 500.0
bandwidth_hz = 25000.0

# Boltzmann constant in dBW/K/Hz
k_dbw_per_k_hz = -228.599

tx_power_dbw = 10 * math.log10(tx_power_w)

eirp_dbw = (
    tx_power_dbw
    + tx_gain_dbi
    - tx_feeder_loss_db
)

fspl_db = (
    92.45
    + 20 * math.log10(f_mhz / 1000.0)
    + 20 * math.log10(range_km)
)

received_dbw = (
    eirp_dbw
    - fspl_db
    + rx_gain_dbi
    - rx_feeder_loss_db
    - other_losses_db
)

noise_dbw = (
    k_dbw_per_k_hz
    + 10 * math.log10(tsys_k)
    + 10 * math.log10(bandwidth_hz)
)

cn_db = received_dbw - noise_dbw

print(f"Received carrier: {received_dbw:.2f} dBW")
print(f"Thermal noise: {noise_dbw:.2f} dBW")
print(f"C/N: {cn_db:.2f} dB")