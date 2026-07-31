from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QCheckBox)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from signal_processing import compute_rms, apply_bandpass_filter

class OfflineView(QDialog):

    COLORS = ["#0c68a9", "#d62728", "#2ca02c", "#ff7f0e"]

    def __init__(self, buffer, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Offline Data Visualization")
        self.buffer = buffer
        self.color_index = 0

        layout = QVBoxLayout(self)
        controls = QHBoxLayout()

        self.channel_selector = QComboBox()
        n_channels = self.buffer.n_channels
        for i in range(n_channels):
            self.channel_selector.addItem(f"Channel {i}")

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Original", "RMS", "Filtered"])

        self.grid_checkbox = QCheckBox("Show Grid")
        self.color_button = QPushButton("Change Color")
        self.refresh_button = QPushButton("Refresh")

        for z in (self.channel_selector, self.mode_selector, self.grid_checkbox, self.color_button, self.refresh_button):
            controls.addWidget(z)
        layout.addLayout(controls)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.refresh_button.clicked.connect(self.update_plot)
        self.grid_checkbox.toggled.connect(lambda _: self.plot_data())
        self.color_button.clicked.connect(self._cycle_color)

        self.plot_data()

    def _cycle_color(self):
        self.color_index = (self.color_index + 1) % len(self.COLORS)
        self.plot_data()

    def plot_data(self):
        channel_index = self.channel_selector.currentIndex()
        y = self.buffer.get_channel(channel_index)
        x = self.buffer.get_time_axis()

        if x.size == 0 or y.size == 0:
            return

        mode = self.mode_selector.currentIndex()
        if mode == "RMS":
            y = compute_rms(y, window_size=50)
        elif mode == "Filtered":
            y = apply_bandpass_filter(y, sampling_rate=self.buffer.sampling_rate, 
                                      low_cut=1.0, high_cut=100.0, order=4)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        current_color = self.COLORS[self.color_index]
        ax.plot(x, y, color=current_color)
        ax.grid(self.grid_checkbox.isChecked())
        ax.plot(x, y)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"Channel {channel_index} - {mode}")
        self.canvas.draw()