
import math

def fspl_db(f_ghz, d_km):
    if f_ghz <= 0 or d_km <= 0:
        raise ValueError("Frequency and distance must be positive.")
    return 92.45 + 20 * math.log10(f_ghz) + 20 * math.log10(d_km)

def received_power_dbm(
    tx_power_dbm,
    tx_gain_dbi,
    rx_gain_dbi,
    tx_feeder_loss_db,
    rx_feeder_loss_db,
    fspl,
    other_losses_db
):
    return (
        tx_power_dbm
        + tx_gain_dbi
        + rx_gain_dbi
        - tx_feeder_loss_db
        - rx_feeder_loss_db
        - fspl
        - other_losses_db
    )

tx_power_dbm = 30.0
tx_gain_dbi = 6.0
rx_gain_dbi = 12.0
tx_feeder_loss_db = 1.0
rx_feeder_loss_db = 1.5
frequency_ghz = 2.2
distance_km = 500.0
other_losses_db = 2.0

path_loss_db = fspl_db(frequency_ghz, distance_km)

pr_dbm = received_power_dbm(
    tx_power_dbm,
    tx_gain_dbi,
    rx_gain_dbi,
    tx_feeder_loss_db,
    rx_feeder_loss_db,
    path_loss_db,
    other_losses_db
)

print("RF-06: Received Power")
print(f"FSPL           : {path_loss_db:.2f} dB")
print(f"Received power : {pr_dbm:.2f} dBm")
print(f"Received power : {pr_dbm - 30:.2f} dBW")
