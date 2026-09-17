from sequence_counter import SequenceCounter


def generate_packets(count: int):
    counter = SequenceCounter(start=100)

    packets = []

    for _ in range(count):
        sequence = counter.next()

        packets.append({
            "sequence": sequence,
            "temperature": 25.0 + sequence * 0.01
        })

    return packets


def simulate_loss(packets, lost_sequences):
    received = []

    for packet in packets:
        if packet["sequence"] not in lost_sequences:
            received.append(packet)

    return received


def detect_missing_packets(received):
    missing = []

    for previous, current in zip(received, received[1:]):

        expected = (previous["sequence"] + 1) % 65536

        if current["sequence"] != expected:

            sequence = expected

            while sequence != current["sequence"]:
                missing.append(sequence)
                sequence = (sequence + 1) % 65536

    return missing


if __name__ == "__main__":

    packets = generate_packets(10)

    received = simulate_loss(
        packets,
        lost_sequences={102, 106, 107}
    )

    print("Received sequences:")

    for packet in received:
        print(packet["sequence"])

    missing = detect_missing_packets(received)

    print("\nMissing sequences:")
    print(missing)