from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QCheckBox, QLabel, QSlider
)

from view.plot_widget import ChannelPlotWidget
from viewmodel.main import MainViewModel

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
        for i in range(self.view_model.tcp_client.n_channels):
            self.channel_selector.addItem(f"Channel {i+1}")

        self.all_channels_checkbox = QCheckBox("Plot all Channels")

        self.connect_button = QPushButton("Connect")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.pause_button = QPushButton("Pause")
        self.resume_button = QPushButton("Resume")

        for widget in (self.connect_button, self.start_button, 
            self.stop_button, self.pause_button, self.resume_button):
            controls.addWidget(widget)

        layout.addLayout(controls)

        self.status_label = QLabel("Not connected")
        layout.addWidget(self.status_label)

        self.plot_widget = ChannelPlotWidget(n_channels=32)
        layout.addWidget(self.plot_widget)

        self.view_model.plot_updated.connect(self.plot_widget.update_plot)
        self.view_model.status_updated.connect(self.status_label.setText)
        self.connect_button.clicked.connect(lambda: self.view_model.connect_tcp())

        self.channel_selector.currentIndexChanged.connect(self.on_channels_changed)
        self.all_channels_checkbox.toggled.connect(self.on_all_channels_toggled)


    


