#!/usr/bin/env python3
"""
NOAA APT Offline Signal-Processing Lab
======================================

Capabilities
------------
1. Generate a synthetic APT-like audio recording.
2. Load demodulated APT audio from WAV.
3. Load complex64 IQ and perform FM discrimination.
4. Apply a known complex-IQ frequency-offset correction.
5. Inspect the time-domain waveform and frequency spectrum.
6. Recover the AM envelope and resample to the APT pixel clock.
7. Detect channel-A synchronization templates.
8. Reconstruct APT channel A and channel B images.
9. Save plots, pixel arrays, and JSON quality reports.
10. Compare two reconstructed grayscale images.
11. Calculate a theoretical Doppler shift.
12. Optionally predict satellite passes from a local TLE file.
13. Run a controlled synthetic noise experiment.

Limitations
-----------
- Synthetic synchronization waveforms are teaching templates, not a
  complete substitute for standard-verified APT synchronization handling.
- FM IQ input must contain a suitable captured satellite channel.
- IQ must be complex64 interleaved I/Q samples, with sample rate and
  FM deviation specified by the user.
- The IQ file must already be centered sufficiently close to the
  desired signal. A large unknown offset may require spectrum inspection.
- Real APT decoding should be cross-checked against an independent
  decoder and a known reference recording.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from math import gcd
from pathlib import Path
import json

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from scipy.io import wavfile
from scipy.signal import (
    butter,
    sosfiltfilt,
    hilbert,
    resample_poly,
    correlate,
    find_peaks,
    welch,
)
from scipy.ndimage import gaussian_filter1d


# ---------------------------------------------------------------------
# APT FORMAT CONSTANTS
# ---------------------------------------------------------------------

PIXEL_RATE = 4160
LINE_RATE = 2.0
PIXELS_PER_LINE = 2080
SUBCARRIER_HZ = 2400.0

CHANNEL_A_START = 0
CHANNEL_A_END = 909

TELEMETRY_A_START = 909
TELEMETRY_A_END = 954

SYNC_A_START = 954
SYNC_A_END = 993

SPACE_A_START = 993
SPACE_A_END = 1040

CHANNEL_B_START = 1040
CHANNEL_B_END = 1949

TELEMETRY_B_START = 1949
TELEMETRY_B_END = 1994

SYNC_B_START = 1994
SYNC_B_END = 2033

SPACE_B_START = 2033
SPACE_B_END = 2080


# ---------------------------------------------------------------------
# GENERAL UTILITIES
# ---------------------------------------------------------------------

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def json_write(path: Path, data: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def normalize_u8(values: np.ndarray) -> np.ndarray:
    """Percentile-stretch numeric data into an 8-bit grayscale image."""
    values = np.asarray(values, dtype=np.float64)

    if values.size == 0:
        raise ValueError("Cannot normalize an empty array.")

    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.zeros(values.shape, dtype=np.uint8)

    low, high = np.percentile(finite, [1, 99])

    if high <= low:
        return np.zeros(values.shape, dtype=np.uint8)

    normalized = (values - low) / (high - low)
    normalized = np.clip(normalized, 0.0, 1.0)
    normalized[~np.isfinite(normalized)] = 0.0

    return np.round(normalized * 255).astype(np.uint8)


def save_grayscale(path: Path, values: np.ndarray) -> None:
    ensure_dir(path.parent)
    Image.fromarray(normalize_u8(values), mode="L").save(path)


def image_metrics(reference: np.ndarray, test: np.ndarray) -> dict:
    """Compare equally shaped images after their chosen intensity scaling."""
    ref = np.asarray(reference, dtype=np.float64)
    tst = np.asarray(test, dtype=np.float64)

    if ref.shape != tst.shape:
        raise ValueError(
            f"Image dimensions differ: {ref.shape} versus {tst.shape}"
        )

    difference = tst - ref
    mae = float(np.mean(np.abs(difference)))
    rmse = float(np.sqrt(np.mean(difference ** 2)))

    if rmse == 0:
        psnr = float("inf")
    else:
        psnr = float(20.0 * np.log10(255.0 / rmse))

    ref_std = float(np.std(ref))
    tst_std = float(np.std(tst))

    if ref_std > 0 and tst_std > 0:
        corr = float(np.corrcoef(ref.ravel(), tst.ravel())[0, 1])
    else:
        corr = None

    return {
        "width": int(ref.shape[1]),
        "height": int(ref.shape[0]),
        "mae": mae,
        "rmse": rmse,
        "psnr_db": psnr,
        "correlation": corr,
    }


# ---------------------------------------------------------------------
# RECORDING INPUT
# ---------------------------------------------------------------------

def correct_iq_offset(
    iq: np.ndarray,
    fs: int,
    offset_hz: float,
) -> np.ndarray:
    """
    Remove a known complex-baseband frequency offset.

    The caller must confirm the sign of offset_hz from the receiver's
    frequency convention and the measured spectrum.
    """
    if fs <= 0:
        raise ValueError("Sample rate must be positive.")

    n = np.arange(iq.size, dtype=np.float64)
    oscillator = np.exp(-2j * np.pi * offset_hz * n / fs)

    return iq * oscillator


def fm_demodulate(
    iq: np.ndarray,
    fs: int,
    deviation_hz: float,
) -> np.ndarray:
    """
    FM discriminator.

    The result is proportional to instantaneous frequency deviation,
    normalized by the specified peak deviation.
    """
    if iq.size < 2:
        raise ValueError("IQ recording needs at least two samples.")

    if fs <= 0 or deviation_hz <= 0:
        raise ValueError("Sample rate and FM deviation must be positive.")

    phase_difference = np.angle(iq[1:] * np.conj(iq[:-1]))
    instantaneous_frequency = phase_difference * fs / (2.0 * np.pi)

    return instantaneous_frequency / deviation_hz


def load_recording(
    path: Path,
    is_iq: bool,
    fs: int | None,
    deviation_hz: float,
    offset_hz: float,
) -> tuple[np.ndarray, int, dict]:
    """
    Load a WAV audio file or raw complex64 IQ recording.

    WAV input is assumed to be demodulated APT audio.
    IQ input is FM-demodulated here.
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if is_iq:
        if fs is None or fs <= 0:
            raise ValueError("--fs is required for IQ input.")

        iq = np.fromfile(path, dtype=np.complex64)

        if iq.size == 0:
            raise ValueError("IQ file is empty.")

        if not np.all(np.isfinite(iq)):
            raise ValueError("IQ contains NaN or infinite values.")

        if offset_hz != 0:
            iq = correct_iq_offset(iq, fs, offset_hz)

        audio = fm_demodulate(iq, fs, deviation_hz)

        metadata = {
            "input_file": str(path),
            "input_type": "complex64_iq",
            "sample_rate_hz": fs,
            "input_samples": int(iq.size),
            "input_bytes": int(path.stat().st_size),
            "fm_deviation_hz": deviation_hz,
            "iq_offset_correction_hz": offset_hz,
        }

        return audio.astype(np.float64), fs, metadata

    sample_rate, raw = wavfile.read(path)

    if raw.size == 0:
        raise ValueError("Audio file is empty.")

    if np.issubdtype(raw.dtype, np.integer):
        scale = float(max(abs(np.iinfo(raw.dtype).min),
                          np.iinfo(raw.dtype).max))
        audio = raw.astype(np.float64) / scale
    else:
        audio = raw.astype(np.float64)

    if audio.ndim == 2:
        audio = np.mean(audio, axis=1)

    if audio.ndim != 1:
        raise ValueError("Expected mono or stereo WAV audio.")

    if not np.all(np.isfinite(audio)):
        raise ValueError("Audio contains NaN or infinite values.")

    if offset_hz != 0:
        raise ValueError(
            "IQ frequency correction is only valid for IQ input."
        )

    metadata = {
        "input_file": str(path),
        "input_type": "demodulated_wav_audio",
        "sample_rate_hz": int(sample_rate),
        "input_samples": int(audio.size),
        "input_bytes": int(path.stat().st_size),
    }

    return audio, int(sample_rate), metadata


