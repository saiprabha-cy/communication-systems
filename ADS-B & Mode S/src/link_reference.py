from dataclasses import dataclass


@dataclass(frozen=True)
class AviationLink:
    name: str
    frequency_mhz: float
    modulation: str
    frame_family: str
    decoder_family: str


LINKS = {
    "1090ES": AviationLink(
        name="1090 MHz Extended Squitter",
        frequency_mhz=1090.0,
        modulation="Pulse-position modulation (PPM)",
        frame_family="Mode S, including DF17",
        decoder_family="Mode S / ADS-B decoder",
    ),
    "UAT": AviationLink(
        name="978 MHz Universal Access Transceiver",
        frequency_mhz=978.0,
        modulation="UAT-specific modulation and framing",
        frame_family="UAT",
        decoder_family="UAT-capable decoder",
    ),
}


def print_link(link: AviationLink) -> None:
    print(f"Name:             {link.name}")
    print(f"Frequency:        {link.frequency_mhz:.1f} MHz")
    print(f"Modulation:       {link.modulation}")
    print(f"Frame family:     {link.frame_family}")
    print(f"Decoder family:   {link.decoder_family}")


def main() -> None:
    for key, link in LINKS.items():
        print(f"\n--- {key} ---")
        print_link(link)

    assert LINKS["1090ES"].frequency_mhz == 1090.0
    assert LINKS["UAT"].frequency_mhz == 978.0
    assert LINKS["1090ES"].frame_family != LINKS["UAT"].frame_family

    print("\nPASS: links are represented separately.")


if __name__ == "__main__":
    main()