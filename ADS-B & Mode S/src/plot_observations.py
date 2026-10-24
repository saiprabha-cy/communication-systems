from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path("data/observations/sample_observations.csv")
PLOT_PATH = Path("plots/aircraft_observations.png")


def create_synthetic_observations(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    # Demonstration points only; not real aircraft observations.
    data = pd.DataFrame(
        [
            {
                "timestamp_utc": "2026-10-24T10:00:00Z",
                "icao": "ABC123",
                "latitude": 13.00,
                "longitude": 80.10,
                "altitude_ft": 12000,
                "ground_speed_kt": 240,
                "source": "synthetic",
            },
            {
                "timestamp_utc": "2026-10-24T10:00:05Z",
                "icao": "ABC123",
                "latitude": 13.05,
                "longitude": 80.16,
                "altitude_ft": 12200,
                "ground_speed_kt": 242,
                "source": "synthetic",
            },
            {
                "timestamp_utc": "2026-10-24T10:00:10Z",
                "icao": "ABC123",
                "latitude": 13.10,
                "longitude": 80.22,
                "altitude_ft": 12400,
                "ground_speed_kt": 245,
                "source": "synthetic",
            },
            {
                "timestamp_utc": "2026-10-24T10:00:00Z",
                "icao": "DEF456",
                "latitude": 12.85,
                "longitude": 80.35,
                "altitude_ft": 9000,
                "ground_speed_kt": 210,
                "source": "synthetic",
            },
            {
                "timestamp_utc": "2026-10-24T10:00:05Z",
                "icao": "DEF456",
                "latitude": 12.91,
                "longitude": 80.30,
                "altitude_ft": 8800,
                "ground_speed_kt": 208,
                "source": "synthetic",
            },
        ]
    )

    data.to_csv(path, index=False)


def main() -> None:
    if not DATA_PATH.exists():
        create_synthetic_observations(DATA_PATH)
        print(f"Created demonstration data: {DATA_PATH}")

    data = pd.read_csv(DATA_PATH)

    required = {
        "timestamp_utc",
        "icao",
        "latitude",
        "longitude",
        "altitude_ft",
        "ground_speed_kt",
    }
    missing = required - set(data.columns)

    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")

    data["latitude"] = pd.to_numeric(data["latitude"], errors="raise")
    data["longitude"] = pd.to_numeric(data["longitude"], errors="raise")

    if not data["latitude"].between(-90, 90).all():
        raise ValueError("Latitude outside [-90, 90].")

    if not data["longitude"].between(-180, 180).all():
        raise ValueError("Longitude outside [-180, 180].")

    fig, ax = plt.subplots(figsize=(9, 6))

    for icao, group in data.groupby("icao"):
        group = group.sort_values("timestamp_utc")
        ax.plot(
            group["longitude"],
            group["latitude"],
            marker="o",
            linewidth=1.5,
            label=icao,
        )

        for _, row in group.iterrows():
            ax.annotate(
                str(row["timestamp_utc"])[11:19],
                (row["longitude"], row["latitude"]),
                fontsize=7,
            )

    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Aircraft Observation Plot — Synthetic Demonstration Data")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PLOT_PATH, dpi=160)
    plt.show()

    print(f"Observations plotted: {len(data)}")
    print(f"Aircraft identifiers: {data['icao'].nunique()}")
    print(f"Plot saved: {PLOT_PATH}")


if __name__ == "__main__":
    main()