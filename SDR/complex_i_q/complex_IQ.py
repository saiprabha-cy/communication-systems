
import numpy as np
import matplotlib.pyplot as plt

fs = 10_000       # Sampling frequency: 10 kHz
f = 1_000         # Tone frequency: 1 kHz
duration = 0.005  # 5 milliseconds
A = 1.0

t = np.arange(int(fs * duration)) / fs
iq = A * np.exp(1j * 2 * np.pi * f * t)

I = iq.real
Q = iq.imag

fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
ax[0].plot(t * 1000, I, label="I")
ax[0].plot(t * 1000, Q, label="Q")
ax[0].set_ylabel("Amplitude")
ax[0].set_title("Complex I/Q samples")
ax[0].legend()
ax[0].grid(True)

ax[1].plot(I, Q, ".-")
ax[1].set_xlabel("I")
ax[1].set_ylabel("Q")
ax[1].set_title("I/Q constellation: circular trajectory")
ax[1].axis("equal")
ax[1].grid(True)

plt.tight_layout()
plt.show()

print("Sample count:", len(iq))
print("First complex sample:", iq[0])
print("I peak:", np.max(np.abs(I)))
print("Q peak:", np.max(np.abs(Q)))
