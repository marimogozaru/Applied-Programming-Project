from PySide6.QtCore import QObject, QTimer, Signal
import numpy as np
from service.tcp_client import TCPClient

from signal_processing import compute_rms, apply_bandpass_filter

class MainViewModel(QObject):
    plot_updated = Signal(object, object) #x,y
    status_updated = Signal(str)

    def __init__(
        self,
        host: str = "localhost",
        port: int = 12345,
        sampling_rate: float = 1000.0,
        n_channels: int = 32,
        samples_per_packet: int = 18,
        buffer_seconds: float = 10.0,
    ):
        super().__init__()
        self.tcp_client = TCPClient(
            host = host,
            port = port,
            n_channels = n_channels,
            samples_per_packet = samples_per_packet,
            sampling_rate = sampling_rate,
            buffer_seconds = buffer_seconds,
        )
        self.is_plotting = False
        self.is_paused = False
        self.selected_channel = 0
        self.plot_all_channels = False

        self.mode = "Original"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    # Netwrok connection 
    def connect_tcp(self, host = None, port = None) -> None:
        if host is not None:
            self.tcp_client.host = host
        if port is not None:
            self.tcp_client.port = port
        try: 
            self.tcp_client.connect()
            self.status_updated.emit(f"Connected to {self.tcp_client.host}:{self.tcp_client.port}")
        except OSError as e:
            self.status_updated.emit(f"Failed to connect: {e}")

    def disconnect_tcp(self) -> None:
        self.stop_visualization()
        self.tcp_client.disconnect()
        self.status_updated.emit(f"Disconnected from {self.tcp_client.host}:{self.tcp_client.port}")

    # Visalization control
    def start_visualization(self) -> None:
        if not self.tcp_client.connected:
            self.connect_tcp()
            if not self.tcp_client.connected:
                return
        self.is_plotting = True 
        self.is_paused = False
        self.timer.start(10)
        self.status_updated.emit("Visualization commenced")

    def stop_visualization(self) -> None:
        self.timer.stop()
        self.is_plotting = False
        self.is_paused = False
        self.status_updated.emit("Visualization stopped")

    def pause_visualization(self) -> None:
        if self.is_plotting and not self.is_paused:
            self.is_paused = True
            self.status_updated.emit("Visualization paused")

    def resume_visualization(self) -> None:
        if self.is_plotting and self.is_paused:
            self.is_paused = False
            self.status_updated.emit("Visualization resumed")

    def clear_data(self) -> None:
        self.tcp_client.buffer.clear()
        self.status_updated.emit("Buffer cleared")

    def has_enough_data(self) -> bool:
        return self.tcp_client.buffer.has_enough_data()

    def get_channel_data(self, channel_index: int) -> np.ndarray:
        return self.tcp_client.buffer.get_channel(channel_index)
    
    def update_plot(self) -> None:
        if not self.is_plotting:
            return
        
        self.tcp_client.update()
        if self.is_paused:
            return
        if not self.has_enough_data():
            return
        
        x = self.tcp_client.buffer.get_time_axis()

        if self.plot_all_channels:
            y = self.tcp_client.buffer.get_all_channels()
        else:
            y = self.tcp_client.buffer.get_channel(self.selected_channel)

        if self.mode == "RMS":
            if y.shape[-1] >= 50:
                y = compute_rms(y)
        elif self.mode == "Filtered":
            if y.shape[-1] >= 30:
                y = apply_bandpass_filter(y, self.tcp_client.sampling_rate)
        
        self.plot_updated.emit(x,y)
