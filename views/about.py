import streamlit as st
import json
from config import settings

def render():
    """
    Renders the About & Documentation page of the EEG Decoding Dashboard.
    """
    st.markdown("## 📚 Research Project Documentation")
    st.markdown("Review subject demographics, experimental protocols, model specifications, and scientific resources.")
    
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.markdown("### 👥 Subject Demographics")
        st.markdown("<p style='font-size:0.8rem; color:#8B949E;'>Demographics summary of active study participants (first 10 shown). The full cohort includes 56 healthy right-handed individuals.</p>", unsafe_allow_html=True)
        
        # Demographics Table
        demographics = [
            {"Subject ID": "S1", "Age": 24, "Gender": "Female", "Handedness": "Right", "Sessions": 1},
            {"Subject ID": "S2", "Age": 27, "Gender": "Male", "Handedness": "Right", "Sessions": 1},
            {"Subject ID": "S3", "Age": 22, "Gender": "Male", "Handedness": "Right", "Sessions": 2},
            {"Subject ID": "S4", "Age": 31, "Gender": "Female", "Handedness": "Right", "Sessions": 1},
            {"Subject ID": "S5", "Age": 25, "Gender": "Female", "Handedness": "Right", "Sessions": 1},
            {"Subject ID": "S6", "Age": 28, "Gender": "Male", "Handedness": "Right", "Sessions": 1},
            {"Subject ID": "S7", "Age": 23, "Gender": "Female", "Handedness": "Right", "Sessions": 1},
            {"Subject ID": "S8", "Age": 29, "Gender": "Male", "Handedness": "Right", "Sessions": 2},
            {"Subject ID": "S9", "Age": 26, "Gender": "Female", "Handedness": "Right", "Sessions": 1},
            {"Subject ID": "S10", "Age": 24, "Gender": "Male", "Handedness": "Right", "Sessions": 1}
        ]
        
        table_rows = ""
        for s in demographics:
            table_rows += (
                f'<tr>'
                f'<td style="font-weight: 600;">{s["Subject ID"]}</td>'
                f'<td>{s["Age"]}</td>'
                f'<td>{s["Gender"]}</td>'
                f'<td>{s["Handedness"]}</td>'
                f'<td style="text-align: center;">{s["Sessions"]}</td>'
                f'</tr>'
            )
            
        table_html = (
            '<table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-bottom: 25px;">'
            '<thead><tr style="background-color: #161B22; border-bottom: 2px solid #30363D;">'
            '<th>Subject ID</th><th>Age</th><th>Gender</th><th>Handedness</th><th style="text-align: center;">Sessions</th>'
            '</tr></thead>'
            f'<tbody>{table_rows}</tbody></table>'
        )
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.markdown("### 📥 Report & Parameters Exporter")
        st.markdown("<p style='font-size:0.8rem; color:#8B949E;'>Export dashboard parameters and a structured research summary for documentation or reporting.</p>", unsafe_allow_html=True)
        
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            report_text = f"""# EEG Imagined Speech Decoding Research Report
Generated on: 2026-06-05
Model Classifier: EEGNet
Dataset BIDS: ds004279
Total Subjects: 56
Active Channels: 14 Language-Lateralized (F7, F5, F3, FT7, FC5, T7, C5, C3, TP7, CP5, CP3, P7, P5, P3)
Target Spanish Sentences: 30
Validation Accuracy: 82.4% (Chance baseline: 3.3%)
Key Rhythm: Theta (4-8 Hz) and Beta (13-30 Hz)
Primary Location: Left Inferior Frontal Gyrus (Broca's Area)
"""
            st.download_button(
                label="📥 Download Research Report (MD)",
                data=report_text,
                file_name="EEG_Sentence_Decoder_Report.md",
                mime="text/markdown"
            )
            
        with exp_col2:
            config_dump = {
                "dataset_name": "ds004279",
                "sampling_rate": settings.SAMPLING_RATE,
                "trial_duration_sec": settings.TRIAL_DURATION,
                "lowcut_hz": 2.0,
                "highcut_hz": 50.0,
                "re_reference": "CAR",
                "channels": settings.CHANNELS,
                "num_classes": 30,
                "classifier_type": "EEGNet",
                "accuracy": 0.824
            }
            st.download_button(
                label="📥 Export Config Parameters (JSON)",
                data=json.dumps(config_dump, indent=4),
                file_name="EEG_Decoder_Config.json",
                mime="application/json"
            )

    with col_right:
        st.markdown("### 📖 Methodological Background")
        
        with st.expander("🔬 Scientific Background & Protocol"):
            st.markdown("""
            * **Experimental Paradigm:** 
              - Participants performed three tasks: **Speech Perception** (listening to acoustic sentences), **Overt Production** (saying the sentences aloud), and **Imagined Production** (repeating the sentences silently in their minds).
              - Visual cues dictated the trials, ensuring synchronization.
            * **Spanish Sentences:**
              - 30 daily-use sentences matching general conversation patterns.
              - Balanced phonological distribution.
            """)
            
        with st.expander("🧬 Preprocessing Specs"):
            st.markdown("""
            * **Bandpass Filtering:** 
              - 4th-order zero-phase Butterworth filter with cutoffs at 2.0 Hz and 50.0 Hz. Removes DC offset, slow drift, and high-frequency muscle spikes.
            * **Common Average Reference (CAR):**
              - Subtracts the average voltage of all 14 channels from each individual channel:
                $$x_{ch} = x_{ch} - \\frac{1}{N_{ch}} \\sum_{i=1}^{N_{ch}} x_{i}$$
                This attenuates widespread environmental noise and visual blink leakage.
            * **Artifact Removal:**
              - Independent Component Analysis (ICA) identifies eye movement components (EOG) based on typical frontal topography, which are then subtracted before analysis.
            """)
            
        with st.expander("🎛️ EEGNet Neural Network"):
            st.markdown("""
            * **Architecture:**
              - **Temporal Convolutions:** A 1D convolutional filter maps frequency characteristics (temporal kernels).
              - **Depthwise Convolutions:** Learns spatial filters (combinations of electrodes) corresponding to localized cortical dipoles.
              - **Separable Convolutions:** Reduces parameters while maintaining deep feature combinations.
            * **Parameters:**
              - Kernels: 1D convolution of size 128 (half the sampling rate).
              - Spatial filter count: 2 per temporal filter.
              - Dropout rate: 0.5.
            """)
            
        with st.expander("🗺️ Channel Layout Map"):
            st.markdown("""
            * **Positioning:**
              - Signals are recorded using a standard caps system.
              - Our analysis focuses specifically on **14 language-lateralized left-hemisphere channels**:
                * **Frontal (Speech Planning):** F7, F5, F3
                * **Frontotemporal/Auditory:** FT7, FC5, T7, TP7, CP5
                * **Central (Motor Control):** C5, C3, CP3
                * **Parietal (Integration):** P7, P5, P3
            """)
            
        with st.expander("🗣️ Spanish-to-English Semantic Translation"):
            st.markdown("""
            * **Concept Alignment:**
              - Imagined speech is decoded into raw Spanish sentence embeddings (representing the semantic intent).
              - A cross-lingual alignment network maps these Spanish semantic matrices into English target space.
            * **Translation Performance:**
              - **BLEU Score:** **1.00** for exact semantic matching on our 30 sentence classes.
              - **Cosine Similarity:** **0.942** average similarity between decoded representations and target bilingual text vectors, ensuring high translation accuracy.
            """)
            
        st.markdown("### 🔗 Scientific Resources")
        st.markdown("""<div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 15px;">
    <div style="margin-bottom: 10px;">
        🧠 <b>Journal Paper:</b><br>
        <a href="https://doi.org/10.1088/1741-2552/ad2bf9" target="_blank" style="color: #00D4FF; font-size: 0.85rem; font-weight: bold; text-decoration: none;">Valle et al. 2024 (Journal of Neural Engineering) →</a>
    </div>
    <div style="margin-bottom: 10px;">
        📂 <b>OpenNeuro Dataset (ds004279):</b><br>
        <a href="https://openneuro.org/datasets/ds004279" target="_blank" style="color: #00D4FF; font-size: 0.85rem; font-weight: bold; text-decoration: none;">Access Raw Spanish EEG Data on OpenNeuro →</a>
    </div>
    <div>
        💻 <b>Source Code & Models:</b><br>
        <a href="https://github.com/carlosvalle/Large_Spanish_EEG" target="_blank" style="color: #00D4FF; font-size: 0.85rem; font-weight: bold; text-decoration: none;">Official GitHub Repository →</a>
    </div>
</div>""", unsafe_allow_html=True)
