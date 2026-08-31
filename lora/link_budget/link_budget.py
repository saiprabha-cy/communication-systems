import math


def fspl(distance_km, frequency_mhz):
    """
    Calculate Free-Space Path Loss.

    distance_km   : distance in kilometres
    frequency_mhz : frequency in MHz
    return        : path loss in dB
    """

    return (
        32.44
        + 20 * math.log10(distance_km)
        + 20 * math.log10(frequency_mhz)
    )


def received_power(tx_power_dbm,
                   tx_gain_dbi,
                   rx_gain_dbi,
                   path_loss_db,
                   other_losses_db):

    return (
        tx_power_dbm
        + tx_gain_dbi
        + rx_gain_dbi
        - path_loss_db
        - other_losses_db
    )


def link_margin(received_power_dbm, sensitivity_dbm):

    return received_power_dbm - sensitivity_dbm


# --------------------------------------------------
# LoRa Link Parameters
# --------------------------------------------------

frequency_mhz = 868
distance_km = 10

tx_power_dbm = 20

tx_gain_dbi = 2
rx_gain_dbi = 2

other_losses_db = 3

receiver_sensitivity_dbm = -120


# --------------------------------------------------
# Calculations
# --------------------------------------------------

path_loss_db = fspl(
    distance_km,
    frequency_mhz
)

received_power_dbm = received_power(
    tx_power_dbm,
    tx_gain_dbi,
    rx_gain_dbi,
    path_loss_db,
    other_losses_db
)

margin_db = link_margin(
    received_power_dbm,
    receiver_sensitivity_dbm
)


# --------------------------------------------------
# Results
# --------------------------------------------------

print("========== LoRa Link Budget ==========")

print(f"Frequency       : {frequency_mhz} MHz")
print(f"Distance        : {distance_km} km")

print(f"Tx Power        : {tx_power_dbm:.2f} dBm")
print(f"Tx Antenna Gain : {tx_gain_dbi:.2f} dBi")
print(f"Rx Antenna Gain : {rx_gain_dbi:.2f} dBi")

print(f"Path Loss       : {path_loss_db:.2f} dB")
print(f"Other Losses    : {other_losses_db:.2f} dB")

print("--------------------------------------")

print(f"Received Power  : {received_power_dbm:.2f} dBm")
print(f"Rx Sensitivity  : {receiver_sensitivity_dbm:.2f} dBm")
print(f"Link Margin     : {margin_db:.2f} dB")

print("--------------------------------------")

if margin_db > 0:
    print("LINK STATUS     : LINK POSSIBLE")
else:
    print("LINK STATUS     : LINK NOT POSSIBLE")