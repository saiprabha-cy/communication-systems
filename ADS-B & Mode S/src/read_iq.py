from pathlib import Path

import numpy as np

IQ_PATH = Path("data/iq/synthetic_df17.c64")


def main() -> None:
    if not IQ_PATH.exists():
        raise FileNotFoundError(
            f"{IQ_PATH} not found. Run src/signal_generator.py first."
        )

    iq = np.fromfile(IQ_PATH, dtype=np.complex64)

    if iq.size == 0:
        raise ValueError("IQ file is empty.")

    print(f"Samples:      {iq.size:,}")
    print(f"Dtype:        {iq.dtype}")
    print(f"File bytes:   {IQ_PATH.stat().st_size:,}")
    print(f"Peak |IQ|:    {np.max(np.abs(iq)):.3f}")
    print(f"Mean power:   {np.mean(np.abs(iq) ** 2):.6f}")

    assert IQ_PATH.stat().st_size == iq.size * 8
    assert np.isfinite(iq.real).all()
    assert np.isfinite(iq.imag).all()

    print("PASS: IQ file read and basic integrity checks succeeded.")


if __name__ == "__main__":
    main()