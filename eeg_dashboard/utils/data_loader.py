import os
import numpy as np
import pandas as pd
import streamlit as st
from scipy import signal
from config import settings

@st.cache_resource
def load_real_dataset(filepath):
    """
    Loads the real EEG NPZ dataset file.
    Cached using streamlit's st.cache_data to prevent reloading.
    """
    if not os.path.exists(filepath):
        return None
    try:
        data_dict = np.load(filepath)
        return data_dict
    except Exception as e:
        st.error(f"Error loading NPZ file: {e}")
        return None

def get_real_trial_data(data_dict, subject, condition, stimulus_idx, trial_idx):
    """
    Retrieves a single trial from the real dataset.
    """
    key = f"{subject}_{condition}_{stimulus_idx}"
    if key not in data_dict:
        return None
    
    epochs_data = data_dict[key] # shape: (num_epochs, channels, timepoints)
    if trial_idx >= epochs_data.shape[0]:
        trial_idx = epochs_data.shape[0] - 1
        
    # Return shape: (channels, timepoints) -> (14, 750)
    return epochs_data[trial_idx]

def get_number_of_epochs(data_dict, subject, condition, stimulus_idx):
    """
    Gets the number of trials (epochs) available for a specific subject/condition/stimulus
    """
    key = f"{subject}_{condition}_{stimulus_idx}"
    if data_dict is not None and key in data_dict:
        return data_dict[key].shape[0]
    return 6 # Default for demo mode

def generate_synthetic_eeg(seed=42, has_artifacts=True):
    """
    Generates highly realistic synthetic EEG signal for 14 channels, 750 samples.
    Simulates 1/f spectral noise, channel-specific oscillations, and optional artifacts.
    """
    np.random.seed(seed)
    n_channels = len(settings.CHANNELS)
    n_samples = int(settings.SAMPLING_RATE * settings.TRIAL_DURATION)
    t = np.linspace(0, settings.TRIAL_DURATION, n_samples)
    
    # 1. Base 1/f noise (pink noise approximation using integration of white noise)
    white_noise = np.random.normal(0, 5.0, (n_channels, n_samples))
    b, a = signal.butter(1, 0.1, btype='low')
    pink_noise = signal.filtfilt(b, a, white_noise, axis=1) * 3.0
    
    # 2. Add realistic rhythmic oscillations based on brain region
    # Frontal channels: F7, F5, F3 (Theta wave: 4-8Hz, cognitive workload / speech planning)
    # Temporal: T7 (Alpha/Theta), Parietal: P7, P5, P3 (Alpha wave: 8-13Hz, visual/idle state)
    # Central/Motor: C5, C3 (Beta wave: 13-30Hz, motor imagery)
    
    signals = pink_noise.copy()
    
    for ch_idx, ch_name in enumerate(settings.CHANNELS):
        # Base amplitude (microvolts)
        amp = 8.0
        
        # Frontal channels: add theta (5-6 Hz)
        if ch_name in ['F7', 'F5', 'F3', 'FT7', 'FC5']:
            theta_freq = np.random.uniform(5, 7)
            theta_wave = amp * 1.2 * np.sin(2 * np.pi * theta_freq * t + np.random.uniform(0, 2*np.pi))
            signals[ch_idx] += theta_wave
            
        # Central/Motor channels: add beta (18-22 Hz)
        if ch_name in ['C5', 'C3', 'FC5']:
            beta_freq = np.random.uniform(18, 22)
            beta_wave = amp * 0.7 * np.sin(2 * np.pi * beta_freq * t + np.random.uniform(0, 2*np.pi))
            signals[ch_idx] += beta_wave
            
        # Parietal/Occipital/Temporal channels: add alpha (9-11 Hz)
        if ch_name in ['P7', 'P5', 'P3', 'TP7', 'T7']:
            alpha_freq = np.random.uniform(9, 11)
            alpha_wave = amp * 1.5 * np.sin(2 * np.pi * alpha_freq * t + np.random.uniform(0, 2*np.pi))
            signals[ch_idx] += alpha_wave
            
    # 3. Add Ocular Artifacts (EOG/Blinks) if requested
    if has_artifacts:
        # Simulate an eyeblink artifact (high-amplitude slow wave mainly in frontal channels F7, F5, F3)
        blink_center = np.random.uniform(0.8, 2.2)
        blink_width = 0.25 # seconds
        blink_envelope = np.exp(-((t - blink_center) / blink_width) ** 2)
        
        # Eyeblinks decrease in amplitude towards posterior channels
        for ch_idx, ch_name in enumerate(settings.CHANNELS):
            if ch_name in ['F7', 'F5', 'F3']:
                blink_amp = 80.0 # High amplitude blink (80 uV)
            elif ch_name in ['FT7', 'FC5', 'C5', 'C3']:
                blink_amp = 20.0
            else:
                blink_amp = 3.0 # Occipital has minimal blink leakage
                
            # Add blink wave (slow half-sine-like deflection)
            blink_wave = blink_amp * blink_envelope
            signals[ch_idx] += blink_wave
            
        # Add a muscle artifact (high-frequency noise in temporal/frontal channels)
        # T7 and FT7 are close to jaw muscles
        muscle_noise = np.random.normal(0, 15.0, n_samples)
        b_m, a_m = signal.butter(2, [40, 80], btype='bandpass', fs=settings.SAMPLING_RATE)
        filtered_muscle = signal.filtfilt(b_m, a_m, muscle_noise)
        
        signals[settings.CHANNELS.index('T7')] += filtered_muscle * 1.5
        signals[settings.CHANNELS.index('FT7')] += filtered_muscle * 1.0

    return signals # shape: (14, 750)

def get_demo_subject_metadata(subject, condition, stimulus_idx, trial_idx):
    """
    Generates realistic metadata for a trial.
    """
    spanish_sentence = settings.SENTENCES[stimulus_idx]
    return {
        "Subject ID": subject,
        "Condition": settings.CONDITIONS[condition],
        "Linguistic Stimulus (Spanish)": spanish_sentence,
        "Linguistic Category": "Daily Use Spanish Phrase",
        "Trial Repetition": f"Trial #{trial_idx + 1}",
        "Sampling Rate": f"{settings.SAMPLING_RATE} Hz",
        "Trial Duration": f"{settings.TRIAL_DURATION} s",
        "Number of Channels": f"{len(settings.CHANNELS)} (Selected Left-Hemisphere Language channels)",
        "Data Source": "Synthetic (Demo Mode)" if st.session_state.get('demo_mode', True) else "Live OpenNeuro NPZ Dataset"
    }
