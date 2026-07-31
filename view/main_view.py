from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QCheckBox, QLabel, QSlider
)

from view.plot_widget import ChannelPlotWidget          
from viewmodel.main_viewmodel import MainViewModel   
from view.offline_view import OfflineView           

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMG Visualization")

        self.view_model = MainViewModel()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        controls = QHBoxLayout()

        self.channel_selector = QComboBox()

        n_channels = self.view_model.tcp_client.buffer.n_channels
        for i in range(n_channels):
            self.channel_selector.addItem(f"Channel {i}")

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Original", "RMS", "Filtered"])
        
        self.all_channels_checkbox = QCheckBox("Plot all Channels")

        self.connect_button = QPushButton("Connect")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.pause_button = QPushButton("Pause")
        self.resume_button = QPushButton("Resume")

        for widget in (self.connect_button, self.channel_selector, self.mode_selector, self.all_channels_checkbox,
                       self.start_button, self.stop_button, self.pause_button, self.resume_button):
            controls.addWidget(widget)

        layout.addLayout(controls)

        self.status_label = QLabel("Not connected")
        layout.addWidget(self.status_label)

        self.plot_widget = ChannelPlotWidget(n_channels=32)
        layout.addWidget(self.plot_widget)

        self.view_model.plot_updated.connect(self.plot_widget.update_plot)
        self.view_model.status_updated.connect(self.status_label.setText)

        self.connect_button.clicked.connect(lambda: self.view_model.connect_tcp())
        self.start_button.clicked.connect(lambda: self.view_model.start_visualization())
        self.stop_button.clicked.connect(lambda: self.view_model.stop_visualization())
        self.pause_button.clicked.connect(lambda: self.view_model.pause_visualization())
        self.resume_button.clicked.connect(lambda: self.view_model.resume_visualization())

        self.mode_selector.currentTextChanged.connect(self.view_model.set_mode)
        
        self.channel_selector.currentIndexChanged.connect(self._on_channels_changed)
        self.all_channels_checkbox.toggled.connect(self._on_all_channels_toggled)

    def _open_offline_view(self):
        dialog = OfflineView(self.view_model.tcp_client.buffer, self)
        dialog.exec_()

    def _on_channels_changed(self, index: int) -> None:
        self.view_model.selected_channel = index

    def _on_all_channels_toggled(self, checked: bool) -> None:
        self.view_model.plot_all_channels = checked