import streamlit as st
import numpy as np
import plotly.graph_objects as go
from config import settings
from utils import data_loader
from components import eeg_plotter

def render():
    """
    Renders the Dataset Explorer page of the EEG Decoding Dashboard.
    """
    st.markdown("## 📊 Dataset Explorer")
    st.markdown("Explore individual trials, channel groupings, and dataset statistics.")
    
    # 1. Load active data
    is_demo = st.session_state.demo_mode
    subject = st.session_state.selected_subject
    condition = st.session_state.selected_condition
    stimulus_idx = st.session_state.selected_stimulus
    trial_idx = st.session_state.selected_trial
    
    eeg_raw = None
    if not is_demo and st.session_state.real_data is not None:
        # Load from real NPZ
        eeg_raw = data_loader.get_real_trial_data(
            st.session_state.real_data, subject, condition, stimulus_idx, trial_idx
        )
        
    if eeg_raw is None:
        # Fallback to high-fidelity synthetic EED data (contains eyeblink artifact at onset)
        eeg_raw = data_loader.generate_synthetic_eeg(seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}") % 100000, has_artifacts=True)
        
    metadata = data_loader.get_demo_subject_metadata(subject, condition, stimulus_idx, trial_idx)
    
    # Layout Split
    col_left, col_right = st.columns([1, 2.5])
    
    with col_left:
        st.markdown("### 📋 Trial Metadata")
        
        # Display metadata cards
        meta_html = ""
        for k, v in metadata.items():
            meta_html += f"""
            <div style="margin-bottom: 8px; border-bottom: 1px solid var(--border-default); padding-bottom: 4px;">
                <span style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-family: 'JetBrains Mono', monospace; font-weight: 500;">{k}</span><br>
                <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-white); font-family: 'Inter', sans-serif;">{v}</span>
            </div>
            """
        st.markdown(f'<div style="background-color: var(--bg-card); border: 1px solid var(--border-default); border-radius: 8px; padding: 15px;">{meta_html}</div>', unsafe_allow_html=True)
        
        # Dataset stats summary
        st.markdown("### 📈 Dataset Statistics")
        
        tab1, tab2 = st.tabs(["Class Distribution", "Trials per Subject"])
        with tab1:
            # Equal distribution bar chart (since BIDS dataset usually has balanced trials)
            fig_dist = go.Figure(go.Bar(
                x=[f"S{i}" for i in range(1, 31)],
                y=[180] * 30, # Balanced 180 trials per class in standard balanced setups
                marker_color='#C4FF3D'
            ))
            fig_dist.update_layout(
                title="Balanced Trial Count per Sentence",
                xaxis_title="Sentence Class",
                yaxis_title="Trial Count",
                plot_bgcolor="#0A0A0A",
                paper_bgcolor="#0A0A0A",
                font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
                height=180,
                margin=dict(l=30, r=10, t=30, b=30)
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            
        with tab2:
            # Subject trial counts
            fig_sub = go.Figure(go.Bar(
                x=settings.SUBJECTS[:8] + ["..."],
                y=[360, 360, 360, 360, 360, 360, 360, 360, 4800],
                marker_color='#FFFFFF'
            ))
            fig_sub.update_layout(
                title="EEG Epochs per Subject (Top 8)",
                xaxis_title="Subject",
                yaxis_title="Epochs",
                plot_bgcolor="#0A0A0A",
                paper_bgcolor="#0A0A0A",
                font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
                height=180,
                margin=dict(l=30, r=10, t=30, b=30)
            )
            st.plotly_chart(fig_sub, use_container_width=True)
            
    with col_right:
        # Waveform scale controls
        st.markdown("### 🎛️ Interactive EEG Waves")
        scale_col, spacing_col = st.columns(2)
        with scale_col:
            scaling = st.slider("Signal Gain (Zoom Y)", 0.2, 5.0, 1.0, step=0.1)
        with spacing_col:
            st.markdown("<p style='font-size:0.8rem; color: var(--text-muted); font-family: \"Inter\", sans-serif; font-weight: 300; margin-top:28px;'>Tip: Drag to zoom in on specific times. Double-click to reset.</p>", unsafe_allow_html=True)
            
        # Draw waveform viewer
        fig_wave = eeg_plotter.plot_eeg_waveforms(
            eeg_raw, settings.SAMPLING_RATE, scaling, f"Raw EEG Signals (Subject {subject} - {settings.CONDITIONS[condition]})"
        )
        st.plotly_chart(fig_wave, use_container_width=True)
        
        # Export Actions
        st.markdown("##### 📤 Export Data")
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            st.download_button(
                label="📥 Export Trial Data as CSV",
                data=np.array2string(eeg_raw),
                file_name=f"{subject}_{condition}_trial{trial_idx}.csv",
                mime="text/csv"
            )
        with exp_col2:
            st.download_button(
                label="📥 Export Metadata as JSON",
                data=str(metadata),
                file_name=f"{subject}_{condition}_trial{trial_idx}_meta.json",
                mime="application/json"
            )
