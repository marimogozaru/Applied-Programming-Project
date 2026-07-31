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

The application strictly separates responsibilities across three layers, plus a standalone signal-processing module shared by both the live and offline views:

- **Model (`service/`)** : owns raw data. Has no knowledge of the GUI, Qt, or plotting.
- **ViewModel (`viewmodel/`)** : owns application state and logic. Bridges the Model and View using Qt `Signal`s and a `QTimer` polling loop. Has no knowledge of widgets or pixels.
- **View (`view/`)** : owns the UI. Displays whatever the ViewModel emits and forwards user actions (button clicks, dropdown changes) back to the ViewModel. Contains no data-processing logic of its own.

me project/
├── main.py # Application entry point
├── service/ # Model layer
│ ├── tcp_client.py # Non-blocking TCP socket client
│ └── data_buffer.py # Byte-to-array reconstruction + rolling buffer
├── viewmodel/
│ └── main_viewmodel.py # App state, TCP lifecycle, mode switching, Qt Signals
├── view/ # View layer
│ ├── main_view.py # Main window: controls + live VisPy plot
│ ├── plot_widget.py # VisPy canvas widget
│ └── offline_view.py # Offline analysis window (Matplotlib)
└── signal_processing.py # Stateless RMS + bandpass filter functions