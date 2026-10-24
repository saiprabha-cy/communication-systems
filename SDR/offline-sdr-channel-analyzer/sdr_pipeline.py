
from pathlib import Path
import json

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin, lfilter, resample_poly


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

FS_IN = 200_000
DURATION = 1.0
CENTER_HZ = 20_000
CUTOFF_HZ = 5_000
DECIMATION = 2
RNG_SEED = 2026


def generate_recording():
    """Generate a reproducible complex IQ recording."""
    DATA.mkdir(parents=True, exist_ok=True)

    n = int(FS_IN * DURATION)
    t = np.arange(n) / FS_IN
    rng = np.random.default_rng(RNG_SEED)

    wanted = 0.7 * np.exp(1j * 2 * np.pi * 20_000 * t)
    interferer = 0.2 * np.exp(1j * 2 * np.pi * 35_000 * t)

    noise = 0.03 / np.sqrt(2) * (
        rng.standard_normal(n)
        + 1j * rng.standard_normal(n)
    )

    iq = (wanted + interferer + noise).astype(np.complex64)

    path = DATA / "recording.c64"
    iq.tofile(path)

    return path


def read_iq(path):
    """Read interleaved complex float32 samples."""
    iq = np.fromfile(path, dtype=np.complex64)

    if iq.size == 0:
        raise ValueError("IQ file is empty")

    if not np.all(np.isfinite(iq)):
        raise ValueError("IQ file contains invalid samples")

    return iq


def translate_channel(iq, fs, center_hz):
    """Translate a selected channel toward zero frequency."""
    n = np.arange(len(iq))
    oscillator = np.exp(-1j * 2 * np.pi * center_hz * n / fs)
    return iq * oscillator


def filter_and_decimate(iq, fs):
    """Low-pass filter, then reduce the sample rate by two."""
    taps = firwin(
        numtaps=401,
        cutoff=CUTOFF_HZ,
        fs=fs
    )

    filtered = lfilter(taps, 1.0, iq)

    # Keep the even-indexed output samples after filtering.
    output = filtered[::DECIMATION]

    fs_out = fs / DECIMATION
    return output.astype(np.complex64), fs_out, taps


def spectrum(iq, fs):
    """Return a windowed, normalized complex-baseband spectrum."""
    n = len(iq)
    window = np.hanning(n)

    spec = np.fft.fftshift(np.fft.fft(iq * window))
    freq = np.fft.fftshift(np.fft.fftfreq(n, d=1 / fs))

    magnitude = np.abs(spec) / np.sum(window)
    db = 20 * np.log10(np.maximum(magnitude, 1e-12))

    return freq, db


def run_pipeline():
    RESULTS.mkdir(parents=True, exist_ok=True)

    recording = generate_recording()
    iq = read_iq(recording)

    translated = translate_channel(iq, FS_IN, CENTER_HZ)

    output, fs_out, taps = filter_and_decimate(
        translated, FS_IN
    )

    output_path = RESULTS / "filtered_baseband.c64"
    output.tofile(output_path)

    # Save frequency-domain comparison.
    f_in, db_in = spectrum(translated, FS_IN)
    f_out, db_out = spectrum(output, fs_out)

    fig, ax = plt.subplots(2, 1, figsize=(10, 7))

    ax[0].plot(f_in / 1000, db_in)
    ax[0].set_title("Spectrum after frequency translation")
    ax[0].set_ylabel("Magnitude (dB relative to tone)")
    ax[0].set_xlim(-50, 50)
    ax[0].grid(True)

    ax[1].plot(f_out / 1000, db_out)
    ax[1].set_title("Spectrum after filtering and decimation")
    ax[1].set_xlabel("Baseband frequency (kHz)")
    ax[1].set_ylabel("Magnitude (dB relative to tone)")
    ax[1].set_xlim(-50, 50)
    ax[1].grid(True)

    fig.tight_layout()
    fig.savefig(RESULTS / "spectrum_comparison.png", dpi=150)
    plt.close(fig)

    # Ignore the initial FIR transient for the output RMS measurement.
    settled = output[500:]

    metrics = {
        "input_sample_rate_hz": FS_IN,
        "output_sample_rate_hz": fs_out,
        "input_samples": int(len(iq)),
        "output_samples": int(len(output)),
        "input_bytes": int(recording.stat().st_size),
        "output_bytes": int(output_path.stat().st_size),
        "filter_taps": len(taps),
        "group_delay_ms": (len(taps) - 1) / (2 * FS_IN) * 1000,
        "output_rms": float(np.sqrt(np.mean(np.abs(settled)**2))),
        "output_peak": float(np.max(np.abs(settled))),
        "all_output_samples_finite": bool(np.all(np.isfinite(output))),
    }

    with open(RESULTS / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))
    print("\nPipeline complete.")


if __name__ == "__main__":
    run_pipeline()
