import numpy as np
from scipy.signal import butter, filtfilt

def compute_rms(signal: np.ndarray, window_size: int = 50) -> np.ndarray:
    signal = np.asarray(signal, dtype=np.float64)
    if signal.ndim != 1:
        raise ValueError("Input signal must be a 1D array")

    pad_size = window_size // 2
    padded = np.pad(signal, (pad_size, pad_size), mode="reflect")

    squared = padded ** 2
    kernel = np.ones(window_size)/window_size
    mean_squared = np.convolve(squared, kernel, mode="valid")

    rms = np.sqrt(mean_squared)
    return rms

def apply_bandpass_filter(
        signal: np.ndarray,
        sampling_rate: float,
        low_cut: float = 1.0,
        high_cut: float = 100.0,
        order: int=4
    )-> np.ndarray:

    signal =  signal = np.asarray(signal, dtype=float)
    if signal.ndim != 1:
        raise ValueError("apply_bandpass_filter expects a 1D signal array")

    nyquist = sampling_rate / 2.0

    low = low_cut/nyquist
    high = high_cut/nyquist

    low = max(low, 0.0)
    high = min(high, 1.0)

    b,a = butter(order, [[low,high]], btype='band')

    filtered_signal = filtfilt(b,a,signal)

    return filtered_signal