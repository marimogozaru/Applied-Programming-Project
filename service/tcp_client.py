import socket
from .data_buffer import EmgDataBuffer

class TCPClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 12345,
        n_channels: int = 32,
        samples_per_packet: int = 18,  
        sampling_rate: float = 1000.0,
        buffer_seconds: float = 10.0,
    ):
        
        self.host = host
        self.port = port

        self.buffer = EmgDataBuffer(
            n_channels = n_channels,
            samples_per_packet = samples_per_packet,
            sampling_rate = sampling_rate,
            buffer_seconds = buffer_seconds,
        )

        self._socket = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        if self._connected:
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.setblocking(False)

        self._socket = sock
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None  

        self.buffer.clear()

    def update(self) -> None:
        if not self._connected or self._socket is None:
            return

        while True:
            try:
                chunk = self._socket.recv(4096)
                if not chunk:
                    self.disconnect()
                    return

                self.buffer.add_bytes(chunk)
            except BlockingIOError:
                break