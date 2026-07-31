from PySide6.QtWidgets import QVBoxLayout, QWidget
from vispy import scene
import numpy as np


class VisPyPlotWidget(QWidget):
    """
    Qt Widget encapsulating a VisPy SceneCanvas for high-performance
    2D live signal visualization (single-channel or 32-channel stacked).
    """

    def __init__(
        self,
        n_channels: int = 32,
        channel_offset: float = 300.0,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.n_channels = n_channels
        self.channel_offset = channel_offset  # Vertical spacing for stacked channels

        # Layout container for canvas
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create VisPy Canvas with white background
        self.canvas = scene.SceneCanvas(
            keys="interactive", show=False, bgcolor="white", size=(1000, 600)
        )

        # 1. Setup Grid & Axes
        grid = self.canvas.central_widget.add_grid(margin=10)
        self.y_axis = scene.AxisWidget(orientation="left")
        self.x_axis = scene.AxisWidget(orientation="bottom")
        self.y_axis.width_max = 50
        self.x_axis.height_max = 40

        grid.add_widget(self.y_axis, row=0, col=0)
        self.view = grid.add_view(row=0, col=1)
        self.view.camera = "panzoom"

        grid.add_widget(self.x_axis, row=1, col=1)
        self.x_axis.link_view(self.view)
        self.y_axis.link_view(self.view)

        # 2. Pre-allocate Single Channel Line
        self.single_line = scene.Line(
            pos=np.array([[0.0, 0.0], [1.0, 0.0]]),
            color=(0.1, 0.3, 0.8, 1.0),
            parent=self.view.scene,
            width=2,
        )

        # 3. Pre-allocate Multi-Channel Lines (32 stacked channels)
        self.channel_lines = []
        for _ in range(self.n_channels):
            line = scene.Line(
                pos=np.array([[0.0, 0.0], [1.0, 0.0]]),
                color=(0.1, 0.3, 0.8, 1.0),
                parent=self.view.scene,
                width=1,
            )
            line.visible = False
            self.channel_lines.append(line)

        # Embed native VisPy Qt widget into layout
        layout.addWidget(self.canvas.native)

    def update_plot(self, x: np.ndarray, y: np.ndarray) -> None:
        """
        Updates line positions and rescales camera.
        - x: 1D time vector (shape: (N,))
        - y: 1D single channel (shape: (N,)) OR 2D all channels (shape: (n_channels, N))
        """
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        if x.size == 0 or y.size == 0:
            return

        # Single Channel Display Path
        if y.ndim == 1:
            self.single_line.visible = True
            for line in self.channel_lines:
                line.visible = False

            pos = np.column_stack((x, y))
            self.single_line.set_data(pos=pos)

            y_min, y_max = y.min(), y.max()

        # Multi-Channel Display Path (Stacked view)
        elif y.ndim == 2:
            self.single_line.visible = False

            n_ch = min(y.shape[0], len(self.channel_lines))
            for i in range(n_ch):
                self.channel_lines[i].visible = True
                offset = i * self.channel_offset
                pos = np.column_stack((x, y[i] + offset))
                self.channel_lines[i].set_data(pos=pos)

            # Hide unused lines if data has fewer channels
            for i in range(n_ch, len(self.channel_lines)):
                self.channel_lines[i].visible = False

            y_min = y.min()
            y_max = y.max() + (n_ch - 1) * self.channel_offset

        else:
            return

        # Update camera range with 10% vertical padding
        y_pad = max(0.1, 0.1 * (y_max - y_min + 1e-9))
        self.view.camera.set_range(
            x=(x.min(), x.max()), y=(y_min - y_pad, y_max + y_pad)
        )