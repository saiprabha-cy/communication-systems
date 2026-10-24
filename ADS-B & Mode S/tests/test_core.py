import unittest

from src.frame_structure import inspect_frame
from src.icao_address import extract_icao_df17
from src.cpr import cpr_nl


REFERENCE_DF17 = "8D40621D58C382D690C8AC2863A7"


class TestModeSCore(unittest.TestCase):
    def test_reference_frame_length(self):
        info = inspect_frame(REFERENCE_DF17)
        self.assertEqual(info.downlink_format, 17)
        self.assertEqual(info.length_bits, 112)

    def test_icao_extraction(self):
        address = extract_icao_df17(REFERENCE_DF17)
        self.assertEqual(address, "40621D")

    def test_wrong_frame_length_is_rejected(self):
        with self.assertRaises(ValueError):
            inspect_frame("8D4062")

    def test_invalid_hex_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_icao_df17("8D40621D58C382D690C8AC286Z")

    def test_cpr_nl_equator(self):
        self.assertEqual(cpr_nl(0.0), 59)

    def test_cpr_nl_high_latitude(self):
        self.assertEqual(cpr_nl(89.0), 1)


if __name__ == "__main__":
    unittest.main()