# ---------------------------------------------------------------------
# APT SIGNAL PROCESSING
# ---------------------------------------------------------------------

def recover_pixel_stream(audio: np.ndarray, fs: int) -> np.ndarray:
    """
    Approximate the APT image-video envelope.

    1. Retain the subcarrier and its sidebands.
    2. Estimate the AM envelope using the analytic signal.
    3. Remove residual high-frequency ripple.
    4. Resample to the nominal 4160-pixel/s clock.
    """
    if audio.size < 256:
        raise ValueError("Recording is too short for reliable filtering.")

    if fs <= 0:
        raise ValueError("Sample rate must be positive.")

    high_cutoff = min(4500.0, 0.45 * fs)
    low_cutoff = 300.0

    if high_cutoff <= low_cutoff:
        raise ValueError(
            "Input sample rate is too low for the configured APT filter."
        )

    bandpass_sos = butter(
        5,
        [low_cutoff, high_cutoff],
        btype="bandpass",
        fs=fs,
        output="sos",
    )

    filtered = sosfiltfilt(bandpass_sos, audio)
    envelope = np.abs(hilbert(filtered))

    envelope_cutoff = min(2000.0, 0.45 * fs)

    lowpass_sos = butter(
        5,
        envelope_cutoff,
        btype="lowpass",
        fs=fs,
        output="sos",
    )

    envelope = sosfiltfilt(lowpass_sos, envelope)

    # Convert fs samples/s to 4160 pixels/s using an exact rational ratio.
    divisor = gcd(int(fs), PIXEL_RATE)
    up = PIXEL_RATE // divisor
    down = int(fs) // divisor

    pixels = resample_poly(envelope, up=up, down=down)

    if pixels.size < PIXELS_PER_LINE:
        raise ValueError("Not enough recovered samples for one APT line.")

    return pixels.astype(np.float64)


