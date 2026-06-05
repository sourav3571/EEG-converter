import numpy as np
from scipy import signal
from config import settings

def compute_psd(eeg_data, fs=250.0, nperseg=256):
    """
    Computes Power Spectral Density (PSD) for each channel using Welch's method.
    eeg_data shape: (channels, timepoints)
    Returns:
        freqs: array of sample frequencies
        psd: PSD of each channel, shape (channels, frequencies)
    """
    freqs, psd = signal.welch(eeg_data, fs=fs, nperseg=nperseg, axis=1)
    return freqs, psd

def extract_band_power(freqs, psd):
    """
    Extracts absolute band power for standard frequency bands:
        Delta: 0.5 - 4 Hz
        Theta: 4 - 8 Hz
        Alpha: 8 - 13 Hz
        Beta: 13 - 30 Hz
        Gamma: 30 - 50 Hz
    psd shape: (channels, frequencies)
    Returns a dictionary of band powers of shape (channels,)
    """
    bands = {
        "Delta": (0.5, 4.0),
        "Theta": (4.0, 8.0),
        "Alpha": (8.0, 13.0),
        "Beta": (13.0, 30.0),
        "Gamma": (30.0, 50.0)
    }
    
    band_powers = {}
    total_power = np.zeros(psd.shape[0])
    
    # Calculate total power in 0.5 - 50 Hz range
    idx_total = np.where((freqs >= 0.5) & (freqs <= 50.0))[0]
    total_power = np.trapz(psd[:, idx_total], freqs[idx_total], axis=1)
    # Avoid zero division
    total_power[total_power == 0] = 1.0
    
    for band_name, (low, high) in bands.items():
        idx_band = np.where((freqs >= low) & (freqs <= high))[0]
        if len(idx_band) > 0:
            power = np.trapz(psd[:, idx_band], freqs[idx_band], axis=1)
        else:
            power = np.zeros(psd.shape[0])
        
        band_powers[band_name] = {
            "absolute": power,
            "relative": power / total_power
        }
        
    return band_powers

def compute_spectrogram(channel_data, fs=250.0):
    """
    Computes time-frequency spectrogram for a single channel's data.
    channel_data shape: (timepoints,)
    Returns:
        freqs: array of sample frequencies (filtered 0-50 Hz)
        times: array of segment times
        Sxx: spectrogram values, shape (frequencies, times)
    """
    nperseg = 64
    noverlap = 56
    freqs, times, Sxx = signal.spectrogram(channel_data, fs=fs, nperseg=nperseg, noverlap=noverlap)
    
    # Filter frequencies between 0.5 and 50 Hz
    freq_mask = (freqs >= 0.5) & (freqs <= 50.0)
    return freqs[freq_mask], times, Sxx[freq_mask, :]
