import socket

from validator import validate_packet
from deserializer import deserialize_telemetry


HOST = "127.0.0.1"
PORT = 5005
BUFFER_SIZE = 1024


def run_ground_station():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    print("=== GROUND STATION ===")
    print(f"Listening on {HOST}:{PORT}")

    while True:

        frame, address = sock.recvfrom(BUFFER_SIZE)

        print(f"\nReceived {len(frame)} bytes from {address}")

        if not validate_packet(frame):
            print("STATUS: REJECTED")
            continue

        payload_length = frame[2]
        payload = frame[3:3 + payload_length]

        telemetry = deserialize_telemetry(payload)

        print("STATUS: VALID")
        print(f"Spacecraft ID : {telemetry.spacecraft_id}")
        print(f"Timestamp     : {telemetry.timestamp}")
        print(f"Temperature   : {telemetry.temperature_c:.1f} C")
        print(f"Voltage       : {telemetry.voltage_v:.2f} V")
        print(f"Current       : {telemetry.current_a:.2f} A")
        print(f"Sequence      : {telemetry.sequence}")


if __name__ == "__main__":
    run_ground_station()