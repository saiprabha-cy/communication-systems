
import tempfile
import unittest
from pathlib import Path

import numpy as np

from sdr_pipeline import (
    FS_IN,
    generate_recording,
    read_iq,
    translate_channel,
    filter_and_decimate,
)


class TestSDRPipeline(unittest.TestCase):

    def test_recording_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Generate in the project data directory using the normal
            # pipeline, then validate the actual raw file format.
            path = generate_recording()
            iq = read_iq(path)

            self.assertEqual(iq.dtype, np.complex64)
            self.assertEqual(len(iq), FS_IN)
            self.assertTrue(np.all(np.isfinite(iq)))

    def test_frequency_translation(self):
        fs = 200_000
        n = 20_000
        t = np.arange(n) / fs
        x = np.exp(1j * 2 * np.pi * 20_000 * t)

        y = translate_channel(x, fs, 20_000)

        self.assertAlmostEqual(
            float(np.mean(np.abs(y))),
            1.0,
            places=5
        )
        self.assertLess(
            float(np.std(y)),
            1e-5
        )

    def test_decimation_rate(self):
        fs = 200_000
        t = np.arange(20_000) / fs
        x = np.exp(1j * 2 * np.pi * 20_000 * t)

        baseband = translate_channel(x, fs, 20_000)
        y, fs_out, _ = filter_and_decimate(baseband, fs)

        self.assertEqual(fs_out, 100_000)
        self.assertEqual(len(y), len(x) // 2)
        self.assertTrue(np.all(np.isfinite(y)))


if __name__ == "__main__":
    unittest.main()
