
import numpy as np
import matplotlib.pyplot as plt

N = 1000
t = np.linspace(0, 1, N, endpoint=False)
x = 0.8 * np.sin(2 * np.pi * 5 * t)

def quantize_signed(x, bits):
    levels = 2 ** bits
    xmax = 1 - 1 / (2 ** (bits - 1))
    x_clip = np.clip(x, -1.0, xmax)
    code = np.round((x_clip + 1.0) * (levels - 1) / 2)
    reconstructed = 2 * code / (levels - 1) - 1.0
    return reconstructed

q8 = quantize_signed(x, 8)
q12 = quantize_signed(x, 12)

print("8-bit levels:", 2**8)
print("12-bit levels:", 2**12)
print("8-bit RMSE:", np.sqrt(np.mean((x - q8)**2)))
print("12-bit RMSE:", np.sqrt(np.mean((x - q12)**2)))

plt.figure(figsize=(10, 4))
plt.plot(t[:120], x[:120], label="Original")
plt.step(t[:120], q8[:120], where="mid", label="8-bit")
plt.step(t[:120], q12[:120], where="mid", label="12-bit")
plt.xlabel("Time (s)")
plt.ylabel("Normalized amplitude")
plt.title("Quantization resolution comparison")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Deliberate clipping experiment
x_over = 1.4 * np.sin(2 * np.pi * 5 * t)
x_clipped = np.clip(x_over, -1, 1)

print("Clipped samples:", np.sum(np.abs(x_over) > 1))
