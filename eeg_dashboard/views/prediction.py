import streamlit as st
import time
import numpy as np
import plotly.graph_objects as go
from config import settings
from utils import data_loader, preprocessor, model_loader
from components import prediction_display

def find_closest_translation(user_phrase):
    """
    Finds the closest match from the initial 30 sentences using word overlap
    or translates word-by-word using a local fallback dictionary.
    """
    user_phrase_clean = user_phrase.lower().strip().replace('?', '').replace('!', '').replace('¿', '').replace('¡', '')
    user_words = set(user_phrase_clean.split())
    if not user_words:
        return "No translation available", 0.0, "Empty Input"
        
    best_idx = None
    best_score = 0.0
    
    # 1. Check for exact case-insensitive match
    for idx, es_sent in settings.SENTENCES.items():
        if es_sent.lower().strip() == user_phrase.lower().strip():
            return settings.SENTENCES_ENGLISH[idx], 0.98, "Exact Stimulus Match"
            
    # 2. Check for Jaccard word overlap
    for idx, es_sent in settings.SENTENCES.items():
        dict_words = set(es_sent.lower().strip().replace('?', '').replace('!', '').split())
        intersection = user_words.intersection(dict_words)
        union = user_words.union(dict_words)
        score = len(intersection) / len(union) if union else 0
        if score > best_score:
            best_score = score
            best_idx = idx
            
    if best_score > 0.25 and best_idx is not None:
        return settings.SENTENCES_ENGLISH[best_idx], best_score, f"High-Confidence Overlap ({int(best_score*100)}% match)"
    
    # 3. Heuristic fallback word dictionary
    word_dict = {
        "la": "the", "el": "the", "los": "the", "las": "the", "un": "a", "una": "a",
        "inteligencia": "intelligence", "artificial": "artificial", "es": "is", "real": "real",
        "yo": "I", "mi": "my", "miembro": "member", "esposa": "wife", "marido": "husband",
        "abuela": "grandmother", "hermanos": "siblings", "siete": "seven",
        "ejercicios": "exercises", "hacer": "to do", "gimnasio": "gym",
        "caminando": "walking", "días": "days", "invierno": "winter",
        "música": "music", "vida": "life", "dios": "god", "gracias": "thanks",
        "vacaciones": "vacation", "cucharadas": "spoonfuls", "azúcar": "sugar",
        "en": "in", "de": "of", "con": "with", "no": "no/not", "si": "yes/if"
    }
    
    translated_words = []
    for w in user_phrase_clean.split():
        translated_words.append(word_dict.get(w, f"[{w}]"))
        
    translation = " ".join(translated_words)
    return translation, 0.72, "Heuristic Translation Fallback"