# ---------------------------------------------------------------------
# SYNCHRONIZATION TEMPLATE
# ---------------------------------------------------------------------

def make_sync_template(
    frequency_hz: float,
    length: int = 39,
) -> np.ndarray:
    """
    Generate a simplified teaching synchronization template.

    This model uses seven sinusoidal cycles followed by a constant
    remainder. It is intended for the synthetic generator and for
    demonstrating matched filtering. Verify templates against a
    standard or trusted decoder before using them on real APT.
    """
    if frequency_hz <= 0:
        raise ValueError("Sync frequency must be positive.")

    n = np.arange(length, dtype=np.float64)
    template = np.full(length, 0.5, dtype=np.float64)

    cycle_pixels = PIXEL_RATE / frequency_hz
    active_pixels = min(length, int(round(7 * cycle_pixels)))

    template[:active_pixels] = (
        0.5
        + 0.45
        * np.sin(
            2.0 * np.pi * frequency_hz
            * n[:active_pixels] / PIXEL_RATE
        )
    )

    return template


def detect_sync_positions(
    pixels: np.ndarray,
    threshold: float = 0.25,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Find channel-A sync candidates using normalized template correlation.

    Returns:
        sync_positions: estimated pixel indices of sync-template starts
        scores: normalized correlation scores at those positions
    """
    template = make_sync_template(1040.0)
    template = template - np.mean(template)

    if pixels.size < template.size:
        return np.array([], dtype=int), np.array([], dtype=float)

    raw_corr = correlate(
        pixels,
        template,
        mode="valid",
        method="fft",
    )

    ones = np.ones(template.size, dtype=np.float64)
    local_sum = np.convolve(pixels, ones, mode="valid")
    local_sq_sum = np.convolve(pixels ** 2, ones, mode="valid")

    local_variance_sum = (
        local_sq_sum - (local_sum ** 2) / template.size
    )
    local_variance_sum = np.maximum(local_variance_sum, 0.0)

    denominator = np.sqrt(
        local_variance_sum * np.sum(template ** 2)
    )

    scores = np.zeros_like(raw_corr)
    valid = denominator > 1e-12
    scores[valid] = raw_corr[valid] / denominator[valid]

    peaks, properties = find_peaks(
        scores,
        height=threshold,
        distance=int(0.8 * PIXELS_PER_LINE),
    )

    peak_scores = properties.get(
        "peak_heights",
        np.array([], dtype=np.float64),
    )

    return peaks.astype(int), peak_scores.astype(float)


def reconstruct_channels(
    pixels: np.ndarray,
    sync_positions: np.ndarray,
    scores: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert sync positions into line starts and extract image A and B.

    In this line layout, channel-A sync begins at pixel 954.
    """
    image_a = []
    image_b = []
    accepted_scores = []

    for sync_position, score in zip(sync_positions, scores):
        line_start = int(sync_position) - SYNC_A_START
        line_end = line_start + PIXELS_PER_LINE

        if line_start < 0 or line_end > pixels.size:
            continue

        line = pixels[line_start:line_end]

        if line.size != PIXELS_PER_LINE:
            continue

        image_a.append(line[CHANNEL_A_START:CHANNEL_A_END])
        image_b.append(line[CHANNEL_B_START:CHANNEL_B_END])
        accepted_scores.append(float(score))

    if not image_a:
        raise RuntimeError(
            "No complete image lines found. Try a different recording, "
            "inspect the recovered envelope, and verify the sync template."
        )

    return (
        np.asarray(image_a, dtype=np.float64),
        np.asarray(image_b, dtype=np.float64),
        np.asarray(accepted_scores, dtype=np.float64),
    )


# ---------------------------------------------------------------------
# IMAGE AND QUALITY OUTPUTS
# ---------------------------------------------------------------------

def calculate_quality_metrics(
    pixels: np.ndarray,
    image_a: np.ndarray,
    image_b: np.ndarray,
    scores: np.ndarray,
    fs: int,
    metadata: dict,
) -> dict:
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "input": metadata,
        "apt": {
            "pixel_rate_hz": PIXEL_RATE,
            "line_rate_hz": LINE_RATE,
            "pixels_per_line": PIXELS_PER_LINE,
            "subcarrier_hz_nominal": SUBCARRIER_HZ,
        },
        "processing": {
            "processing_sample_rate_hz": fs,
            "recovered_pixel_count": int(pixels.size),
            "candidate_line_count": int(scores.size),
            "channel_a_shape": list(image_a.shape),
            "channel_b_shape": list(image_b.shape),
            "sync_score_mean": float(np.mean(scores)),
            "sync_score_min": float(np.min(scores)),
            "channel_a_pixel_std": float(np.std(image_a)),
            "channel_b_pixel_std": float(np.std(image_b)),
            "channel_a_clipping_fraction": float(
                np.mean((image_a <= 0.0) | (image_a >= 1.0))
            ),
            "channel_b_clipping_fraction": float(
                np.mean((image_b <= 0.0) | (image_b >= 1.0))
            ),
        },
        "limitations": [
            "Sync detection uses a simplified teaching template.",
            "Line count is not proof of a valid real satellite pass.",
            "Quality values depend on filtering and intensity scaling.",
            "Cross-validation against an independent decoder is recommended.",
        ],
    }


