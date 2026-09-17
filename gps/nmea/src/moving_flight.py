import os
from pathlib import Path
import datetime
import pynmea2

# Set destination output directory and file path
output_dir = Path(r"D:\communication-systems\gps\nmea\data")
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "moving_flight.nmea"

# Starting coordinates: Chennai, Tamil Nadu, India
lat, lon = 13.082700, 80.270700
altitude = 10.0  # initial elevation in meters
speed_knots = 20.0  # ~37 km/h moving speed
start_time = datetime.datetime(2026, 9, 12, 18, 43, 53)

with open(output_file, "w", newline="\r\n") as f:
    for i in range(120):  # 120 seconds = 2 minutes of continuous data
        current_time = start_time + datetime.timedelta(seconds=i)
        time_str = current_time.strftime("%H%M%S.00")
        date_str = current_time.strftime("%d%m%y")

        # Simulate movement northeast through Chennai and gradual climb
        lat += 0.00005  # Moving North
        lon += 0.00005  # Moving East
        altitude += 0.15  # Gaining altitude

        # Convert Decimal Degrees to NMEA DDMM.MMMM format
        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lat_nmea = f"{lat_deg:02d}{lat_min:06.3f}"
        lat_dir = 'N' if lat >= 0 else 'S'

        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60
        lon_nmea = f"{lon_deg:03d}{lon_min:06.3f}"
        lon_dir = 'E' if lon >= 0 else 'W'

        # Generate $GPGGA Sentence
        gga = pynmea2.GGA('GP', 'GGA', (
            time_str, lat_nmea, lat_dir, lon_nmea, lon_dir,
            '1', '08', '1.2', f"{altitude:.2f}", 'M', '-33.9', 'M', '', '0000'
        ))

        # Generate $GPRMC Sentence
        rmc = pynmea2.RMC('GP', 'RMC', (
            time_str, 'A', lat_nmea, lat_dir, lon_nmea, lon_dir,
            f"{speed_knots:.1f}", '045.0', date_str, '', '', 'A'
        ))

        f.write(str(gga) + "\n")
        f.write(str(rmc) + "\n")

print(f"Successfully saved 120 NMEA trajectory points to:\n{output_file}")