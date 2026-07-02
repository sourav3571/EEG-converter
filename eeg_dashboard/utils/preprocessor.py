# NOTE: This module contains illustrative preprocessing simulations for dashboard demonstration purposes. 
# Real MNE-ICA Label artifact rejection on ds004279 recordings requires the full training pipeline execution.
import numpy as np
from scipy import signal
from config import settings

def bandpass_filter(data, lowcut=2.0, highcut=50.0, fs=250.0, order=4):
    """
    Applies a Butterworth bandpass filter to EEG data.
    data shape: (channels, timepoints)
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    # Filter along the time axis (axis=1)
    filtered_data = signal.filtfilt(b, a, data, axis=1)
    return filtered_data

def common_average_reference(data):
    """
    Applies Common Average Reference (CAR) by subtracting the mean of all channels.
    data shape: (channels, timepoints)
    """
    mean_signal = np.mean(data, axis=0)
    car_data = data - mean_signal
    return car_data

def demo_artifact_simulation(raw_data, seed=42):
    """
    Illustrative artifact simulation for dashboard demonstration. 
    NOT equivalent to real Infomax ICA + MNE-ICA Label rejection which is proposed for the full training implementation.
    """
    np.random.seed(seed)
    n_channels, n_samples = raw_data.shape
    t = np.linspace(0, settings.TRIAL_DURATION, n_samples)
    
    # Re-generate the clean portion of the data (no artifacts)
    # We do this by reconstructing the raw_data but removing the blink and muscle envelopes
    blink_center = np.random.uniform(0.8, 2.2)
    blink_width = 0.25
    blink_envelope = np.exp(-((t - blink_center) / blink_width) ** 2)
    
    clean_data = raw_data.copy()
    
    # 1. Cancel the eye blink (EOG) artifact from all channels
    for ch_idx, ch_name in enumerate(settings.CHANNELS):
        if ch_name in ['F7', 'F5', 'F3']:
            blink_amp = 80.0
        elif ch_name in ['FT7', 'FC5', 'C5', 'C3']:
            blink_amp = 20.0
        else:
            blink_amp = 3.0
        
        # Subtract the simulated blink
        clean_data[ch_idx] -= blink_amp * blink_envelope
        
    # 2. Cancel high-frequency muscle (EMG) artifact
    # Run a lowpass filter to remove any muscle artifact above 50Hz
    # (Since EEG is 2-50Hz anyway, lowpassing during preprocessing removes it)
    nyq = 0.5 * settings.SAMPLING_RATE
    b_low, a_low = signal.butter(4, 45.0 / nyq, btype='low')
    
    # We apply this specifically to the channels affected (FT7, T7) to clean them
    t7_idx = settings.CHANNELS.index('T7')
    ft7_idx = settings.CHANNELS.index('FT7')
    
    clean_data[t7_idx] = signal.filtfilt(b_low, a_low, clean_data[t7_idx])
    clean_data[ft7_idx] = signal.filtfilt(b_low, a_low, clean_data[ft7_idx])
    
    return clean_data

def run_preprocessing_pipeline(raw_data, lowcut=2.0, highcut=50.0, fs=250.0, order=4, seed=42):
    """
    Executes the entire preprocessing pipeline step-by-step:
    Raw EEG -> Filter -> Artifact Removal (ICA) -> Re-reference (CAR) -> Normalize -> Clean EEG
    """
    # 1. Filter
    filtered = bandpass_filter(raw_data, lowcut, highcut, fs, order)
    
    # 2. Artifact Removal (ICA)
    ica_cleaned = demo_artifact_simulation(filtered, seed=seed)
    
    # 3. Re-reference (CAR)
    car_referenced = common_average_reference(ica_cleaned)
    
    # 4. Normalize (Z-score scaling per channel)
    mean = np.mean(car_referenced, axis=1, keepdims=True)
    std = np.std(car_referenced, axis=1, keepdims=True)
    std[std == 0] = 1.0 # Prevent division by zero
    normalized = (car_referenced - mean) / std
    
    return normalized, {
        "filter_completed": True,
        "ica_completed": True,
        "car_completed": True,
        "normalization_completed": True,
        "bad_channels_detected": ["EMG", "EKG"], # Standard dropped channels in main_pipeline
        "rejection_percentage": "12.4%", # Mock statistics corresponding to typical datasets
        "trials_before": 180,
        "trials_after": 158
    }

def get_filter_response(lowcut=2.0, highcut=50.0, fs=250.0, order=4):
    """
    Generates frequency response curves for visualization.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    w, h = signal.freqz(b, a, worN=2000)
    freqs = w * (fs / (2 * np.pi))
    gain = 20 * np.log10(abs(h) + 1e-8)
    return freqs, gain
