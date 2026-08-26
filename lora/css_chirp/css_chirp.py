import numpy as np

# Parameters
sample_rate = 100_000
duration = 0.01

start_frequency = 1_000
end_frequency = 10_000

# Time axis
t = np.arange(0, duration, 1 / sample_rate)

# Linear frequency sweep
frequency = np.linspace(
    start_frequency,
    end_frequency,
    len(t)
)

# Integrate frequency to obtain phase
phase = 2 * np.pi * np.cumsum(frequency) / sample_rate

# Generate complex baseband chirp
chirp = np.exp(1j * phase)

print(f"Samples: {len(chirp)}")
print(f"Start frequency: {frequency[0]:.0f} Hz")
print(f"End frequency: {frequency[-1]:.0f} Hz")
print(f"Duration: {duration} s")