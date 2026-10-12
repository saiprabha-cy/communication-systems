import numpy as np
import struct
import matplotlib.pyplot as plt

rng = np.random.default_rng(14)

# Link parameters
fs = 100e3
cfo_hz = 1200.0
ebn0_db = 12.0
preamble_bits = 256


def crc16_x25(data: bytes) -> int:
    """CRC-16/X.25: reflected polynomial 0x8408."""
    crc = 0xFFFF

    for byte in data:
        crc ^= byte

        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1

    return (~crc) & 0xFFFF


# Telemetry fields
sequence = 7
temperature_c = 24.6
battery_v = 3.82

temp_raw = round(temperature_c * 10)
battery_mv = round(battery_v * 1000)

# Explicit little-endian encoding:
# uint8 sequence, int16 temperature x10, uint16 battery mV
payload = struct.pack("<B h H", sequence, temp_raw, battery_mv)

crc = crc16_x25(payload)
frame = payload + struct.pack("<H", crc)

# Convert bytes to MSB-first bits
frame_bits = np.unpackbits(np.frombuffer(frame, dtype=np.uint8))

tx_bits = np.concatenate([
    np.ones(preamble_bits, dtype=int),
    frame_bits.astype(int)
])

# BPSK
tx_symbols = 2 * tx_bits - 1
n = np.arange(len(tx_symbols))

# Frequency offset
rx_cfo = tx_symbols * np.exp(1j * 2*np.pi*cfo_hz*n/fs)

# AWGN
gamma = 10**(ebn0_db/10)
sigma = np.sqrt(1/(2*gamma))
noise = sigma * (
    rng.standard_normal(len(tx_symbols))
    + 1j*rng.standard_normal(len(tx_symbols))
)
rx = rx_cfo + noise

# Estimate CFO using known preamble
pre = rx[:preamble_bits]
products = pre[1:] * np.conj(pre[:-1])
estimated_cfo = fs/(2*np.pi) * np.angle(np.sum(products))

# Compensate
rx_corrected = rx * np.exp(
    -1j*2*np.pi*estimated_cfo*n/fs
)

# Decode frame bits
payload_rx = rx_corrected[preamble_bits:]
detected_bits = (payload_rx.real >= 0).astype(np.uint8)

ber = np.mean(detected_bits != frame_bits)

# Reconstruct bytes
rx_bytes = np.packbits(detected_bits).tobytes()

# Verify CRC
rx_payload = rx_bytes[:-2]
received_crc = struct.unpack("<H", rx_bytes[-2:])[0]
calculated_crc = crc16_x25(rx_payload)
crc_valid = received_crc == calculated_crc

print("SAT-14: TELEMETRY LINK RESULTS")
print(f"Actual CFO:       {cfo_hz:.2f} Hz")
print(f"Estimated CFO:    {estimated_cfo:.2f} Hz")
print(f"Estimation error: {estimated_cfo-cfo_hz:.2f} Hz")
print(f"Eb/N0:            {ebn0_db:.2f} dB")
print(f"BER:              {ber:.6g}")
print(f"CRC valid:        {crc_valid}")

if crc_valid:
    rx_sequence, rx_temp_raw, rx_battery_mv = struct.unpack(
        "<B h H", rx_payload
    )

    print(f"Sequence:         {rx_sequence}")
    print(f"Temperature:      {rx_temp_raw/10:.1f} C")
    print(f"Battery voltage:  {rx_battery_mv/1000:.3f} V")
else:
    print("Frame rejected: CRC verification failed.")

plt.scatter(
    rx_corrected[preamble_bits:].real,
    rx_corrected[preamble_bits:].imag,
    s=16
)
plt.xlabel("In-phase")
plt.ylabel("Quadrature")
plt.title("SAT-14: Received Telemetry Symbols After Compensation")
plt.grid(True)
plt.show()