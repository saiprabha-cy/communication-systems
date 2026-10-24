
import numpy as np

real_samples = np.array([1.0, 0.5, -0.25], dtype=np.float32)
iq_samples = np.array(
    [1+0j, 0.5+0.25j, -0.25-0.5j],
    dtype=np.complex64
)

vector = np.array([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0]
], dtype=np.float32)

print("Real dtype:", real_samples.dtype)
print("Complex dtype:", iq_samples.dtype)
print("Complex sample size:", iq_samples.itemsize, "bytes")
print("Vector shape:", vector.shape)
print("Vector row count:", vector.shape[0])
print("Vector width:", vector.shape[1])
