RAW_SAMPLES = [
    0,
    16384,
    -16384,
    8192,
    -8192,
]
def print_raw_samples(samples):

    print("=== RAW ACCELEROMETER DATA ===")

    for index, raw in enumerate(samples):
        print(f"Sample {index}: raw = {raw}")


if __name__ == "__main__":

    samples = [
        0,
        16384,
        -16384,
        8192,
        -8192,
    ]

    print_raw_samples(samples)