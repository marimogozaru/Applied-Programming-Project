from PySide6.QtWidgets import QVBoxLayout, QWidget
from vispy import scene
import numpy as np

class VisPyPlotWidget(QWidget):
    def __init__(
        self,
        n_channels: int = 32,
        channel_offset: float = 300.0
    ):
        super().__init__()

        self.n_channels = n_channels
        self.channel_offset = channel_offset

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.canvas = scene.SceneCanvas(
            keys='interactive',
            show=False,
            bgcolor='white',
            size=(1000, 600)
        )

        grid = self.canvas.central_widget.add_grid(margin=10)
        self.y_axis = scene.AxisWidget(orientation='left', axis_label='Amplitude')
        self.x_axis = scene.AxisWidget(orientation='bottom', axis_label='Time')
        self.y_axis.width_max = 50
        self.x_axis.height_max = 40
        grid.add_widget(self.y_axis, row=0, col=0)
        self.view = grid.add_view(row=0, col=1)
        self.view.camera = 'panzoom'
        grid.add_widget(self.x_axis, row=1, col=1)
        self.x_axis.link_view(self.view)
        self.y_axis.link_view(self.view)

        self.single_line = scene.Line(
            pos=np.array([[0.0, 0.0], [1.0, 1.0]]),
            color=(0.1, 0.3, 0.8, 1.0),
            parent = self.view.scene,
            width = 2
        )

        self.channel_lines = []
        for i in range(self.n_channels):
            line = scene.Line(pos=np.array([[0.0, 0.0], [1.0, 1.0]]),color=(0.1,0.3,0.8,1.0),
                              parent = self.view.scene, width=1)
            line.visible = False
            self.channel_lines.append(line)

        layout.addWidget(self.canvas.native)

    def update_plot(self, x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        if x.size == 0 or y.size == 0:
            return
        
        if y.ndim == 1: # One channel path
            self.single_line.visible = True
            for line in self.channel_lines:
                line.visible = False
            pos = np.column_stack((x,y))
            self.single_line.set_data(pos=pos)

            y_min, y_max = y.min(), y.max()

        elif y.ndim == 2: # Multi channel path
            self.single_line.visible = False

            for i in range(y.shape[0]):
                self.channel_lines[i].visible = True
                offset = i*self.channel_offset
                pos = np.column_stack((x, y[i] + offset))
                self.channel_lines[i].set_data(pos=pos)

            y_min = y.min()
            y_max = y.max() + (y.shape[0]-1)*self.channel_offset

        else:
            return

        y_pad = max(0.1, 0.1 * (y_max-y_min + 1e-9))  # 1e-9 guarantess that y_pad is never zero
        self.view.camera.set_range(
            x=(x.min(), x.max()),
            y=(y_min - y_pad, y_max + y_pad)
        )        
