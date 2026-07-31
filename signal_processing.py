import numpy as np
from scipy.signal import butter, filtfilt

def compute_rms(signal: np.ndarray, window_size: int = 50) -> np.ndarray:
    if signal.ndim == 1:
        pad_size = window_size // 2
        padded = np.pad(signal, (pad_size, pad_size), mode="reflect")
        squared = padded ** 2
        kernel = np.ones(window_size) / window_size
        mean_squared = np.convolve(squared, kernel, mode="valid")
        rms = np.sqrt(mean_squared)
        return rms[:signal.shape[0]]
        
    elif signal.ndim == 2:
        n_channels = signal.shape[0]
        rms_2d = np.zeros_like(signal)
        for i in range(n_channels):
            rms_2d[i] = compute_rms(signal[i], window_size = window_size)
        return rms_2d
        
    else:
        raise ValueError("compute_rms expects a 1D or 2D array")

def apply_bandpass_filter(
        signal: np.ndarray,
        sampling_rate: float,
        low_cut: float = 1.0,
        high_cut: float = 100.0,
        order: int=4
    )-> np.ndarray:

    signal = np.asarray(signal, dtype=float)
    if signal.ndim != 1:
        raise ValueError("apply_bandpass_filter expects a 1D signal array")

    nyquist = sampling_rate / 2.0

    low = low_cut/nyquist
    high = high_cut/nyquist

    low = max(low, 0.0)
    high = min(high, 1.0)

    b,a = butter(order, [low,high], btype='band')

    filtered_signal = filtfilt(b,a,signal, axis=-1)

    return filtered_signal