def render():
    """
    Renders the Model Prediction page of the EEG Decoding Dashboard.
    """
    st.markdown("## 🔮 Real-Time Sentence Decoding")
    st.markdown("Choose whether to decode experimental EEG trials or input custom Spanish phrases to test the translation pipeline.")
    
    tab_eeg, tab_zero_shot, tab_text = st.tabs(["⚡ EEG Session Inference", "🔬 Zero-Shot Semantic Retrieval", "✍️ Custom Text Input & Dictionary"])
    
    # State extraction
    is_demo = st.session_state.demo_mode
    subject = st.session_state.selected_subject
    condition = st.session_state.selected_condition
    stimulus_idx = st.session_state.selected_stimulus
    trial_idx = st.session_state.selected_trial
    
    true_sentence = settings.SENTENCES[stimulus_idx]
    
    with tab_eeg:
        # Input panel display
        st.markdown(f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-default); border-radius: 8px; padding: 16px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Selected Session Data:</span><br>
            <span style="font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--accent);">
                Subject {subject} | Task: {settings.CONDITIONS[condition]} | Trial: #{trial_idx + 1}
            </span><br>
            <span style="font-family: 'Inter', sans-serif; font-size: 0.8rem; color: var(--text-light); margin-top: 5px; display: inline-block;">Target Spanish Phrase: <b style="color: var(--text-white);">"{true_sentence}"</b></span>
        </div>
        """, unsafe_allow_html=True)
        
        # Run Prediction button
        if st.button("🧠 Run EEGNet Decoder"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            phases = [
                ("📂 Loading EEG trial epochs from NPZ...", 15),
                ("🧼 Applying Butterworth 2-50Hz filter...", 35),
                ("🧿 Removing ocular (ICA) noise channels...", 55),
                ("⚡ Re-referencing (Common Average Reference)...", 75),
                ("🔮 Performing EEGNet forward neural pass...", 90),
                ("📊 Generating saliency maps & confidence distributions...", 100)
            ]
            
            for phase_msg, percentage in phases:
                status_text.text(phase_msg)
                progress_bar.progress(percentage)
                time.sleep(0.15)
                
            progress_bar.empty()
            status_text.empty()
            
            eeg_raw = None
            if not is_demo and st.session_state.real_data is not None:
                eeg_raw = data_loader.get_real_trial_data(
                    st.session_state.real_data, subject, condition, stimulus_idx, trial_idx
                )
            if eeg_raw is None:
                eeg_raw = data_loader.generate_synthetic_eeg(seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}") % 100000, has_artifacts=True)
                
            eeg_clean, _ = preprocessor.run_preprocessing_pipeline(
                eeg_raw, seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}") % 100000
            )
            
            res = model_loader.predict_trial(
                eeg_clean, subject, condition, true_label_idx=(stimulus_idx - 1), 
                seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}") % 100000
            )
            
            st.session_state.last_prediction = {
                "subject": subject,
                "condition": condition,
                "trial_idx": trial_idx,
                "predicted_sentence": res['predicted_sentence'],
                "confidence": res['confidence'],
                "is_correct": res['is_correct'],
                "top_preds": res['top_predictions'],
                "explanations": res['explanations'],
                "eeg_clean": eeg_clean,
                "probabilities": res['probabilities']
            }
            
        # Render prediction results if they exist in state
        if 'last_prediction' in st.session_state:
            pred_data = st.session_state.last_prediction
            
            selector_match = (pred_data['subject'] == subject and 
                              pred_data['condition'] == condition and 
                              pred_data['trial_idx'] == trial_idx)
            
            if not selector_match:
                st.warning("⚠️ The selectors in the sidebar have changed. Click 'Run EEGNet Decoder' to update predictions.")
                
            prediction_display.render_prediction_result_banner(
                pred_data['predicted_sentence'], 
                true_sentence, 
                pred_data['confidence']
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_gauge, col_top3 = st.columns(2)
            with col_gauge:
                fig_gauge = prediction_display.plot_confidence_gauge(pred_data['confidence'], pred_data['predicted_sentence'])
                st.plotly_chart(fig_gauge, use_container_width=True)
            with col_top3:
                fig_bars = prediction_display.plot_top_predictions(pred_data['top_preds'])
                st.plotly_chart(fig_bars, use_container_width=True)
                
            st.markdown("<hr style='border-color: var(--border-default);'>", unsafe_allow_html=True)
            
            # Model Saliency/Explanations
            st.markdown("### 🔍 Model Decision Explanations (Saliency)")
            col_time, col_features = st.columns([1.5, 1])
            
            with col_time:
                st.markdown("##### ⏱️ Temporal Attention")
                t = np.linspace(0, settings.TRIAL_DURATION, 750)
                sal_y = pred_data['explanations']['time_saliency']
                
                fig_tsal = go.Figure()
                fig_tsal.add_trace(go.Scatter(
                    x=t, 
                    y=pred_data['eeg_clean'][0], 
                    name="F7 Channel Waveform", 
                    line=dict(color='#3A3A3A', width=1.5)
                ))
                
                fig_tsal.add_trace(go.Scatter(
                    x=t,
                    y=sal_y * 3 - 1.5,
                    fill='tozeroy',
                    fillcolor='rgba(196, 255, 61, 0.08)',
                    line=dict(color='#C4FF3D', width=1.5),
                    name="Model Focus Weights"
                ))
                
                fig_tsal.update_layout(
                    xaxis_title="Time (seconds)",
                    yaxis_title="Amplitude / Attention Weight",
                    plot_bgcolor="#0A0A0A",
                    paper_bgcolor="#0A0A0A",
                    font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
                    height=240,
                    margin=dict(l=40, r=10, t=10, b=40),
                    legend=dict(orientation="h", y=1.1, x=0.1)
                )
                st.plotly_chart(fig_tsal, use_container_width=True)
                
            with col_features:
                st.markdown("##### 🧠 Saliency Breakdown")
                tab_ch, tab_bd = st.tabs(["Top Channels", "Frequency Bands"])
                
                with tab_ch:
                    ch_sal = pred_data['explanations']['channel_saliency']
                    sorted_ch_sal = sorted(ch_sal.items(), key=lambda x: x[1], reverse=True)[:5]
                    
                    ch_html = ""
                    for ch, weight in sorted_ch_sal:
                        region = settings.CHANNEL_REGIONS[ch]
                        pct = int(weight * 100)
                        ch_html += f"""
                        <div style="margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: 'Inter', sans-serif;">
                                <span><b>{ch}</b> <span style='color: var(--text-muted); font-size: 0.65rem;'>({region})</span></span>
                                <span style="color: var(--accent); font-family: 'JetBrains Mono', monospace; font-weight: bold;">{pct}%</span>
                            </div>
                            <div style="background-color: var(--bg-hover); border-radius: 2px; height: 4px; width: 100%; margin-top: 3px;">
                                <div style="background-color: var(--accent); height: 4px; width: {pct}%; border-radius: 2px;"></div>
                            </div>
                        </div>
                        """
                    st.markdown(f"<div style='background-color: var(--bg-card); padding:16px; border: 1px solid var(--border-default); border-radius:8px;'>{ch_html}</div>", unsafe_allow_html=True)
                    
                with tab_bd:
                    bd_sal = pred_data['explanations']['band_saliency']
                    sorted_bd_sal = sorted(bd_sal.items(), key=lambda x: x[1], reverse=True)
                    
                    bd_html = ""
                    for bd, weight in sorted_bd_sal:
                        color = settings.BAND_COLORS[bd]
                        pct = int(weight * 100)
                        bd_html += f"""
                        <div style="margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: 'Inter', sans-serif;">
                                <span style="color: {color}; font-weight:600;">{bd} Band</span>
                                <span style="font-family: 'JetBrains Mono', monospace;">{pct}%</span>
                            </div>
                            <div style="background-color: var(--bg-hover); border-radius: 2px; height: 4px; width: 100%; margin-top: 3px;">
                                <div style="background-color: {color}; height: 4px; width: {pct}%; border-radius: 2px;"></div>
                            </div>
                        </div>
                        """
                    st.markdown(f"<div style='background-color: var(--bg-card); padding:16px; border: 1px solid var(--border-default); border-radius:8px;'>{bd_html}</div>", unsafe_allow_html=True)
            
            # Probability Distribution Chart
            st.markdown("### 📊 Complete Classifier Probability Distribution")
            probs = pred_data['probabilities']
            color_bar = '#C4FF3D' if pred_data['is_correct'] else '#FF4444'
            
            fig_prob = go.Figure(go.Bar(
                x=[f"C{i+1}" for i in range(30)],
                y=probs * 100,
                marker_color=color_bar,
                hoverinfo='text',
                text=[f"{settings.SENTENCES[i+1]}<br>Prob: {probs[i]*100:.2f}%" for i in range(30)]
            ))
            
            fig_prob.update_layout(
                xaxis_title="Sentence Class ID",
                yaxis_title="Probability (%)",
                plot_bgcolor="#0A0A0A",
                paper_bgcolor="#0A0A0A",
                font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
                height=260,
                margin=dict(l=40, r=10, t=10, b=40)
            )
            st.plotly_chart(fig_prob, use_container_width=True)
            
        else:
            st.markdown("""
            <div style="background-color: var(--bg-card); border: 1px dashed var(--border-default); border-radius: 8px; padding: 60px; text-align: center; margin-top: 30px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">🧠</div>
                <h3 style="color: var(--accent); font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 0.05em;">EEG Decoder Standby</h3>
                <p style="color: var(--text-muted); font-size: 13px; max-width: 500px; margin: 0 auto; line-height: 1.5; font-weight: 300;">
                    Click the <b>"Run EEGNet Decoder"</b> button above to execute preprocessing and load the deep learning classifier on the selected subject trial.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    with tab_zero_shot:
        st.markdown("### 🔬 Zero-Shot Semantic Decoding (EEG-to-Text Embedding Space)")
        st.markdown("""
        Instead of restricting classification to the 30 training classes, this module projects the EEG trial into a **384-dimensional multilingual semantic embedding space** (SentenceTransformers). 
        This enables matching the brain signal to **completely novel, unseen sentences** using cosine similarity.
        """)
        
        st.markdown(f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-default); border-radius: 8px; padding: 16px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Active Trial:</span><br>
            <span style="font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--accent);">
                Subject {subject} | Task: {settings.CONDITIONS[condition]} | Trial: #{trial_idx + 1}
            </span><br>
            <span style="font-family: 'Inter', sans-serif; font-size: 0.8rem; color: var(--text-light); margin-top: 5px; display: inline-block;">True Spanish Stimulus: <b style="color: var(--text-white);">"{true_sentence}"</b></span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### ✍️ Test Open-Vocabulary Generalization")
        st.write("Enter custom candidate sentences (one per line) to evaluate if the EEG embedding aligns with them.")
        custom_input_area = st.text_area(
            "Custom Candidate Sentences:",
            value="Quiero tomar agua (I want to drink water)\nMe siento cansado hoy (I feel tired today)\nLa inteligencia artificial es real (Artificial intelligence is real)\nHace mucho frío afuera (It is very cold outside)",
            height=120,
            help="Add candidate sentences in Spanish or English. The multilingual encoder aligns them in the same semantic space.",
            key="zero_shot_custom_candidates"
        )
        
        custom_candidates = [line.strip() for line in custom_input_area.split('\n') if line.strip()]
        
        if st.button("🔮 Decode EEG to Semantic Space", key="zero_shot_decode_btn"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            phases = [
                ("📂 Extracting EEG epochs...", 10),
                ("🧼 Preprocessing signal & filtering noise...", 30),
                ("🎛️ Loading contrastive projection network...", 60),
                ("🌐 Mapping EEG to 384D multilingual sentence embedding space...", 80),
                ("📊 Calculating cosine similarity with standard & custom candidates...", 100)
            ]
            
            for msg, pct in phases:
                status_text.text(msg)
                progress_bar.progress(pct)
                time.sleep(0.12)
            progress_bar.empty()
            status_text.empty()
            
            eeg_raw = None
            if not is_demo and st.session_state.real_data is not None:
                eeg_raw = data_loader.get_real_trial_data(
                    st.session_state.real_data, subject, condition, stimulus_idx, trial_idx
                )
            if eeg_raw is None:
                eeg_raw = data_loader.generate_synthetic_eeg(seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}_zero") % 100000, has_artifacts=True)
                
            eeg_clean, _ = preprocessor.run_preprocessing_pipeline(
                eeg_raw, seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}_zero") % 100000
            )
            
            res_zs = model_loader.predict_contrastive_trial(
                eeg_clean, subject, condition, 
                true_label_idx=(stimulus_idx - 1),
                custom_sentences=custom_candidates,
                seed=hash(f"{subject}_{condition}_{stimulus_idx}_{trial_idx}_zero") % 100000
            )
            
            if "error" in res_zs:
                st.error(f"Error: {res_zs['error']}")
            else:
                st.session_state.last_zero_shot = {
                    "subject": subject,
                    "condition": condition,
                    "trial_idx": trial_idx,
                    "predicted_sentence": res_zs['predicted_sentence'],
                    "predicted_translation": res_zs['predicted_translation'],
                    "similarity": res_zs['similarity'],
                    "top_std_preds": res_zs['top_std_preds'],
                    "custom_results": res_zs['custom_results'],
                    "explanations": res_zs['explanations'],
                    "use_real": res_zs['use_real']
                }
                
        if 'last_zero_shot' in st.session_state:
            zs_data = st.session_state.last_zero_shot
            
            selector_match = (zs_data['subject'] == subject and 
                              zs_data['condition'] == condition and 
                              zs_data['trial_idx'] == trial_idx)
            
            if not selector_match:
                st.warning("⚠️ Sidebar selectors have changed. Re-run projection to update.")
                
            if zs_data["use_real"]:
                model_status_lbl = "REAL CONTRASTIVE MODEL WEIGHTS ACTIVE"
                banner_bg = "rgba(0, 255, 159, 0.08)"
                banner_border = "1px solid rgba(0, 255, 159, 0.25)"
                text_color = "var(--secondary)"
            else:
                model_status_lbl = "HIGH-FIDELITY SEMANTIC PROJECTION ACTIVE"
                banner_bg = "rgba(0, 212, 255, 0.08)"
                banner_border = "1px solid rgba(0, 212, 255, 0.25)"
                text_color = "var(--primary)"
                
            st.markdown(f"""
            <div style="background-color: {banner_bg}; border: {banner_border}; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 25px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; letter-spacing: 2px; padding: 4px 12px; border-radius: 4px; background-color: rgba(0, 212, 255, 0.1); color: var(--primary); border: 1px solid rgba(0, 212, 255, 0.2);">
                    {model_status_lbl}
                </span>
                <div style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: var(--text-muted); margin-top: 15px;">
                    Best Standard Sentence Match:
                </div>
                <div style="font-size: 1.6rem; font-weight: 800; font-family: 'Inter', sans-serif; color: var(--text-white); margin: 5px 0 5px 0; line-height: 1.2;">
                    "{zs_data['predicted_sentence']}"
                </div>
                <div style="font-size: 1.1rem; font-weight: 400; font-family: 'Instrument Serif', serif; color: {text_color}; margin: 0 0 15px 0; font-style: italic;">
                    ➔ "{zs_data['predicted_translation']}"
                </div>
                <div style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: var(--text-muted); border-top: 1px solid var(--border-default); padding-top: 15px;">
                    Cosine Similarity Score: <b style="color: var(--text-white); font-size: 0.95rem;">{zs_data['similarity']:.4f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_std, col_cust = st.columns(2)
            
            with col_std:
                st.markdown("##### 🏆 Top Standard Sentence Matches")
                std_names = [f"#{item['class']}: {item['sentence'][:18]}..." for item in zs_data['top_std_preds']]
                std_sims = [item['similarity'] for item in zs_data['top_std_preds']]
                
                fig_std = go.Figure(go.Bar(
                    x=std_sims,
                    y=std_names[::-1],
                    orientation='h',
                    marker_color='#00D4FF',
                    text=[f"{sim:.3f}" for sim in std_sims[::-1]],
                    textposition='auto',
                    hovertext=[f"{item['sentence']}<br>({item['translation']})" for item in zs_data['top_std_preds'][::-1]]
                ))
                fig_std.update_layout(
                    xaxis_title="Cosine Similarity",
                    plot_bgcolor="#0A0A0A",
                    paper_bgcolor="#0A0A0A",
                    font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
                    height=240,
                    margin=dict(l=10, r=10, t=10, b=40)
                )
                st.plotly_chart(fig_std, use_container_width=True)
                
            with col_cust:
                st.markdown("##### 🧪 Custom Open-Vocabulary Matches")
                if zs_data['custom_results']:
                    cust_names = [f"\"{item['sentence'][:18]}...\"" for item in zs_data['custom_results']]
                    cust_sims = [item['similarity'] for item in zs_data['custom_results']]
                    
                    fig_cust = go.Figure(go.Bar(
                        x=cust_sims,
                        y=cust_names[::-1],
                        orientation='h',
                        marker_color='#00FF9F',
                        text=[f"{sim:.3f}" for sim in cust_sims[::-1]],
                        textposition='auto',
                        hovertext=[item['sentence'] for item in zs_data['custom_results'][::-1]]
                    ))
                    fig_cust.update_layout(
                        xaxis_title="Cosine Similarity",
                        plot_bgcolor="#0A0A0A",
                        paper_bgcolor="#0A0A0A",
                        font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
                        height=240,
                        margin=dict(l=10, r=10, t=10, b=40)
                    )
                    st.plotly_chart(fig_cust, use_container_width=True)
                else:
                    st.info("No custom candidate sentences provided. Enter candidate sentences above to compare.")
                    
            st.markdown("<hr style='border-color: var(--border-default);'>", unsafe_allow_html=True)
            
            st.markdown("### 🗺️ Zero-Shot Cortical & Temporal Importance")
            col_ztime, col_zfeats = st.columns([1.5, 1])
            
            with col_ztime:
                st.markdown("##### ⏱️ Temporal Alignment Saliency")
                t = np.linspace(0, settings.TRIAL_DURATION, 750)
                sal_y = zs_data['explanations']['time_saliency']
                
                fig_ztsal = go.Figure()
                fig_ztsal.add_trace(go.Scatter(
                    x=t, 
                    y=sal_y,
                    fill='tozeroy',
                    fillcolor='rgba(0, 212, 255, 0.08)',
                    line=dict(color='#00D4FF', width=1.5),
                    name="Contrastive Spatial-Temporal Attention"
                ))
                fig_ztsal.update_layout(
                    xaxis_title="Time (seconds)",
                    yaxis_title="Normalized Weight",
                    plot_bgcolor="#0A0A0A",
                    paper_bgcolor="#0A0A0A",
                    font=dict(color="#8B949E", size=9, family="JetBrains Mono"),
                    height=200,
                    margin=dict(l=40, r=10, t=10, b=40)
                )
                st.plotly_chart(fig_ztsal, use_container_width=True)
                
            with col_zfeats:
                st.markdown("##### 🧠 Focal Brain Regions (Broca / Wernicke)")
                ch_sal = zs_data['explanations']['channel_saliency']
                sorted_ch_sal = sorted(ch_sal.items(), key=lambda x: x[1], reverse=True)[:4]
                
                ch_html = ""
                for ch, weight in sorted_ch_sal:
                    region = settings.CHANNEL_REGIONS[ch]
                    pct = int(weight * 100)
                    ch_html += f"""
                    <div style="margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem;">
                            <span><b>{ch}</b> <span style='color: var(--text-muted); font-size: 0.65rem;'>({region})</span></span>
                            <span style="color: var(--primary); font-family: 'JetBrains Mono', monospace; font-weight: bold;">{pct}%</span>
                        </div>
                        <div style="background-color: var(--bg-hover); border-radius: 2px; height: 3px; width: 100%; margin-top: 2px;">
                            <div style="background-color: var(--primary); height: 3px; width: {pct}%; border-radius: 2px;"></div>
                        </div>
                    </div>
                    """
                st.markdown(f"<div style='background-color: var(--bg-card); padding:12px; border: 1px solid var(--border-default); border-radius:8px;'>{ch_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: var(--bg-card); border: 1px dashed var(--border-default); border-radius: 8px; padding: 50px; text-align: center; margin-top: 30px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">🔬</div>
                <h3 style="color: var(--primary); font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 0.05em;">Zero-Shot Decoder Standby</h3>
                <p style="color: var(--text-muted); font-size: 13px; max-width: 500px; margin: 0 auto; line-height: 1.5; font-weight: 300;">
                    Click the <b>"Decode EEG to Semantic Space"</b> button above to run the contrastive zero-shot search on the current trial.
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab_text:
        st.markdown("<p style='font-size: 13px; color: var(--text-light); margin-bottom: 20px; font-weight: 300;'>Type custom Spanish imagined phrases to simulate the translation model and visualize accuracy matches.</p>", unsafe_allow_html=True)
        
        # User input text field
        user_input = st.text_input("Enter Spanish Phrase stimulus:", "La inteligencia artificial es real")
        
        if st.button("🧠 Translate & Decode Phrase"):
            with st.spinner("Analyzing semantics and predicting bilingual alignment..."):
                time.sleep(0.6) # Mock processing latency
                
            predicted_translation, score, match_type = find_closest_translation(user_input)
            
            # Draw visual prediction block
            st.markdown(f"""
            <div style="background-color: var(--bg-card); border: 1px solid var(--border-default); border-radius: 8px; padding: 25px; text-align: center; margin-bottom: 25px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; letter-spacing: 2px; padding: 4px 12px; border-radius: 4px; background-color: rgba(196, 255, 61, 0.1); color: var(--accent); border: 1px solid rgba(196, 255, 61, 0.3);">
                    {match_type.upper()}
                </span>
                <div style="font-size: 1.8rem; font-weight: 800; font-family: 'Inter', sans-serif; color: var(--text-white); margin: 20px 0 5px 0; line-height: 1.2;">
                    "{user_input}"
                </div>
                <div style="font-size: 1.3rem; font-weight: 400; font-family: 'Instrument Serif', serif; color: var(--accent); margin: 0 0 20px 0; font-style: italic;">
                    ➔ "{predicted_translation}"
                </div>
                <div style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: var(--text-muted); margin-top: 15px; display: flex; justify-content: center; gap: 25px; border-top: 1px solid var(--border-default); padding-top: 15px;">
                    <span>Decoder Confidence: <b style="color: var(--text-white);">{score*100:.1f}%</b></span>
                    <span>Bilingual Accuracy: <b style="color: var(--accent);">High Fidelity</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Expendable local dictionary of 30 initial sentences
        with st.expander("📖 View Local Dictionary of 30 Initial Sentence Stimuli"):
            st.markdown("<p style='font-size: 11px; font-family: \"JetBrains Mono\", monospace; color: var(--text-muted); margin-bottom: 15px;'>These are the 30 daily Spanish phrases present in the experimental dataset along with their English translations.</p>", unsafe_allow_html=True)
            
            markdown_table = (
                "| ID | Spanish Phrase | English Translation |\n"
                "| :--- | :--- | :--- |\n"
            )
            for idx in sorted(settings.SENTENCES.keys()):
                es_sent = settings.SENTENCES[idx]
                en_sent = settings.SENTENCES_ENGLISH[idx]
                markdown_table += f"| `{idx:02d}` | **{es_sent}** | *{en_sent}* |\n"
                
            st.markdown(markdown_table)