def save_decoded_outputs(
    pixels: np.ndarray,
    image_a: np.ndarray,
    image_b: np.ndarray,
    scores: np.ndarray,
    fs: int,
    metadata: dict,
    output_dir: Path,
) -> dict:
    ensure_dir(output_dir)

    save_grayscale(output_dir / "channel_a.png", image_a)
    save_grayscale(output_dir / "channel_b.png", image_b)

    combined = np.concatenate([image_a, image_b], axis=1)
    save_grayscale(output_dir / "channels_side_by_side.png", combined)

    np.save(output_dir / "recovered_pixels.npy", pixels)
    np.save(output_dir / "channel_a_raw.npy", image_a)
    np.save(output_dir / "channel_b_raw.npy", image_b)

    metrics = calculate_quality_metrics(
        pixels, image_a, image_b, scores, fs, metadata
    )

    json_write(output_dir / "quality_report.json", metrics)

    fig, axes = plt.subplots(2, 1, figsize=(12, 7))

    axes[0].plot(
        np.arange(min(10000, pixels.size)),
        pixels[:10000],
        linewidth=0.7,
    )
    axes[0].set_title("Recovered APT Video Envelope")
    axes[0].set_xlabel("Pixel sample index")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True)

    axes[1].plot(scores, marker="o", linewidth=0.7)
    axes[1].set_title("Accepted Channel-A Synchronization Scores")
    axes[1].set_xlabel("Accepted line index")
    axes[1].set_ylabel("Normalized correlation")
    axes[1].grid(True)

    fig.tight_layout()
    fig.savefig(output_dir / "decoder_diagnostics.png", dpi=160)
    plt.close(fig)

    return metrics


