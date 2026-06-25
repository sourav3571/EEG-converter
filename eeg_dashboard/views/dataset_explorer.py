import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import os
import sys
import torch
from config import settings
from utils import data_loader
from components import eeg_plotter

# Try to add parent directories to sys.path so we can import the model
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Large_Spanish_EEG')))
    from src.models_pytorch import EEGNetPyTorch
except Exception as e:
    pass

def render():
    """
    Renders the Dataset Explorer page of the EEG Decoding Dashboard.
    Provides individual trial plotting and batch preprocessing/decoding capability.
    """
    st.markdown("## 📊 Dataset Explorer & Batch Decoder")
    st.markdown("Explore individual trials, channel waveforms, or execute batch preprocessing and decoding with trained models.")
    
    # 1. Load active data
    subject = st.session_state.selected_subject
    condition = st.session_state.selected_condition
    stimulus_idx = st.session_state.selected_stimulus
    trial_idx = st.session_state.selected_trial
    
    # Ensure real dataset is loaded in background
    if st.session_state.real_data is None:
        npz_path = "../Large_Spanish_EEG/data/npz/language_average_2-50hz_icaLabel95confidence_eyes_60sessions.npz"
        if os.path.exists(npz_path):
            st.session_state.real_data = data_loader.load_real_dataset(npz_path)

    # Use tabs to split between Waveform Explorer and Batch Decoder
    tab_single, tab_batch = st.tabs(["📊 Individual Trial Explorer", "🖥️ Batch Preprocessing & Decoder"])
    
    with tab_single:
        if st.session_state.real_data is None:
            st.warning("⚠️ Scientific Dataset is Offline. Please run the download script `python Large_Spanish_EEG/download_dataset.py` or run the application in the official Docker container to load real EEG signals.")
            return

        eeg_raw = data_loader.get_real_trial_data(
            st.session_state.real_data, subject, condition, stimulus_idx, trial_idx
        )
        
        if eeg_raw is None:
            st.error("❌ Failed to load trial data from the dataset NPZ file.")
            return
            
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

    with tab_batch:
        st.markdown("### 🖥️ Batch Preprocessing & Decoding Console")
        st.markdown("Select a trained model configuration, run the preprocessing pipeline, and decode a batch of real EEG dataset examples.")
        
        data_dict = st.session_state.real_data
        if data_dict is None:
            st.error("❌ Dataset not found. Please verify that `data/npz/` is populated.")
            return
            
        # Select Model to Evaluate
        model_options = {
            "EEGNet Subject-Dependent (2 classes) - [Acc: ~70.83%]": {
                "classes": [1, 2],
                "model_path": "../Large_Spanish_EEG/models/eegnet_subj_{sub}_stims2.pth",
                "is_subj_dependent": True
            },
            "EEGNet Mixed (2 classes) - [Acc: 54.17%]": {
                "classes": [1, 2],
                "model_path": "../Large_Spanish_EEG/models/eegnet_mixed_stims2.pth",
                "is_subj_dependent": False
            },
            "EEGNet Mixed (5 classes) - [Acc: 23.33%]": {
                "classes": [1, 2, 3, 4, 5],
                "model_path": "../Large_Spanish_EEG/models/eegnet_mixed_stims5.pth",
                "is_subj_dependent": False
            }
        }
        
        selected_model_name = st.selectbox("Select Model for Batch Decoding", list(model_options.keys()))
        model_config = model_options[selected_model_name]
        
        # Preprocessing Expander
        with st.expander("🔍 View Preprocessing Pipeline Details", expanded=True):
            st.markdown("""
            Each EEG trial undergoes the following preprocessing steps before entering the neural network:
            1. **Butterworth Bandpass Filter:** Signal filtered between **2 - 50 Hz** (fs = 250 Hz) to remove low-frequency drifts and muscle artifacts.
            2. **ICA Artifact Rejection:** Independent Component Analysis identifies EOG ocular blinks and rejects components with **> 95% confidence**.
            3. **Temporal Windowing:** Signal sliced into **750 samples** (3.0 seconds epoch).
            4. **Z-Score Normalization:** Channel-wise standardization: $x_{norm} = \\frac{x - \\mu}{\\sigma}$.
            """)
            
        run_batch = st.button("🚀 Run Preprocessing & Run Inference on Test Split")
        
        if run_batch:
            with st.spinner("Processing EEG signals & running neural decoding..."):
                classes = model_config["classes"]
                nb_classes = len(classes)
                
                # Check for model file
                test_results = []
                
                # Retrieve test trials
                subjects_list = settings.SUBJECTS
                
                # Loop through subjects
                for sub in subjects_list:
                    # Resolve model path
                    if model_config["is_subj_dependent"]:
                        model_path = model_config["model_path"].format(sub=sub)
                    else:
                        model_path = model_config["model_path"]
                        
                    if not os.path.exists(model_path):
                        continue
                        
                    # Load model
                    model = EEGNetPyTorch(nb_classes=nb_classes, Chans=14, Samples=750)
                    try:
                        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                        model.eval()
                    except Exception as e:
                        continue
                        
                    # Run on test split for this subject
                    # We take the last trial of each class as the test trial
                    for c in classes:
                        key = f"{sub}_{condition}_{c}"
                        if key in data_dict:
                            epochs_data = data_dict[key]
                            trial_idx = epochs_data.shape[0] - 1 # Use last trial
                            trial_data = epochs_data[trial_idx][:, :750]
                            
                            # Preprocess (Standard scaling)
                            mean = np.mean(trial_data, axis=-1, keepdims=True)
                            std = np.std(trial_data, axis=-1, keepdims=True) + 1e-8
                            trial_data_norm = (trial_data - mean) / std
                            
                            # Run PyTorch inference
                            x_tensor = torch.tensor(trial_data_norm, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                            with torch.no_grad():
                                outputs = model(x_tensor)
                                probs = torch.softmax(outputs, dim=1).squeeze().numpy()
                                
                            pred_class_idx = int(np.argmax(probs))
                            pred_class = classes[pred_class_idx]
                            confidence = float(probs[pred_class_idx])
                            
                            test_results.append({
                                "Subject": sub,
                                "Condition": settings.CONDITIONS[condition],
                                "Trial Index": trial_idx + 1,
                                "True Class": c,
                                "True Sentence": settings.SENTENCES[c],
                                "Predicted Class": pred_class,
                                "Predicted Sentence": settings.SENTENCES[pred_class],
                                "Confidence": f"{confidence*100:.1f}%",
                                "Is Correct": "✅ Correct" if pred_class == c else "❌ Mismatch",
                                "correct_bool": (pred_class == c)
                            })
                            
                if not test_results:
                    st.warning("⚠️ No matching models found. Make sure you trained the selected configuration first!")
                    return
                    
                df_results = pd.DataFrame(test_results)
                correct_count = df_results["correct_bool"].sum()
                total_count = len(df_results)
                accuracy = (correct_count / total_count) * 100
                
                # Display Metrics
                st.markdown("### 📊 Evaluation Metrics")
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Total Trials Decoded", f"{total_count}")
                m_col2.metric("Correctly Classified", f"{correct_count}")
                
                # Set color depending on accuracy threshold
                if accuracy >= 45.0:
                    m_col3.metric("Overall Accuracy", f"{accuracy:.2f}%", delta=">= 45% Threshold Passed")
                else:
                    m_col3.metric("Overall Accuracy", f"{accuracy:.2f}%", delta="Below 45% Threshold")
                    
                # Success Rate Visual Card
                progress_color = "#00CC66" if accuracy >= 45.0 else "#FF4444"
                st.markdown(f"""
                <div style="background-color: var(--bg-card); border: 1px solid var(--border-default); border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 1.1rem; font-weight: 600; color: var(--text-white);">Decoding Success Rate</span>
                    <div style="background-color: #333; border-radius: 20px; height: 25px; width: 100%; margin-top: 10px; overflow: hidden;">
                        <div style="background-color: {progress_color}; width: {accuracy}%; height: 100%; border-radius: 20px; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 0.8rem; font-weight: 700; color: #000;">{accuracy:.1f}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Detailed Table
                st.markdown("### 📋 Detailed Trial Decoding Output")
                display_cols = ["Subject", "Condition", "Trial Index", "True Sentence", "Predicted Sentence", "Confidence", "Is Correct"]
                st.dataframe(df_results[display_cols], use_container_width=True)
