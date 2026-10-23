
import numpy as np

def mw_to_dbm(power_mw):
    if power_mw <= 0:
        raise ValueError("Power must be positive")
    return 10 * np.log10(power_mw)

def dbm_to_mw(power_dbm):
    return 10 ** (power_dbm / 10)

for p in [0.1, 1, 10, 100]:
    print(f"{p:6.1f} mW = {mw_to_dbm(p):6.2f} dBm")

for p in [-30, -10, 0, 10]:
    print(f"{p:6.1f} dBm = {dbm_to_mw(p):8.4f} mW")

print("Power gain for +20 dB:", 10 ** (20 / 10), "times")
print("Voltage gain for +20 dB:", 10 ** (20 / 20), "times")
