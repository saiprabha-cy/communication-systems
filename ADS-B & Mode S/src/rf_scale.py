SPEED_OF_LIGHT_M_S = 299_792_458.0


def wavelength_m(frequency_hz: float) -> float:
    if frequency_hz <= 0:
        raise ValueError("Frequency must be positive.")
    return SPEED_OF_LIGHT_M_S / frequency_hz


def main() -> None:
    frequency_hz = 1_090_000_000.0
    wavelength = wavelength_m(frequency_hz)

    print(f"Frequency:       {frequency_hz / 1e6:.3f} MHz")
    print(f"Wavelength:       {wavelength:.4f} m")
    print(f"Quarter-wave:     {wavelength / 4:.4f} m")
    print(f"Half-wave:        {wavelength / 2:.4f} m")

    assert 0.27 < wavelength < 0.28
    assert 0.067 < wavelength / 4 < 0.071

    print("\nPASS: RF scale calculations are plausible.")


if __name__ == "__main__":
    main()