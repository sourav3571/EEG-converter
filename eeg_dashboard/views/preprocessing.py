import streamlit as st
import numpy as np
import plotly.graph_objects as go
from config import settings
from utils import data_loader, preprocessor
from components import eeg_plotter

def render():
    """
    Renders the Preprocessing Pipeline page of the EEG Decoding Dashboard.
    """
    st.markdown("## 🧼 Preprocessing Pipeline")
    st.markdown("Inspect how the raw EEG signal is cleaned and normalized step-by-step through our scientific pipeline.")
    
    # 1. Pipeline Flow Diagram (HTML)
    st.markdown("""
    <div class="pipeline-container">
        <div class="pipeline-step completed">
            <span>🔌 Raw EEG Input</span><br>
            <span style="font-size: 0.65rem; opacity: 0.8;">64 Channels</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step completed">
            <span>⚡ Drop Bad Chans</span><br>
            <span style="font-size: 0.65rem; opacity: 0.8;">Dropped EMG, EKG</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step completed">
            <span>📉 Bandpass Filter</span><br>
            <span style="font-size: 0.65rem; opacity: 0.8;">2.0 - 50.0 Hz</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step completed">
            <span>🧿 ICA Artifact Clean</span><br>
            <span style="font-size: 0.65rem; opacity: 0.8;">95% CI EOG Removed</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step completed">
            <span>⚖️ Re-reference (CAR)</span><br>
            <span style="font-size: 0.65rem; opacity: 0.8;">Common Average</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step completed">
            <span>📏 Normalization</span><br>
            <span style="font-size: 0.65rem; opacity: 0.8;">Z-score scaled</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load raw and execute preprocessor
    is_demo = st.session_state.demo_mode
    subject = st.session_state.selected_subject
    condition = st.session_state.selected_condition
    stimulus_idx = st.session_state.selected_stimulus
    trial_idx = st.session_state.selected_trial
    
    eeg_raw = None
    if not is_demo and st.session_state.real_data is not None:
        eeg_raw = data_loader.get_real_trial_data(
            st.session_state.real_data, subject, condition, stimulus_idx, trial_idx
        )
        
    if eeg_raw is None:
        eeg_raw = data_loader.generate_synthetic_eeg(seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}") % 100000, has_artifacts=True)
        
    # Run the pipeline
    eeg_clean, stats = preprocessor.run_preprocessing_pipeline(
        eeg_raw, lowcut=2.0, highcut=50.0, fs=settings.SAMPLING_RATE, order=4, 
        seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}") % 100000
    )
    
    # Side-by-side Waveform Comparison
    st.markdown("### 🔍 Before / After Pipeline Comparison")
    
    col_raw, col_clean = st.columns(2)
    with col_raw:
        fig_raw = eeg_plotter.plot_eeg_waveforms(
            eeg_raw, settings.SAMPLING_RATE, 1.0, f"Raw Signal (with Artifacts & Drift)"
        )
        st.plotly_chart(fig_raw, use_container_width=True)
        
    with col_clean:
        fig_clean = eeg_plotter.plot_eeg_waveforms(
            eeg_clean, settings.SAMPLING_RATE, 1.0, f"Preprocessed Signal (ICA Cleaned & CAR)"
        )
        st.plotly_chart(fig_clean, use_container_width=True)
        
    st.markdown("<hr style='border-color: var(--border-default);'>", unsafe_allow_html=True)
    
    # Second Row: Filter response, Histograms & Stats
    col_left, col_right = st.columns([1.2, 2.5])
    
    with col_left:
        st.markdown("### 📊 Preprocessing Stats")
        
        stat_html = f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-default); border-radius: 8px; padding: 20px;">
            <div style="margin-bottom: 15px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Bad Channels Detected</span><br>
                <span style="font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 700; color: #FF4444;">EMG, EKG (dropped)</span>
            </div>
            <div style="margin-bottom: 15px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Epochs Before Rejection</span><br>
                <span style="font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--text-white);">{stats['trials_before']} trials</span>
            </div>
            <div style="margin-bottom: 15px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Epochs Kept</span><br>
                <span style="font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--accent);">{stats['trials_after']} trials</span>
            </div>
            <div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Artifact Rejection %</span><br>
                <span style="font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 700; color: #FFB800;">{stats['rejection_percentage']}</span>
            </div>
        </div>
        """
        st.markdown(stat_html, unsafe_allow_html=True)
        
        st.markdown("### 📐 Filter Frequency Response")
        # Butterworth response
        freqs, gain = preprocessor.get_filter_response(2.0, 50.0, settings.SAMPLING_RATE, order=4)
        
        fig_filt = go.Figure()
        fig_filt.add_trace(go.Scatter(x=freqs, y=gain, mode='lines', line=dict(color='#C4FF3D', width=2)))
        fig_filt.update_layout(
            xaxis_title="Frequency (Hz)",
            yaxis_title="Gain (dB)",
            xaxis=dict(range=[0, 100], gridcolor="#1F1F1F", linecolor="#2A2A2A"),
            yaxis=dict(range=[-80, 5], gridcolor="#1F1F1F", linecolor="#2A2A2A"),
            plot_bgcolor="#0A0A0A",
            paper_bgcolor="#0A0A0A",
            font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
            height=200,
            margin=dict(l=40, r=10, t=10, b=30)
        )
        st.plotly_chart(fig_filt, use_container_width=True)
        
    with col_right:
        st.markdown("### 📊 Amplitude Distribution Changes")
        
        # Histograms of all samples before and after preprocessing
        raw_flat = eeg_raw.flatten()
        clean_flat = eeg_clean.flatten()
        
        fig_hist = go.Figure()
        
        # Raw distribution (large spread, outlier tails from blinks)
        fig_hist.add_trace(go.Histogram(
            x=raw_flat,
            name="Raw Amplitudes",
            nbinsx=100,
            marker_color='rgba(255, 68, 68, 0.4)',
            xaxis='x',
            yaxis='y'
        ))
        
        # Clean distribution (tight normalized gaussian centered at 0)
        fig_hist.add_trace(go.Histogram(
            x=clean_flat,
            name="Preprocessed Amplitudes",
            nbinsx=100,
            marker_color='rgba(196, 255, 61, 0.6)',
            xaxis='x2',
            yaxis='y2'
        ))
        
        fig_hist.update_layout(
            grid=dict(rows=1, columns=2, pattern='independent'),
            title_text="Signal Amplitude Histograms (uV vs. Standardized Z-Score)",
            title_font=dict(size=13, color="#FFFFFF", family="JetBrains Mono"),
            plot_bgcolor="#0A0A0A",
            paper_bgcolor="#0A0A0A",
            font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
            height=430,
            margin=dict(l=40, r=20, t=50, b=40),
            legend=dict(x=0.75, y=0.95, bordercolor="var(--border-default)", borderwidth=1, bgcolor="rgba(10, 10, 10, 0.8)", font=dict(family="JetBrains Mono"))
        )
        
        # Update subplots axes labels
        fig_hist.update_layout(
            xaxis=dict(title="Voltage (µV)", gridcolor="#1F1F1F", linecolor="#2A2A2A", domain=[0, 0.45]),
            xaxis2=dict(title="Z-Score Amplitude", gridcolor="#1F1F1F", linecolor="#2A2A2A", domain=[0.55, 1.0]),
            yaxis=dict(title="Counts", gridcolor="#1F1F1F", linecolor="#2A2A2A"),
            yaxis2=dict(title="Counts", gridcolor="#1F1F1F", linecolor="#2A2A2A")
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
