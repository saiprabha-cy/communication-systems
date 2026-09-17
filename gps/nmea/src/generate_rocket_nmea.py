import datetime
from pathlib import Path
import pynmea2

# Set destination output path
output_dir = Path(r"D:\communication-systems\gps\nmea\data")
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "rocket_launch.nmea"

# Initial Parameters: Satish Dhawan Space Centre (Sriharikota, India)
lat, lon = 13.7199, 80.2304
altitude = 10.0  # Launchpad elevation (meters)
velocity_mps = 0.0  # Initial speed (m/s)
acceleration_mps2 = 45.0  # ~4.6g ascent acceleration
start_time = datetime.datetime(2026, 9, 13, 6, 0, 0)

# Knots conversion factor
MPS_TO_KNOTS = 1.94384

with open(output_file, "w", newline="\r\n") as f:
    for t in range(120):  # 120-second ascent timeline
        current_time = start_time + datetime.timedelta(seconds=t)
        time_str = current_time.strftime("%H%M%S.00")
        date_str = current_time.strftime("%d%m%y")

        # Flight Dynamics Simulation
        velocity_mps += acceleration_mps2
        speed_knots = velocity_mps * MPS_TO_KNOTS

        # Vertical climb + Downrange velocity shift (moving East toward ocean)
        altitude += velocity_mps * 1.0 + 0.5 * acceleration_mps2 * 1.0
        lat += 0.00002  # Slight North movement
        lon += 0.00025 * (t / 10.0)  # Downrange East acceleration

        # NMEA Format String Formatting
        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lat_nmea = f"{lat_deg:02d}{lat_min:06.3f}"
        lat_dir = "N"

        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60
        lon_nmea = f"{lon_deg:03d}{lon_min:06.3f}"
        lon_dir = "E"

        # SIMULATE STAGE SEPARATION SIGNAL BLACKOUT (t = 50s to t = 55s)
        if 50 <= t <= 55:
            fix_qual = "0"  # Invalid Fix
            status_rmc = "V"  # Void Status
            num_sats = "00"
            hdop = "99.9"  # High HDOP dilution
        else:
            fix_qual = "1"  # Valid Autonomous Fix
            status_rmc = "A"  # Valid Active Status
            num_sats = "09"
            hdop = "1.1"

        # Generate $GPGGA Sentence
        gga = pynmea2.GGA(
            "GP",
            "GGA",
            (
                time_str,
                lat_nmea,
                lat_dir,
                lon_nmea,
                lon_dir,
                fix_qual,
                num_sats,
                hdop,
                f"{altitude:.2f}",
                "M",
                "-28.0",
                "M",
                "",
                "0000",
            ),
        )

        # Generate $GPRMC Sentence
        rmc = pynmea2.RMC(
            "GP",
            "RMC",
            (
                time_str,
                status_rmc,
                lat_nmea,
                lat_dir,
                lon_nmea,
                lon_dir,
                f"{speed_knots:.1f}",
                "090.0",
                date_str,
                "",
                "",
                "A",
            ),
        )

        f.write(str(gga) + "\n")
        f.write(str(rmc) + "\n")

print(f"Successfully generated rocket flight NMEA log at:\n{output_file}")