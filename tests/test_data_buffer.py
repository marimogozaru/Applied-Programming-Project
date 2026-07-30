import unittest

import numpy as np

from service.data_buffer import EmgDataBuffer


class EmgDataBufferTests(unittest.TestCase):
    def test_total_time_tracks_current_buffer_after_trim(self) -> None:
        buffer = EmgDataBuffer(
            n_channels=1,
            samples_per_packet=1,
            sampling_rate=1000.0,
            buffer_seconds=0.001,
        )

        raw = np.zeros((1, 1), dtype=np.float64).tobytes()
        buffer.add_bytes(raw)
        buffer.add_bytes(raw)

        self.assertEqual(buffer.get_all_channels().shape[1], 1)
        self.assertAlmostEqual(buffer.total_time_seconds(), 0.001)


if __name__ == "__main__":
    unittest.main()
