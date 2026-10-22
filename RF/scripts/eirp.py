
import math

def watts_to_dbw(power_w):
    if power_w <= 0:
        raise ValueError("Power must be positive.")
    return 10 * math.log10(power_w)

def dbw_to_dbm(power_dbw):
    return power_dbw + 30

def calculate_eirp(power_w, antenna_gain_dbi, feeder_loss_db):
    tx_power_dbw = watts_to_dbw(power_w)
    eirp_dbw = tx_power_dbw + antenna_gain_dbi - feeder_loss_db
    return tx_power_dbw, eirp_dbw, dbw_to_dbm(eirp_dbw)

power_w = 10.0
antenna_gain_dbi = 8.0
feeder_loss_db = 1.0

tx_dbw, eirp_dbw, eirp_dbm = calculate_eirp(
    power_w, antenna_gain_dbi, feeder_loss_db
)

print("RF-05: EIRP Calculator")
print(f"Transmitter power : {power_w:.2f} W")
print(f"Transmitter power : {tx_dbw:.2f} dBW")
print(f"Antenna gain      : {antenna_gain_dbi:.2f} dBi")
print(f"Feeder loss       : {feeder_loss_db:.2f} dB")
print(f"EIRP              : {eirp_dbw:.2f} dBW")
print(f"EIRP              : {eirp_dbm:.2f} dBm")
