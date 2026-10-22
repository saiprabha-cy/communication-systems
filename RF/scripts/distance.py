
import numpy as np
import matplotlib.pyplot as plt

def fspl_db(f_ghz, d_km):
    if f_ghz <= 0 or np.any(np.asarray(d_km) <= 0):
        raise ValueError("Frequency and distance must be positive.")
    return 92.45 + 20 * np.log10(f_ghz) + 20 * np.log10(d_km)

frequency_ghz = 2.2
distances_km = np.array([100, 200, 300, 500, 750, 1000, 1500, 2000])

losses_db = fspl_db(frequency_ghz, distances_km)

print("RF-03: Distance Variation")
print(f"Fixed frequency: {frequency_ghz:.2f} GHz\n")

for distance, loss in zip(distances_km, losses_db):
    print(f"{distance:4.0f} km -> FSPL = {loss:.2f} dB")

plt.figure()
plt.plot(distances_km, losses_db, marker="o")
plt.xlabel("Distance (km)")
plt.ylabel("Free-space path loss (dB)")
plt.title("RF-03: FSPL versus Distance")
plt.grid(True)
plt.tight_layout()
plt.show()
