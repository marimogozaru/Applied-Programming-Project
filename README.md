# EMG TCP Visualization Application

A real-time EMG signal visualization application built with **PySide6** and **VisPy**, following the **MVVM (Model-View-ViewModel)** architectural pattern,designed for monitoring and analyzing multi-channel data streams over TCP connections.

## Features

### Real-time Visualization
- GPU-accelerated live plotting via VisPy, capable of smooth updates at high refresh rates
- Single-channel view with a **Channel** selector dropdown
- **Plot all Channels** mode : displays all 32 channels simultaneously, vertically offset for readability
- Adjustable line **color** (cycling through a preset palette) and toggleable **grid**
- Auto-scaling camera range based on the currently visible signal

### TCP Communication
- Non-blocking TCP client for receiving binary EMG packets
- Byte-buffer reconstruction : correctly reassembles NumPy arrays even when TCP delivers partial or merged packets
- Graceful handling of server disconnects (detected via an empty `recv()`)
- Connection status feedback displayed directly in the UI

### Offline Analysis
- Separate analysis window, opened on demand from the main view
- Reads directly from the same in-memory buffer populated during the live session — no duplicate data storage
- Independent **Channel** and **Signal Mode** selectors
- Static Matplotlib plot with axis labels, toggleable grid, and color cycling

### Data Management
- Rolling buffer holding the most recent samples (configurable buffer duration)
- **Signal Mode** switching between :
  - *Original* : raw signal, unprocessed
  - *RMS* : Root Mean Square envelope (sliding window)
  - *Filtered* : bandpass Butterworth filter (1–100 Hz, 4th order)
- Mode switching is available in both the live single-channel view and the offline analysis view

## Architecture

The application follows the MVVM (Model-View-ViewModel) pattern separating responsibilities, plus a signal-processing module shared by both live and offline views:

```bash
me project/
├── main.py             # Application entry point
├── service/            # Model layer
│ ├── tcp_client.py       # Non-blocking TCP socket client
│ └── data_buffer.py      # Byte-to-array reconstruction + rolling buffer
├── viewmodel/
│ └── main_viewmodel.py   # App state, TCP lifecycle, mode switching, Qt Signals
├── view/               # View layer
│ ├── main_view.py        # Main window: controls + live VisPy plot
│ ├── plot_widget.py      # VisPy canvas widget
│ └── offline_view.py     # Offline analysis window (Matplotlib)
└── signal_processing.py # Stateless RMS + bandpass filter functions
```
**Data flow, live mode:**
`TCP_Server` → *socket bytes* → `service/tcp_client.py` → *raw bytes* → `service/data_buffer.py` → *NumPy array* → `viewmodel/main_viewmodel.py` (applies signal mode, emits `plot_updated`) → `view/plot_widget.py` (renders)

## Requirements

- Python 3.10+
- PySide6
- VisPy
- NumPy
- SciPy
- Matplotlib

All dependencies and their exact versions are pinned in *requirements.txt*.

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd "me project"
```

2. **Create and activate a virtual environment:**
```bash
python -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Verify the setup:**
```bash
python main.py
```

## Quick Start

```bash
# Terminal 1
cd TCP_Server
python main.py

# Terminal 2
cd "me project"
source .venv/bin/activate
python main.py
```

Then in the application window:
1. Click **Connect**
2. Click **Start**
3. Select a channel or check **Plot all Channels**

## Usage

### Live Visualization
- Use the **Channel** dropdown to choose which of the 32 channels to display.
- Check **Plot all Channels** to display all channels simultaneously, stacked vertically. In this mode, the signal shown is always *Original* : the *RMS*/*Filtered* modes only apply to single-channel view.
- Use the mode dropdown (*Original* / *RMS* / *Filtered*) to change how the single-channel signal is processed before plotting.
- Check **Show Grid** to overlay reference gridlines; click **Change Color** to cycle the plot line's color.

### Offline Analysis
- Click **Offline View** to open a separate window.
- This window reads from the data already collected during the current session — connect and let it run for a few seconds before opening it, so there's data to inspect.
- Independently select a channel and signal mode, then click **Refresh** to redraw.

## Application Controls

| Control | Function |
|---|---|
| **Connect** | Opens the TCP socket connection to the server |
| **Start** | Begins the plotting timer; connects automatically first if not already connected |
| **Stop** | Halts the plotting timer entirely |
| **Pause** | Freezes the displayed plot while the buffer continues receiving data in the background |
| **Resume** | Resumes plot updates after a pause, continuing from the current buffer state |
| **Channel** dropdown | Selects which single channel is displayed |
| **Signal Mode** dropdown | Switches between Original / RMS / Filtered processing |
| **Plot all Channels** checkbox | Toggles between single-channel and all-32-channel stacked view |
| **Show Grid** checkbox | Toggles gridline overlay on the live plot |
| **Change Color** | Cycles the plot line through a preset color palette |
| **Offline View** | Opens the offline Matplotlib analysis window |

## Troubleshooting

**`ModuleNotFoundError` on startup**
Ensure the virtual environment is activated *before* running `pip install -r requirements.txt` and before running `python main.py`. Check with `pip list` that `PySide6`, `vispy`, `numpy`, `scipy`, and `matplotlib` are present in the active environment.

**Connection fails / status stays "Not connected"**
Confirm `TCP_Server/main.py` is running first, in its own terminal, and printed a "Server started" message before launching the main application.

**Server crashes with a file-not-found error on `recording.pkl`**
The server script's default file path is hardcoded to the original development machine. Open `TCP_Server/main.py`, locate the `EMGTCPServer(...)` call at the bottom of the file, and update the `pkl_file` argument to the absolute path of *recording.pkl* on your machine.

**`qt.qpa.plugin: Could not find the Qt platform plugin "cocoa"` (macOS)**
This indicates a broken or conflicting PySide6/Qt installation, not an application bug. Try, in order: (1) check for a conflicting `PyQt5`/`PyQt6` install in the same environment and uninstall it, (2) `pip uninstall PySide6 -y && pip install PySide6` for a clean reinstall, (3) check for and `unset` a stray `QT_QPA_PLATFORM_PLUGIN_PATH` environment variable.

**Application crashes when combining "Filtered"/"RMS" mode with "Plot all Channels"**
This is a known limitation, not a bug: signal processing functions in *signal_processing.py* are designed for single-channel (1D) input. When "Plot all Channels" is active, mode processing is automatically skipped and the raw signal is shown instead.

**Performance is choppy / laggy**
Reduce the plotting timer interval's frequency in *viewmodel/main_viewmodel.py*, or reduce `buffer_seconds` in the `TCPClient` configuration to hold less historical data in memory.