import os
import streamlit as st
import numpy as np

# Set page configuration first (Must be the first Streamlit command)
st.set_page_config(
    page_title="EEG Imagined Spanish Sentence Decoder",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set working directory to project root to resolve relative paths correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Initialize Session State Variables
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = 'S3'
if 'selected_condition' not in st.session_state:
    st.session_state.selected_condition = 'perception'
if 'selected_trial' not in st.session_state:
    st.session_state.selected_trial = 0
if 'selected_stimulus' not in st.session_state:
    st.session_state.selected_stimulus = 1
if 'real_data' not in st.session_state:
    st.session_state.real_data = None
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Home / Overview"

# Import configurations & data loaders
from config import settings
from utils import data_loader

# Custom CSS Injection
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            
local_css("assets/style.css")

# Attempt to load real dataset in background (if file exists)
npz_path = "../Large_Spanish_EEG/data/npz/language_average_2-50hz_icaLabel95confidence_eyes_60sessions.npz"
real_data_exists = os.path.exists(npz_path)

if real_data_exists and st.session_state.real_data is None:
    with st.spinner("Loading scientific dataset in background..."):
        st.session_state.real_data = data_loader.load_real_dataset(npz_path)

# ========================================================
# GLOBAL SIDEBAR RENDER
# ========================================================
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 25px;'>
    <h2 style='margin-bottom: 0; color: var(--accent); font-family: "JetBrains Mono", monospace; font-size: 1.3rem; letter-spacing: 0.05em;'>NEURODECODE</h2>
    <p style='color: var(--text-muted); font-size: 0.75rem; margin-top: 5px; text-transform: uppercase; letter-spacing: 1.5px;'>Spanish imagined speech</p>
</div>
""", unsafe_allow_html=True)

# 1. Dataset & Demo Status Card
status_header = "DEMO ACTIVE" if st.session_state.demo_mode else "LIVE DATA ACTIVE"
status_class = "status-demo" if st.session_state.demo_mode else "status-loaded"
status_msg = "Running on simulated high-fidelity EEG data." if st.session_state.demo_mode else "Reading trials from ds004279 dataset."

st.sidebar.markdown(f"""
<div style='background-color: var(--bg-card); border: 1px solid var(--border-default); border-radius: 8px; padding: 14px; margin-bottom: 15px;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <span style='font-family: "JetBrains Mono", monospace; font-size: 9px; color: var(--text-muted); font-weight: 600; letter-spacing: 0.05em;'>SYSTEM STATUS</span>
        <span class="status-badge {status_class}">{status_header}</span>
    </div>
    <p style='font-family: "Inter", sans-serif; font-size: 11px; color: var(--text-light); margin: 10px 0 0 0; line-height: 1.4; font-weight: 300;'>{status_msg}</p>
</div>
""", unsafe_allow_html=True)

# 2. Demo Mode Toggle (Only show toggle if real data is available, otherwise lock to Demo)
if real_data_exists:
    demo_toggle = st.sidebar.checkbox("Enable Demo Mode", value=st.session_state.demo_mode, 
                                      help="Toggle between real dataset and synthetic mock data.")
    if demo_toggle != st.session_state.demo_mode:
        st.session_state.demo_mode = demo_toggle
        st.rerun()
else:
    st.sidebar.warning("Real dataset NPZ not found in cache. Locked in Demo Mode.")
    st.session_state.demo_mode = True

st.sidebar.markdown("<hr style='margin: 15px 0; border-color: var(--border-default);'>", unsafe_allow_html=True)

# 3. Global Selectors
st.sidebar.markdown("<p style='font-size: 0.75rem; font-family: \"JetBrains Mono\", monospace; font-weight: bold; color: var(--accent); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;'>Global Selectors</p>", unsafe_allow_html=True)

# Subject selection
subjects_list = settings.SUBJECTS
selected_sub = st.sidebar.selectbox("Select Subject", subjects_list, 
                                    index=subjects_list.index(st.session_state.selected_subject))
if selected_sub != st.session_state.selected_subject:
    st.session_state.selected_subject = selected_sub
    st.session_state.selected_trial = 0 # Reset trial index on subject change

# Condition selection (imagined vs overt vs visualized/perception)
cond_keys = list(settings.CONDITIONS.keys())
cond_display = [settings.CONDITIONS[k] for k in cond_keys]
selected_cond_idx = st.sidebar.selectbox("Experimental Task", range(len(cond_keys)), 
                                        format_func=lambda x: cond_display[x],
                                        index=cond_keys.index(st.session_state.selected_condition))
if cond_keys[selected_cond_idx] != st.session_state.selected_condition:
    st.session_state.selected_condition = cond_keys[selected_cond_idx]
    st.session_state.selected_trial = 0 # Reset trial index on condition change

# Sentence Stimulus Selection (to load trials for that specific sentence class)
sentence_ids = list(settings.SENTENCES.keys())
selected_stim = st.sidebar.selectbox("Sentence Class", sentence_ids,
                                     format_func=lambda x: f"S{x}: {settings.SENTENCES[x][:22]}... ({settings.SENTENCES_ENGLISH[x][:18]}...)",
                                     index=sentence_ids.index(st.session_state.selected_stimulus))
if selected_stim != st.session_state.selected_stimulus:
    st.session_state.selected_stimulus = selected_stim
    st.session_state.selected_trial = 0

# Trial Selector Slider (based on number of available epochs)
num_epochs = data_loader.get_number_of_epochs(st.session_state.real_data, 
                                             st.session_state.selected_subject, 
                                             st.session_state.selected_condition, 
                                             st.session_state.selected_stimulus)
selected_tr = st.sidebar.slider("Trial Repetition Index", 0, max(0, num_epochs - 1), 
                               value=min(st.session_state.selected_trial, num_epochs - 1))
if selected_tr != st.session_state.selected_trial:
    st.session_state.selected_trial = selected_tr

st.sidebar.markdown("<hr style='margin: 15px 0; border-color: var(--border-default);'>", unsafe_allow_html=True)

# 4. Navigation Menu
st.sidebar.markdown("<p style='font-size: 0.75rem; font-family: \"JetBrains Mono\", monospace; font-weight: bold; color: var(--accent); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;'>Navigation</p>", unsafe_allow_html=True)

navigation_pages = [
    "Home / Overview",
    "Dataset Explorer",
    "Preprocessing Pipeline",
    "Frequency Analysis",
    "Brain Topography",
    "Model Prediction",
    "Model Performance",
    "Research Insights",
    "About & Docs"
]

active_nav = st.sidebar.radio("Go to Page:", navigation_pages, label_visibility="collapsed",
                             index=navigation_pages.index(st.session_state.active_page))
if active_nav != st.session_state.active_page:
    st.session_state.active_page = active_nav
    st.rerun()

st.sidebar.markdown("""
<div style='margin-top: 30px; text-align: center; font-size: 0.7rem; color: #8B949E;'>
    <span>EEG Decoder UI v1.0.0</span><br>
    <span>Developed for Academic Research</span>
</div>
""", unsafe_allow_html=True)

# ========================================================
# PAGE ROUTING IMPLEMENTATION
# ========================================================
# Dynamically import page modules and render them
from views import (
    home, dataset_explorer, preprocessing, 
    frequency_analysis, brain_topography, 
    prediction, performance, insights, about
)

# Route execution
if st.session_state.active_page == "Home / Overview":
    home.render()
elif st.session_state.active_page == "Dataset Explorer":
    dataset_explorer.render()
elif st.session_state.active_page == "Preprocessing Pipeline":
    preprocessing.render()
elif st.session_state.active_page == "Frequency Analysis":
    frequency_analysis.render()
elif st.session_state.active_page == "Brain Topography":
    brain_topography.render()
elif st.session_state.active_page == "Model Prediction":
    prediction.render()
elif st.session_state.active_page == "Model Performance":
    performance.render()
elif st.session_state.active_page == "Research Insights":
    insights.render()
elif st.session_state.active_page == "About & Docs":
    about.render()
