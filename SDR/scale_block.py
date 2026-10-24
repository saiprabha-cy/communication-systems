
import numpy as np
from gnuradio import gr


class ScaleComplex(gr.sync_block):
    """Scale complex input samples by a constant gain."""

    def __init__(self, gain=0.5):
        gr.sync_block.__init__(
            self,
            name="Scale Complex",
            in_sig=[np.complex64],
            out_sig=[np.complex64],
        )
        self.gain = float(gain)

    def work(self, input_items, output_items):
        x = input_items[0]
        y = output_items[0]

        y[:] = self.gain * x
        return len(y)
