import numpy as np
import matplotlib.pyplot as plt

def fspl_db(f_ghz, d_km):
    f = np.asarray(f_ghz)
    d = np.asarray(d_km)
    if np.any(f <= 0) or np.any(d <= 0):
        raise ValueError("Inputs must be positive.")
    return 92.45 + 20 * np.log10(f) + 20 * np.log10(d)

distance_km = 500.0
frequencies_ghz = np.array([1.0, 2.2, 4.0, 8.0])

losses_db = fspl_db(frequencies_ghz, distance_km)

print("RF-02: Frequency Variation")
print(f"Fixed distance: {distance_km:.1f} km\n")

for frequency, loss in zip(frequencies_ghz, losses_db):
    print(f"{frequency:4.1f} GHz -> FSPL = {loss:.2f} dB")

plt.figure()
plt.plot(frequencies_ghz, losses_db, marker="o")
plt.xlabel("Frequency (GHz)")
plt.ylabel("Free-space path loss (dB)")
plt.title("RF-02: FSPL versus Frequency")
plt.grid(True)
plt.tight_layout()
plt.show()