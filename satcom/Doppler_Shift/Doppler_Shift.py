import numpy as np
import matplotlib.pyplot as plt

c = 299_792_458.0
fc = 437e6

t = np.linspace(-300, 300, 601)

# Illustrative range-rate profile
vr = 7000 * np.sin(2 * np.pi * t / 1200)

fd = -(vr / c) * fc
frx = fc + fd

print("SAT-12: DOPPLER SHIFT")
print(f"Carrier frequency: {fc / 1e6:.3f} MHz")
print(f"Maximum absolute shift: {np.max(np.abs(fd)):.2f} Hz")
print(f"Received frequency range: "
      f"{np.min(frx) / 1e6:.6f} to {np.max(frx) / 1e6:.6f} MHz")

fig, axes = plt.subplots(2, 1, figsize=(9, 6))

axes[0].plot(t, vr / 1000)
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Radial velocity (km/s)")
axes[0].set_title("Illustrative Satellite Radial Velocity")
axes[0].grid(True)

axes[1].plot(t, fd / 1000)
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Doppler shift (kHz)")
axes[1].set_title("SAT-12: Doppler Shift at 437 MHz")
axes[1].grid(True)

plt.tight_layout()
plt.show()