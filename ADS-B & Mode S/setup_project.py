from pathlib import Path

DIRECTORIES = [
    "data/iq",
    "data/frames",
    "data/observations",
    "plots",
    "reports",
    "src",
    "tests",
]

def main():
    for name in DIRECTORIES:
        path = Path(name)
        path.mkdir(parents=True, exist_ok=True)
        print(f"READY: {path}")

    print("\nADS-B / Mode S project directories created.")

if __name__ == "__main__":
    main()