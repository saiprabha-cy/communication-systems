
#!/usr/bin/env python3
"""
GNSS Signal Processing Learning Lab
===================================
Topics: GNSS-01 through GNSS-25

Educational GPS L1 C/A simulator and receiver experiments.

Included:
  - GPS L1 C/A PRN generation (PRNs 1-32)
  - Synthetic complex-baseband IQ generation
  - Doppler, code delay, navigation bits and complex noise
  - FFT-based parallel code-phase search (PCPS)
  - Peak-ratio acquisition diagnostic
  - Carrier wipeoff and early/prompt/late correlators
  - Synthetic navigation-bit recovery
  - Pseudorange position solution and DOP
  - IQ inspection, plots and JSON reports

Dependencies:
    python -m pip install numpy matplotlib

Examples:
    python gnss_signal_lab.py demo
    python gnss_signal_lab.py demo --prn 3 --doppler 2500 --delay 731 --noise 0.10
    python gnss_signal_lab.py acquire output/demo.c64 --fs 4092000 --prn 1
    python gnss_signal_lab.py inspect output/demo.c64 --fs 4092000
    python gnss_signal_lab.py position
    python gnss_signal_lab.py doppler --carrier 1575420000 --radial-velocity 1000

Limitations:
    This is a learning lab, not a certified GNSS receiver.
    Tracking diagnostics do not constitute a robust closed-loop DLL/PLL.
    Navigation decoding is a synthetic-bit demonstration, not complete LNAV
    word/subframe/parity decoding. For genuine recordings, use GNSS-SDR and
    validate against an independent receiver or trusted reference.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

C = 299_792_458.0
GPS_L1_HZ = 1_575_420_000.0
CA_CHIP_RATE = 1_023_000.0
CA_CODE_LENGTH = 1023
CA_PERIOD_S = 0.001
NAV_BIT_RATE = 50.0
EARTH_RADIUS_M = 6_378_137.0

# GPS C/A G2 phase-selection tap pairs for PRNs 1-32.
# Each tap is a register stage numbered 1 through 10.
G2_TAPS = {
    1: (2, 6),   2: (3, 7),   3: (4, 8),   4: (5, 9),
    5: (1, 9),   6: (2, 10),  7: (1, 8),   8: (2, 9),
    9: (3, 10), 10: (2, 3),  11: (3, 4),  12: (5, 6),
    13: (6, 7), 14: (7, 8),  15: (8, 9),  16: (9, 10),
    17: (1, 4), 18: (2, 5),  19: (3, 6),  20: (4, 7),
    21: (5, 8), 22: (6, 9),  23: (1, 3),  24: (4, 6),
    25: (5, 7), 26: (6, 8),  27: (7, 9),  28: (8, 10),
    29: (1, 6), 30: (2, 7),  31: (3, 8),  32: (4, 9),
}


def gps_ca_code(prn: int) -> np.ndarray:
    """Return 1023 GPS C/A chips mapped to {-1,+1}."""
    if prn not in G2_TAPS:
        raise ValueError("This lab supports GPS C/A PRNs 1 through 32.")

    # Registers are stored as stages 1..10. All stages start at one.
    g1 = np.ones(10, dtype=np.int8)
    g2 = np.ones(10, dtype=np.int8)
    tap_a, tap_b = G2_TAPS[prn]
    chips = np.empty(CA_CODE_LENGTH, dtype=np.int8)

    for i in range(CA_CODE_LENGTH):
        # Stage 10 is the current output.
        g1_out = int(g1[9])
        g2_out = int(g2[tap_a - 1] ^ g2[tap_b - 1])
        chips[i] = g1_out ^ g2_out

        # G1: x^10 + x^3 + 1
        g1_feedback = int(g1[2] ^ g1[9])
        # G2: x^10 + x^9 + x^8 + x^6 + x^3 + x^2 + 1
        g2_feedback = int(g2[1] ^ g2[2] ^ g2[5] ^
                          g2[7] ^ g2[8] ^ g2[9])

        g1[1:] = g1[:-1]
        g2[1:] = g2[:-1]
        g1[0] = g1_feedback
        g2[0] = g2_feedback

    # Bipolar mapping: binary 0 -> +1, binary 1 -> -1.
    return (1 - 2 * chips).astype(np.float64)


def samples_per_chip(fs: float) -> int:
    ratio = fs / CA_CHIP_RATE
    rounded = int(round(ratio))
    if rounded < 1 or not np.isclose(ratio, rounded, rtol=0, atol=1e-8):
        raise ValueError(
            "For this simple lab, fs must be an integer multiple of "
            "1.023 MHz. Try fs=4092000 (4 samples/chip)."
        )
    return rounded


def sampled_ca_code(prn: int, fs: float) -> np.ndarray:
    """Generate one millisecond of sampled C/A code."""
    spc = samples_per_chip(fs)
    return np.repeat(gps_ca_code(prn), spc).astype(np.float64)


def complex_awgn(rng: np.random.Generator, n: int,
                 sigma: float) -> np.ndarray:
    """Complex Gaussian noise; E[|w|^2] = sigma^2."""
    return (rng.normal(size=n) + 1j * rng.normal(size=n)) * (
        sigma / np.sqrt(2.0)
    )


def generate_iq(
    prn: int = 1,
    fs: float = 4_092_000.0,
    duration_s: float = 0.040,
    doppler_hz: float = 2_500.0,
    code_delay_samples: int = 731,
    noise_sigma: float = 0.10,
    amplitude: float = 1.0,
    nav_seed: int = 1234,
    carrier_phase_rad: float = 0.4,
    seed: int = 42,
) -> tuple[np.ndarray, dict]:
    """
    Generate synthetic complex baseband GPS L1 C/A-like samples.

    The code delay is a circular sample delay within the repeated C/A code.
    A real receiver observes propagation delay, front-end filtering, clock
    offsets and other effects that are not all modelled here.
    """
    spc = samples_per_chip(fs)
    code_1ms = sampled_ca_code(prn, fs)
    n_per_ms = len(code_1ms)
    n_total = int(round(duration_s * fs))

    if n_total < n_per_ms:
        raise ValueError("duration_s must be at least 1 ms.")

    rng = np.random.default_rng(seed)
    nav_rng = np.random.default_rng(nav_seed)
    nav_bits = nav_rng.choice(np.array([-1.0, 1.0]), size=100)

    n = np.arange(n_total)
    code_index = (n - int(code_delay_samples)) % n_per_ms
    code = code_1ms[code_index]

    # 50 bps: one navigation bit lasts 20 ms.
    bit_samples = int(round(fs / NAV_BIT_RATE))
    bit_index = (n // bit_samples) % len(nav_bits)
    data = nav_bits[bit_index]

    carrier = np.exp(
        1j * (2.0 * np.pi * doppler_hz * n / fs + carrier_phase_rad)
    )
    clean = amplitude * data * code * carrier
    noisy = clean + complex_awgn(rng, n_total, noise_sigma)

    metadata = {
        "prn": int(prn),
        "sample_rate_hz": float(fs),
        "duration_s": float(n_total / fs),
        "samples": int(n_total),
        "samples_per_chip": int(spc),
        "samples_per_code_period": int(n_per_ms),
        "true_doppler_hz": float(doppler_hz),
        "true_code_delay_samples": int(code_delay_samples % n_per_ms),
        "noise_sigma": float(noise_sigma),
        "amplitude": float(amplitude),
        "true_carrier_phase_rad": float(carrier_phase_rad),
        "nav_bits_seed": int(nav_seed),
        "signal_model": "synthetic complex-baseband GPS L1 C/A-like signal",
    }
    return noisy.astype(np.complex64), metadata


def load_iq(path: str | Path, dtype: str = "complex64") -> np.ndarray:
    """Load raw IQ samples; raw files normally contain no metadata."""
    allowed = {
        "complex64": np.complex64,
        "complex128": np.complex128,
    }
    if dtype not in allowed:
        raise ValueError("dtype must be complex64 or complex128.")
    x = np.fromfile(path, dtype=allowed[dtype])
    if x.size == 0:
        raise ValueError(f"No samples read from {path}")
    return x


def save_json(path: str | Path, obj: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def pcps_acquire(
    x: np.ndarray,
    prn: int,
    fs: float,
    doppler_min: float = -10_000.0,
    doppler_max: float = 10_000.0,
    doppler_step: float = 500.0,
) -> dict:
    """
    Parallel code-phase search on one code period.

    For each Doppler hypothesis:
        wiped = x * exp(-j*2*pi*f*n/fs)
        corr = IFFT(FFT(wiped) * conj(FFT(local_code)))

    The peak's code-phase convention is checked against the injected delay
    in the synthetic demo; real data should also be validated independently.
    """
    code = sampled_ca_code(prn, fs)
    n_code = len(code)
    if len(x) < n_code:
        raise ValueError("At least one millisecond of IQ is required.")

    # One C/A period keeps the acquisition example easy to inspect.
    x1 = np.asarray(x[:n_code], dtype=np.complex128)
    code_fft = np.fft.fft(code)
    n = np.arange(n_code)
    dopplers = np.arange(
        doppler_min, doppler_max + 0.5 * doppler_step, doppler_step
    )
    best = {
        "peak_power": -np.inf,
        "doppler_hz": None,
        "code_phase_samples": None,
        "correlation_power": None,
    }

    for fd in dopplers:
        wiped = x1 * np.exp(-1j * 2.0 * np.pi * fd * n / fs)
        corr = np.fft.ifft(np.fft.fft(wiped) * np.conj(code_fft))
        power = np.abs(corr) ** 2
        idx = int(np.argmax(power))
        peak = float(power[idx])
        if peak > best["peak_power"]:
            best.update({
                "peak_power": peak,
                "doppler_hz": float(fd),
                "code_phase_samples": idx,
                "correlation_power": power,
            })

    power = best.pop("correlation_power")
    peak_idx = int(best["code_phase_samples"])
    # Exclude a small neighborhood around the primary peak when estimating
    # a second peak; this is a heuristic, not a formal false-alarm detector.
    masked = power.copy()
    guard = max(1, int(round(fs / CA_CHIP_RATE)))
    for offset in range(-guard, guard + 1):
        masked[(peak_idx + offset) % n_code] = 0.0
    second_peak = float(np.max(masked))
    peak_power = float(best["peak_power"])
    best["second_peak_power"] = second_peak
    best["peak_to_second_peak_ratio"] = (
        peak_power / max(second_peak, np.finfo(float).tiny)
    )
    best["doppler_grid_hz"] = [
        float(doppler_min), float(doppler_max), float(doppler_step)
    ]
    best["interpretation"] = (
        "Peak-ratio diagnostic only; not a calibrated P_FA detector."
    )
    return best


def track_correlators(
    x: np.ndarray,
    prn: int,
    fs: float,
    code_phase_samples: int,
    doppler_hz: float,
    milliseconds: int = 10,
) -> dict:
    """
    Measure prompt, early and late correlators after acquisition.

    This is an open-loop tracking diagnostic, not a full closed-loop DLL/PLL.
    Early/late offsets are one sample in this simple implementation.
    """
    code = sampled_ca_code(prn, fs)
    n_code = len(code)
    n_ms = min(milliseconds, len(x) // n_code)
    if n_ms < 1:
        raise ValueError("Not enough samples for one tracking interval.")

    prompt_mag = []
    early_mag = []
    late_mag = []
    pll_phase_error = []
    dll_error = []
    prompt_complex = []

    for m in range(n_ms):
        seg = np.asarray(
            x[m * n_code:(m + 1) * n_code], dtype=np.complex128
        )
        n = np.arange(n_code)
        wiped = seg * np.exp(-1j * 2.0 * np.pi * doppler_hz * n / fs)

        prompt_code = np.roll(code, int(code_phase_samples))
        early_code = np.roll(code, int(code_phase_samples) - 1)
        late_code = np.roll(code, int(code_phase_samples) + 1)

        p = np.vdot(prompt_code, wiped)
        e = np.vdot(early_code, wiped)
        l = np.vdot(late_code, wiped)

        prompt_complex.append([float(p.real), float(p.imag)])
        prompt_mag.append(float(abs(p)))
        early_mag.append(float(abs(e)))
        late_mag.append(float(abs(l)))
        pll_phase_error.append(float(np.angle(p)))
        dll_error.append(float(
            (abs(e) - abs(l)) / (abs(e) + abs(l) + 1e-12)
        ))

    return {
        "interval_ms": 1,
        "number_of_intervals": n_ms,
        "code_phase_samples_used": int(code_phase_samples),
        "doppler_hz_used": float(doppler_hz),
        "prompt_magnitude": prompt_mag,
        "early_magnitude": early_mag,
        "late_magnitude": late_mag,
        "pll_phase_error_rad": pll_phase_error,
        "dll_early_late_discriminator": dll_error,
        "prompt_complex": prompt_complex,
        "mean_prompt_magnitude": float(np.mean(prompt_mag)),
        "mean_abs_dll_discriminator": float(np.mean(np.abs(dll_error))),
        "mean_abs_pll_phase_error_rad": float(
            np.mean(np.abs(pll_phase_error))
        ),
        "warning": (
            "Open-loop correlator diagnostics only. No loop filter or "
            "closed-loop code/carrier updates are implemented."
        ),
    }


def recover_synthetic_nav_bits(
    x: np.ndarray,
    prn: int,
    fs: float,
    code_phase_samples: int,
    doppler_hz: float,
    bit_count: int = 5,
) -> dict:
    """
    Demonstrate 20 ms prompt integration and hard decisions.

    This is a synthetic bit recovery exercise, not LNAV framing/parity decode.
    """
    code = sampled_ca_code(prn, fs)
    n_code = len(code)
    samples_per_bit = int(round(fs / NAV_BIT_RATE))
    bits = []
    soft_values = []

    for k in range(bit_count):
        start = k * samples_per_bit
        stop = start + samples_per_bit
        if stop > len(x):
            break
        acc = 0j
        # Coherently sum 20 one-millisecond prompt correlations.
        for start_ms in range(start // n_code, stop // n_code):
            a = start_ms * n_code
            b = a + n_code
            if b > len(x):
                break
            seg = np.asarray(x[a:b], dtype=np.complex128)
            n = np.arange(n_code)
            wiped = seg * np.exp(-1j * 2 * np.pi * doppler_hz * n / fs)
            local = np.roll(code, int(code_phase_samples))
            acc += np.vdot(local, wiped)
        soft = float(acc.real)
        soft_values.append(soft)
        bits.append(1 if soft >= 0 else -1)

    return {
        "estimated_bits_pm1": bits,
        "soft_decision_values": soft_values,
        "bit_rate_bps": NAV_BIT_RATE,
        "bit_duration_ms": 20,
        "note": (
            "Assumes the code phase, Doppler, bit boundary and useful carrier "
            "phase are already known. Not a complete GPS LNAV decoder."
        ),
    }


def doppler_from_radial_velocity(
    carrier_hz: float, radial_velocity_mps: float
) -> float:
    """Positive radial velocity means increasing range (receding)."""
    return -(radial_velocity_mps / C) * carrier_hz


def generate_positioning_case(
    satellite_count: int = 8,
    seed: int = 9,
    pseudorange_noise_m: float = 2.0,
) -> dict:
    """
    Generate a geometry-only positioning test in ECEF coordinates.

    Satellite positions are synthetic points on a shell; they are NOT
    propagated GPS ephemerides. This tests least-squares mathematics only.
    """
    if satellite_count < 4:
        raise ValueError("At least four satellites are required.")

    rng = np.random.default_rng(seed)
    truth = np.array([EARTH_RADIUS_M, 0.0, 0.0, 75_000.0])
    sat_radius = EARTH_RADIUS_M + 20_200_000.0

    satellites = []
    for _ in range(satellite_count):
        v = rng.normal(size=3)
        v /= np.linalg.norm(v)
        satellites.append(sat_radius * v)
    satellites = np.asarray(satellites)

    ranges = np.linalg.norm(satellites - truth[:3], axis=1)
    measurements = (
        ranges + truth[3] +
        rng.normal(0.0, pseudorange_noise_m, size=satellite_count)
    )

    return {
        "true_state_xyz_clock_m": truth.tolist(),
        "satellite_positions_ecef_m": satellites.tolist(),
        "pseudoranges_m": measurements.tolist(),
        "pseudorange_noise_sigma_m": float(pseudorange_noise_m),
        "note": (
            "Synthetic satellite geometry, not real ephemeris or real GNSS "
            "observations."
        ),
    }


def solve_position(
    satellite_positions: np.ndarray,
    pseudoranges: np.ndarray,
    max_iterations: int = 20,
) -> dict:
    """Iterative unweighted least-squares ECEF position and clock-bias solve."""
    sat = np.asarray(satellite_positions, dtype=float)
    obs = np.asarray(pseudoranges, dtype=float)
    if sat.ndim != 2 or sat.shape[1] != 3 or len(obs) != len(sat):
        raise ValueError("Expected satellite_positions shape (N,3) and N ranges.")
    if len(obs) < 4:
        raise ValueError("At least four pseudoranges are required.")

    # State: ECEF x,y,z and receiver clock bias expressed in metres.
    state = np.array([EARTH_RADIUS_M, 0.0, 0.0, 0.0], dtype=float)

    for iteration in range(max_iterations):
        delta = state[:3][None, :] - sat
        geometric_ranges = np.linalg.norm(delta, axis=1)
        if np.any(geometric_ranges <= 0):
            raise ValueError("Invalid satellite/receiver geometry.")

        predicted = geometric_ranges + state[3]
        residual = obs - predicted

        # Linearized range derivative with respect to x,y,z and clock bias.
        H = np.column_stack((
            delta / geometric_ranges[:, None],
            np.ones(len(obs))
        ))
        update, *_ = np.linalg.lstsq(H, residual, rcond=None)
        state += update
        if np.linalg.norm(update) < 1e-4:
            break

    delta = state[:3][None, :] - sat
    geometric_ranges = np.linalg.norm(delta, axis=1)
    residual = obs - (geometric_ranges + state[3])
    H = np.column_stack((
        delta / geometric_ranges[:, None],
        np.ones(len(obs))
    ))
    Q = np.linalg.pinv(H.T @ H)

    # In this state vector, the fourth component is clock bias in metres.
    q_xyz = Q[:3, :3]
    pdop = float(np.sqrt(max(0.0, np.trace(q_xyz))))
    hdop = float(np.sqrt(max(0.0, Q[0, 0] + Q[1, 1])))
    vdop = float(np.sqrt(max(0.0, Q[2, 2])))
    gdop = float(np.sqrt(max(0.0, np.trace(Q))))

    return {
        "estimated_xyz_ecef_m": state[:3].tolist(),
        "estimated_receiver_clock_bias_m": float(state[3]),
        "estimated_receiver_clock_bias_s": float(state[3] / C),
        "residuals_m": residual.tolist(),
        "residual_rms_m": float(np.sqrt(np.mean(residual ** 2))),
        "iterations": int(iteration + 1),
        "PDOP": pdop,
        "HDOP": hdop,
        "VDOP": vdop,
        "GDOP": gdop,
        "warning": (
            "Geometry-only synthetic solution. DOP is dimensionless; this "
            "does not model real satellite ephemeris or atmospheric errors."
        ),
    }


def make_plots(
    x: np.ndarray,
    fs: float,
    acq: dict | None,
    tracking: dict | None,
    out_dir: Path,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    n_show = min(len(x), int(round(0.002 * fs)))
    t_ms = np.arange(n_show) / fs * 1000.0

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(t_ms, np.real(x[:n_show]), linewidth=0.7, label="I")
    ax.plot(t_ms, np.imag(x[:n_show]), linewidth=0.7, label="Q")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Complex-baseband IQ samples")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "iq_samples.png", dpi=150)
    plt.close(fig)

    if tracking:
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.plot(tracking["prompt_magnitude"], label="Prompt")
        ax.plot(tracking["early_magnitude"], label="Early")
        ax.plot(tracking["late_magnitude"], label="Late")
        ax.set_xlabel("1 ms interval index")
        ax.set_ylabel("Correlation magnitude")
        ax.set_title("Open-loop early/prompt/late correlator measurements")
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / "tracking_correlators.png", dpi=150)
        plt.close(fig)

    if acq:
        # Re-run a small display-only correlation at the winning Doppler.
        code = sampled_ca_code(int(acq["prn"]), fs)
        n_code = len(code)
        seg = np.asarray(x[:n_code], dtype=np.complex128)
        n = np.arange(n_code)
        wiped = seg * np.exp(
            -1j * 2.0 * np.pi * acq["doppler_hz"] * n / fs
        )
        corr = np.fft.ifft(np.fft.fft(wiped) * np.conj(np.fft.fft(code)))
        power = np.abs(corr) ** 2
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.plot(np.arange(n_code), power, linewidth=0.7)
        ax.axvline(acq["code_phase_samples"], linestyle="--",
                   label="Detected peak")
        ax.set_xlabel("Code phase (samples)")
        ax.set_ylabel("Correlation power")
        ax.set_title("PCPS correlation versus code phase")
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / "acquisition_correlation.png", dpi=150)
        plt.close(fig)


def run_demo(args) -> None:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    x, truth = generate_iq(
        prn=args.prn,
        fs=args.fs,
        duration_s=args.duration,
        doppler_hz=args.doppler,
        code_delay_samples=args.delay,
        noise_sigma=args.noise,
        seed=args.seed,
    )
    iq_path = out / "demo.c64"
    x.tofile(iq_path)
    save_json(out / "synthetic_truth.json", truth)

    acq = pcps_acquire(
        x, args.prn, args.fs,
        doppler_min=args.doppler_search_min,
        doppler_max=args.doppler_search_max,
        doppler_step=args.doppler_step,
    )
    acq["prn"] = int(args.prn)
    acq["sample_rate_hz"] = float(args.fs)
    acq["true_doppler_hz"] = float(args.doppler)
    acq["true_code_delay_samples"] = int(args.delay)
    save_json(out / "acquisition.json", acq)

    tracking = track_correlators(
        x, args.prn, args.fs,
        acq["code_phase_samples"], acq["doppler_hz"],
        milliseconds=args.track_ms,
    )
    save_json(out / "tracking.json", tracking)

    nav = recover_synthetic_nav_bits(
        x, args.prn, args.fs,
        acq["code_phase_samples"], acq["doppler_hz"],
        bit_count=args.nav_bits,
    )
    save_json(out / "nav_bit_demo.json", nav)

    make_plots(x, args.fs, acq, tracking, out)

    summary = {
        "synthetic_truth": truth,
        "acquisition": {
            k: v for k, v in acq.items()
            if k not in ("correlation_power",)
        },
        "tracking": {
            "mean_prompt_magnitude": tracking["mean_prompt_magnitude"],
            "mean_abs_dll_discriminator":
                tracking["mean_abs_dll_discriminator"],
            "mean_abs_pll_phase_error_rad":
                tracking["mean_abs_pll_phase_error_rad"],
        },
        "navigation_bit_demo": nav,
        "files": [
            "demo.c64", "synthetic_truth.json", "acquisition.json",
            "tracking.json", "nav_bit_demo.json", "iq_samples.png",
            "acquisition_correlation.png", "tracking_correlators.png"
        ],
        "limitations": [
            "Synthetic signal only; no real satellite was received.",
            "Peak-ratio diagnostic is not a formal false-alarm probability.",
            "Tracking is open-loop diagnostic, not a full closed-loop receiver.",
            "Navigation demonstration is not full GPS LNAV parity decoding."
        ],
    }
    save_json(out / "summary.json", summary)

    print("\nGNSS SYNTHETIC DEMO")
    print("===================")
    print(f"Output directory: {out.resolve()}")
    print(f"PRN: {args.prn}")
    print(f"True Doppler: {args.doppler:.1f} Hz")
    print(f"Estimated Doppler: {acq['doppler_hz']:.1f} Hz")
    print(f"True code delay: {args.delay % len(sampled_ca_code(args.prn,args.fs))}")
    print(f"Estimated code phase: {acq['code_phase_samples']} samples")
    print(f"Peak/second-peak ratio: {acq['peak_to_second_peak_ratio']:.3f}")
    print(f"Mean prompt magnitude: {tracking['mean_prompt_magnitude']:.3f}")
    print(f"Demo bits (+1/-1): {nav['estimated_bits_pm1']}")
    print("\nInspect summary.json and the generated plots.")
    print("These results validate only the synthetic test case.")


def run_acquire(args) -> None:
    x = load_iq(args.file, args.dtype)
    acq = pcps_acquire(
        x, args.prn, args.fs,
        doppler_min=args.doppler_min,
        doppler_max=args.doppler_max,
        doppler_step=args.doppler_step,
    )
    acq["prn"] = args.prn
    acq["sample_rate_hz"] = args.fs
    if args.out:
        save_json(args.out, {
            k: v for k, v in acq.items() if k != "correlation_power"
        })
    print(json.dumps(
        {k: v for k, v in acq.items() if k != "correlation_power"},
        indent=2
    ))


def run_inspect(args) -> None:
    x = load_iq(args.file, args.dtype)
    out = Path(args.out)
    make_plots(x, args.fs, None, None, out)
    power = np.abs(x) ** 2
    report = {
        "file": str(args.file),
        "samples": int(len(x)),
        "sample_rate_hz": float(args.fs),
        "duration_s": float(len(x) / args.fs),
        "mean_I": float(np.mean(x.real)),
        "mean_Q": float(np.mean(x.imag)),
        "mean_power": float(np.mean(power)),
        "rms_amplitude": float(np.sqrt(np.mean(power))),
        "peak_amplitude": float(np.max(np.abs(x))),
        "dtype_loaded": args.dtype,
        "warning": (
            "Raw IQ metadata such as RF center frequency, quantization, "
            "front-end gain and frequency offset must be supplied separately."
        ),
    }
    save_json(out / "iq_inspection.json", report)
    print(json.dumps(report, indent=2))
    print(f"Plots saved to {out.resolve()}")


def run_position(args) -> None:
    case = generate_positioning_case(
        satellite_count=args.satellites,
        seed=args.seed,
        pseudorange_noise_m=args.noise_m,
    )
    result = solve_position(
        np.asarray(case["satellite_positions_ecef_m"]),
        np.asarray(case["pseudoranges_m"]),
    )
    truth = np.asarray(case["true_state_xyz_clock_m"])
    est = np.asarray(result["estimated_xyz_ecef_m"])
    position_error = float(np.linalg.norm(est - truth[:3]))
    result["true_xyz_ecef_m"] = truth[:3].tolist()
    result["true_clock_bias_m"] = float(truth[3])
    result["position_error_m"] = position_error
    result["synthetic_case"] = case

    if args.out:
        save_json(args.out, result)
    print(json.dumps(result, indent=2))
    print("\nThis is a geometry-only pseudorange simulation, not a real GPS fix.")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Software-only GPS L1 C/A signal processing lab"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Generate, acquire and inspect synthetic IQ")
    demo.add_argument("--out", default="output/gnss_demo")
    demo.add_argument("--prn", type=int, default=1)
    demo.add_argument("--fs", type=float, default=4_092_000.0)
    demo.add_argument("--duration", type=float, default=0.080)
    demo.add_argument("--doppler", type=float, default=2_500.0)
    demo.add_argument("--delay", type=int, default=731)
    demo.add_argument("--noise", type=float, default=0.10)
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--doppler-search-min", type=float, default=-10_000.0)
    demo.add_argument("--doppler-search-max", type=float, default=10_000.0)
    demo.add_argument("--doppler-step", type=float, default=500.0)
    demo.add_argument("--track-ms", type=int, default=10)
    demo.add_argument("--nav-bits", type=int, default=3)
    demo.set_defaults(func=run_demo)

    acquire = sub.add_parser("acquire", help="Run PCPS on raw complex IQ")
    acquire.add_argument("file")
    acquire.add_argument("--fs", type=float, required=True)
    acquire.add_argument("--prn", type=int, default=1)
    acquire.add_argument("--dtype", choices=["complex64", "complex128"],
                         default="complex64")
    acquire.add_argument("--doppler-min", type=float, default=-10_000.0)
    acquire.add_argument("--doppler-max", type=float, default=10_000.0)
    acquire.add_argument("--doppler-step", type=float, default=500.0)
    acquire.add_argument("--out", default="output/acquisition.json")
    acquire.set_defaults(func=run_acquire)

    inspect = sub.add_parser("inspect", help="Inspect raw complex IQ samples")
    inspect.add_argument("file")
    inspect.add_argument("--fs", type=float, required=True)
    inspect.add_argument("--dtype", choices=["complex64", "complex128"],
                         default="complex64")
    inspect.add_argument("--out", default="output/iq_inspection")
    inspect.set_defaults(func=run_inspect)

    position = sub.add_parser(
        "position", help="Test least-squares positioning on synthetic ranges"
    )
    position.add_argument("--satellites", type=int, default=8)
    position.add_argument("--seed", type=int, default=9)
    position.add_argument("--noise-m", type=float, default=2.0)
    position.add_argument("--out", default="output/position_solution.json")
    position.set_defaults(func=run_position)

    doppler = sub.add_parser("doppler", help="Calculate first-order Doppler shift")
    doppler.add_argument("--carrier", type=float, default=GPS_L1_HZ)
    doppler.add_argument("--radial-velocity", type=float, default=1000.0)
    doppler.set_defaults(func=lambda a: print(json.dumps({
        "carrier_hz": a.carrier,
        "radial_velocity_mps_receding_positive": a.radial_velocity,
        "doppler_hz": doppler_from_radial_velocity(
            a.carrier, a.radial_velocity
        ),
        "convention": "Positive radial velocity means increasing range.",
    }, indent=2)))

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
