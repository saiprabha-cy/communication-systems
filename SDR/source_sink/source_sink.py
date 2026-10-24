
import numpy as np
from pathlib import Path

out = Path("synthetic_iq.c64")

fs = 100_000
duration = 1.0
N = int(fs * duration)
t = np.arange(N) / fs

iq = (
    0.7 * np.exp(1j * 2 * np.pi * 5_000 * t)
    + 0.2 * np.exp(1j * 2 * np.pi * 15_000 * t)
).astype(np.complex64)

iq.tofile(out)

print("File:", out.resolve())
print("Samples:", len(iq))
print("Bytes:", out.stat().st_size)
print("Expected bytes:", N * 8)