def decode_audio_signal(
    audio: np.ndarray,
    fs: int,
    metadata: dict,
    output_dir: Path,
) -> dict:
    pixels = recover_pixel_stream(audio, fs)

    sync_positions, sync_scores = detect_sync_positions(pixels)

    image_a, image_b, accepted_scores = reconstruct_channels(
        pixels,
        sync_positions,
        sync_scores,
    )

    metrics = save_decoded_outputs(
        pixels,
        image_a,
        image_b,
        accepted_scores,
        fs,
        metadata,
        output_dir,
    )

    print(f"Recovered pixels: {pixels.size}")
    print(f"Accepted image lines: {image_a.shape[0]}")
    print(f"Channel A image: {output_dir / 'channel_a.png'}")
    print(f"Channel B image: {output_dir / 'channel_b.png'}")
    print(f"Quality report: {output_dir / 'quality_report.json'}")

    return metrics


# ---------------------------------------------------------------------
# SYNTHETIC APT-LIKE TEST SIGNAL
# ---------------------------------------------------------------------

def synthetic_sync(
    frequency_hz: float,
    length: int = 39,
) -> np.ndarray:
    return make_sync_template(frequency_hz, length)


def generate_synthetic_video(
    number_of_lines: int,
    seed: int = 12345,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate a simplified APT-like pixel stream.

    The scene patterns are artificial. They are not real satellite images.
    """
    if number_of_lines < 3:
        raise ValueError("Generate at least three image lines.")

    rng = np.random.default_rng(seed)

    x = np.linspace(0.0, 2.0 * np.pi, 909, endpoint=False)
    image_a = np.zeros((number_of_lines, 909), dtype=np.float64)
    image_b = np.zeros((number_of_lines, 909), dtype=np.float64)

    for y in range(number_of_lines):
        noise_a = gaussian_filter1d(
            rng.normal(0.0, 1.0, 909), sigma=8
        )
        noise_b = gaussian_filter1d(
            rng.normal(0.0, 1.0, 909), sigma=10
        )

        image_a[y] = np.clip(
            0.50
            + 0.20 * np.sin(2.0 * x + y * 0.10)
            + 0.12 * np.sin(6.0 * x - y * 0.06)
            + 0.045 * noise_a,
            0.05,
            0.95,
        )

        image_b[y] = np.clip(
            0.48
            + 0.18 * np.cos(1.5 * x - y * 0.08)
            + 0.15 * np.sin(4.5 * x + y * 0.04)
            + 0.045 * noise_b,
            0.05,
            0.95,
        )

    sync_a = synthetic_sync(1040.0)
    sync_b = synthetic_sync(832.0)

    lines = []

    for row in range(number_of_lines):
        telemetry_a = np.where(
            (np.arange(45) // 5) % 2 == 0,
            0.80,
            0.20,
        ).astype(np.float64)

        telemetry_b = np.where(
            (np.arange(45) // 5) % 2 == 0,
            0.75,
            0.25,
        ).astype(np.float64)

        space_a = np.full(47, 0.05)
        space_b = np.full(47, 0.05)

        line = np.concatenate(
            [
                image_a[row],
                telemetry_a,
                sync_a,
                space_a,
                image_b[row],
                telemetry_b,
                sync_b,
                space_b,
            ]
        )

        if line.size != PIXELS_PER_LINE:
            raise RuntimeError(
                f"Incorrect generated line length: {line.size}"
            )

        lines.append(line)

    video = np.concatenate(lines)

    return video, image_a, image_b


def generate_synthetic_audio(
    number_of_lines: int,
    noise_std: float = 0.01,
    seed: int = 12345,
) -> tuple[np.ndarray, int, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate audio containing an AM subcarrier.

    The synthetic sample rate is three times the APT pixel rate, making
    it convenient to demonstrate envelope recovery and resampling.
    """
    if noise_std < 0:
        raise ValueError("Noise standard deviation cannot be negative.")

    video, image_a, image_b = generate_synthetic_video(
        number_of_lines,
        seed=seed,
    )

    fs = 3 * PIXEL_RATE
    envelope = np.repeat(video, 3)
    t = np.arange(envelope.size, dtype=np.float64) / fs

    carrier = np.cos(2.0 * np.pi * SUBCARRIER_HZ * t)
    audio = envelope * carrier

    rng = np.random.default_rng(seed + 1)
    audio += rng.normal(0.0, noise_std, audio.size)

    return audio, fs, video, image_a, image_b


def write_wav(path: Path, audio: np.ndarray, fs: int) -> None:
    ensure_dir(path.parent)

    audio = np.asarray(audio, dtype=np.float64)
    peak = float(np.max(np.abs(audio)))

    if peak > 1.0:
        audio = audio / peak

    pcm = np.round(np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    wavfile.write(path, fs, pcm)


def run_demo(output_dir: Path, number_of_lines: int, noise_std: float) -> None:
    ensure_dir(output_dir)

    audio, fs, video, reference_a, reference_b = generate_synthetic_audio(
        number_of_lines,
        noise_std=noise_std,
    )

    wav_path = output_dir / "synthetic_apt.wav"
    write_wav(wav_path, audio, fs)

    save_grayscale(
        output_dir / "synthetic_reference_a.png",
        reference_a,
    )
    save_grayscale(
        output_dir / "synthetic_reference_b.png",
        reference_b,
    )

    metadata = {
        "input_file": str(wav_path),
        "input_type": "synthetic_apt_like_audio",
        "sample_rate_hz": fs,
        "sample_count": int(audio.size),
        "duration_seconds": float(audio.size / fs),
        "noise_std": noise_std,
        "synthetic": True,
    }

    metrics = decode_audio_signal(audio, fs, metadata, output_dir / "decoded")

    print("\nSynthetic demo finished.")
    print(f"Audio: {wav_path}")
    print(f"Noise standard deviation: {noise_std}")
    print(f"Generated image lines: {number_of_lines}")
    print(f"Accepted lines: {metrics['processing']['candidate_line_count']}")
    print("This is synthetic data, not a real satellite reception.")


# ---------------------------------------------------------------------
# TIME AND FREQUENCY INSPECTION
# ---------------------------------------------------------------------

def inspect_signal(
    audio: np.ndarray,
    fs: int,
    output_path: Path,
) -> None:
    if audio.size < 32:
        raise ValueError("Recording is too short to inspect.")

    ensure_dir(output_path.parent)

    display_count = min(audio.size, int(0.1 * fs))
    frequencies, psd = welch(
        audio,
        fs=fs,
        nperseg=min(8192, audio.size),
    )

    try:
        pixels = recover_pixel_stream(audio, fs)
    except (ValueError, RuntimeError):
        pixels = np.array([], dtype=np.float64)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    time_axis = np.arange(display_count) / fs
    axes[0].plot(time_axis, audio[:display_count], linewidth=0.7)
    axes[0].set_title("Time-Domain Signal")
    axes[0].set_xlabel("Time (seconds)")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True)

    axes[1].plot(frequencies, 10 * np.log10(psd + 1e-15))
    axes[1].set_title("Welch Power Spectral Density")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Power (dB, relative)")
    axes[1].grid(True)

    if pixels.size:
        axes[2].plot(
            np.arange(min(pixels.size, 10000)),
            pixels[:10000],
            linewidth=0.7,
        )
    axes[2].set_title("Recovered Video Envelope")
    axes[2].set_xlabel("Pixel sample index")
    axes[2].set_ylabel("Amplitude")
    axes[2].grid(True)

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    print(f"Sample rate: {fs} Hz")
    print(f"Samples: {audio.size}")
    print(f"Duration: {audio.size / fs:.3f} seconds")
    print(f"Peak absolute amplitude: {np.max(np.abs(audio)):.5f}")
    print(f"Mean power: {np.mean(audio ** 2):.6g}")
    print(f"Inspection plot: {output_path}")


# ---------------------------------------------------------------------
# DOPPLER AND SATELLITE PASS PREDICTION
# ---------------------------------------------------------------------

def doppler_shift_hz(
    carrier_hz: float,
    radial_velocity_mps: float,
) -> float:
    """
    Positive radial velocity means receding from the observer.

    Non-relativistic approximation: f_D = -(v_r/c) * f_c.
    """
    speed_of_light = 299_792_458.0

    if carrier_hz <= 0:
        raise ValueError("Carrier frequency must be positive.")

    return -(radial_velocity_mps / speed_of_light) * carrier_hz


def predict_passes(
    tle_path: Path,
    latitude: float,
    longitude: float,
    hours: float,
    minimum_elevation: float,
) -> None:
    try:
        from skyfield.api import EarthSatellite, load, wgs84
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional dependency with: "
            "python -m pip install skyfield"
        ) from exc

    if not tle_path.exists():
        raise FileNotFoundError(f"TLE file not found: {tle_path}")

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be within [-90, 90].")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be within [-180, 180].")

    if hours <= 0:
        raise ValueError("Prediction window must be positive.")

    if not 0 <= minimum_elevation <= 90:
        raise ValueError("Minimum elevation must be within [0, 90].")

    lines = [
        line.strip()
        for line in tle_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if len(lines) >= 3 and lines[0].startswith("0 "):
        name, line1, line2 = lines[0][2:], lines[1], lines[2]
    elif len(lines) >= 3:
        name, line1, line2 = lines[0], lines[1], lines[2]
    elif len(lines) >= 2:
        name, line1, line2 = tle_path.stem, lines[0], lines[1]
    else:
        raise ValueError("TLE file must contain two orbital element lines.")

    ts = load.timescale()
    satellite = EarthSatellite(line1, line2, name, ts)
    observer = wgs84.latlon(latitude, longitude)

    start = ts.now()
    end = start + hours / 24.0

    times, events = satellite.find_events(
        observer,
        start,
        end,
        altitude_degrees=minimum_elevation,
    )

    labels = {
        0: "rise",
        1: "culmination",
        2: "set",
    }

    print(f"Satellite: {name}")
    print(f"Observer: latitude={latitude}, longitude={longitude}")
    print(f"Prediction window: {hours} hours")
    print(f"Minimum elevation: {minimum_elevation} degrees")

    for time, event in zip(times, events):
        topocentric = (satellite - observer).at(time)
        altitude, azimuth, _ = topocentric.altaz()

        print(
            f"{time.utc_iso()} | {labels.get(int(event), 'event')} | "
            f"elevation={altitude.degrees:.2f} deg | "
            f"azimuth={azimuth.degrees:.2f} deg"
        )

    if len(times) == 0:
        print("No events found in this prediction window.")


# ---------------------------------------------------------------------
# COMPARISON AND NOISE EXPERIMENT
# ---------------------------------------------------------------------

def compare_images(path_a: Path, path_b: Path) -> dict:
    if not path_a.exists() or not path_b.exists():
        raise FileNotFoundError("Both image paths must exist.")

    image_a = np.asarray(Image.open(path_a).convert("L"), dtype=np.float64)
    image_b = np.asarray(Image.open(path_b).convert("L"), dtype=np.float64)

    result = image_metrics(image_a, image_b)

    print(json.dumps(result, indent=2))
    return result


def run_noise_sweep(
    output_dir: Path,
    number_of_lines: int,
) -> None:
    """
    Add known noise to the same synthetic signal and report image metrics.

    The reference and decoded images are independently contrast-stretched.
    This is a robustness experiment, not a calibrated physical receiver SNR
    measurement. Synchronization may fail at high noise levels.
    """
    levels = [0.0, 0.01, 0.03, 0.06, 0.10]

    clean, fs, _, reference_a, _ = generate_synthetic_audio(
        number_of_lines,
        noise_std=0.0,
    )

    reference_u8 = normalize_u8(reference_a)
    rows = []

    for level in levels:
        rng = np.random.default_rng(20261024)
        noisy = clean + rng.normal(0.0, level, clean.size)

        try:
            pixels = recover_pixel_stream(noisy, fs)
            positions, scores = detect_sync_positions(pixels)
            image_a, _, accepted_scores = reconstruct_channels(
                pixels,
                positions,
                scores,
            )

            line_count = min(image_a.shape[0], reference_a.shape[0])
            test_u8 = normalize_u8(image_a[:line_count])
            ref_u8 = reference_u8[:line_count]

            # Compare only common line counts. This does not compensate
            # for line shifts or any nonlinear image distortion.
            result = image_metrics(ref_u8, test_u8)
            result["noise_std"] = level
            result["decoded_lines"] = int(image_a.shape[0])
            result["mean_sync_score"] = float(np.mean(accepted_scores))
            result["status"] = "decoded"

        except (ValueError, RuntimeError) as exc:
            result = {
                "noise_std": level,
                "status": "failed",
                "error": str(exc),
            }

        rows.append(result)
        print(json.dumps(result))

    json_write(
        output_dir / "noise_sweep.json",
        {"results": rows, "synthetic": True},
    )

    print(f"Noise sweep report: {output_dir / 'noise_sweep.json'}")


# ---------------------------------------------------------------------
# COMMAND-LINE INTERFACE
# ---------------------------------------------------------------------

def add_recording_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", type=Path, help="Input WAV or IQ file")
    parser.add_argument(
        "--iq",
        action="store_true",
        help="Input is raw complex64 IQ rather than demodulated WAV audio",
    )
    parser.add_argument(
        "--fs",
        type=int,
        default=None,
        help="Sample rate in samples/s; required for IQ",
    )
    parser.add_argument(
        "--deviation",
        type=float,
        default=25000.0,
        help="FM peak deviation in Hz for IQ demodulation",
    )
    parser.add_argument(
        "--offset-hz",
        type=float,
        default=0.0,
        help="Known IQ frequency offset to remove before FM demodulation",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline NOAA APT signal-processing lab"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Generate and decode synthetic APT-like audio")
    demo.add_argument("--out", type=Path, default=Path("output/demo"))
    demo.add_argument("--lines", type=int, default=80)
    demo.add_argument("--noise", type=float, default=0.01)

    inspect = sub.add_parser("inspect", help="Inspect an audio or IQ recording")
    add_recording_arguments(inspect)
    inspect.add_argument(
        "--out",
        type=Path,
        default=Path("output/inspection.png"),
    )

    decode = sub.add_parser("decode", help="Decode an audio or IQ recording")
    add_recording_arguments(decode)
    decode.add_argument(
        "--out",
        type=Path,
        default=Path("output/decoded"),
    )

    doppler = sub.add_parser("doppler", help="Calculate theoretical Doppler shift")
    doppler.add_argument("--carrier", type=float, default=137500000.0)
    doppler.add_argument(
        "--radial-velocity",
        type=float,
        required=True,
        help="Radial velocity in m/s; positive means receding",
    )

    predict = sub.add_parser("predict", help="Predict passes from a local TLE")
    predict.add_argument("--tle", type=Path, required=True)
    predict.add_argument("--lat", type=float, required=True)
    predict.add_argument("--lon", type=float, required=True)
    predict.add_argument("--hours", type=float, default=24.0)
    predict.add_argument("--min-elevation", type=float, default=10.0)

    compare = sub.add_parser("compare", help="Compare two grayscale images")
    compare.add_argument("reference", type=Path)
    compare.add_argument("test", type=Path)

    sweep = sub.add_parser("noise-sweep", help="Run a synthetic noise experiment")
    sweep.add_argument("--out", type=Path, default=Path("output/noise"))
    sweep.add_argument("--lines", type=int, default=80)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "demo":
            run_demo(args.out, args.lines, args.noise)

        elif args.command == "inspect":
            audio, fs, metadata = load_recording(
                args.input,
                args.iq,
                args.fs,
                args.deviation,
                args.offset_hz,
            )

            inspect_signal(audio, fs, args.out)
            json_write(
                args.out.with_suffix(".json"),
                metadata,
            )

        elif args.command == "decode":
            audio, fs, metadata = load_recording(
                args.input,
                args.iq,
                args.fs,
                args.deviation,
                args.offset_hz,
            )

            decode_audio_signal(audio, fs, metadata, args.out)

        elif args.command == "doppler":
            shift = doppler_shift_hz(
                args.carrier,
                args.radial_velocity,
            )

            print(f"Carrier frequency: {args.carrier:.3f} Hz")
            print(f"Radial velocity: {args.radial_velocity:.3f} m/s")
            print(f"Calculated Doppler shift: {shift:.3f} Hz")
            print(f"Shift magnitude: {abs(shift):.3f} Hz")

        elif args.command == "predict":
            predict_passes(
                args.tle,
                args.lat,
                args.lon,
                args.hours,
                args.min_elevation,
            )

        elif args.command == "compare":
            compare_images(args.reference, args.test)

        elif args.command == "noise-sweep":
            run_noise_sweep(args.out, args.lines)

    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()