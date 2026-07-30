import numpy as np

class EmgDataBuffer:
    def __init__(
            self,
            n_channels: int = 32,
            samples_per_packet: int = 18,
            sampling_rate: float = 1000.0,
            buffer_seconds: float = 10.0
    ):

        self.n_channels = n_channels
        self.samples_per_packet = samples_per_packet
        self.sampling_rate = sampling_rate
        self.buffer_seocnds = buffer_seconds

        self.dtype = np.float64

        self._packet_size = self.n_channels * self.samples_per_packet
        self._packet_size_bytes = self._packet_size * np.dtype(self.dtype).itemsize
        self._buffer_size = int(self.sampling_rate * self.buffer_seconds)

        self._byte_buffer = bytearray()
        self._data = np.empty((self.n_channles, 0), dtype=self.dtype)
        self._total_samples = 0

    def add_bytes(self, raw_bytes: bytes) -> None:
        self.byte_buffer.extend(raw_bytes)
        self._process_byte_buffer()

    def process_byte_buffer(self) -> None:
        packets = []

        while len(self._byte_buffer) >= self._packet_size_bytes:
            raw = self._byte_buffer[: self._packet_size_bytes]
            del self._byte_buffer[: self._packet_size_bytes]

            packet = np.frombuffer(raw, dtype = self.dtype)
            packet = packet.reshape((self.n_channles, self.samples_per_packet))
            packets.append(packet)

        if not packets:
            return
        new_data = np.concatenate(packets, axis =1)
        self._data = np.concatenate((self._data, new_data), axis =1)
        self._total_samples += new_data.shape[1]

        if self._data.shape[1] > self._buffer_size:
            self._data = self._data[:, -self._buffer_size:]

        def enough_data(self) -> bool:
            return self._data.shape[1] >= 2

        def get_all_channels(self) -> np.array:
            return self._data.copy()

        def get_channel(self, channel_index: int) -> np.array:
            all_data = self._get_all_channels()
            if all_data.shape[0] <= channel_index:
                raise IndexError(f"Channel index {channel_index} is out of range")
            return all_data[channel_index, :]

        def get_time_axis(self) -> np.array:
            n_samples = self._data.shape[1]
            return np.arange(n_samples)/self.sampling_rate

        def total_time_seconds(self) -> float:
            return self._total_samples / self.sampling_rate

        def clear(self) -> None:
            self._byte_buffer.clear()
            self._data = np.empty((self.n_channels, 0), dtype=self.dtype)
            self._total_samples = 0