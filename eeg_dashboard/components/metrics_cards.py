import streamlit as st
from config import settings

def render_metric_card(label, value, delta=None, border_color="#00D4FF", bg_glow="rgba(0, 212, 255, 0.05)"):
    """
    Renders a custom HTML metric card with a colored accent border, large text, and optional change values.
    """
    delta_html = ""
    if delta:
        color = "#00CC66" if not delta.startswith("-") else "#FF4444"
        delta_html = f'<div style="font-size: 0.85rem; font-weight: 600; color: {color}; margin-top: 4px;">{delta}</div>'
        
    card_html = f"""
    <div style="
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid #30363D;
        border-top: 4px solid {border_color};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    ">
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #8B949E; font-weight: 600;">{label}</div>
        <div style="font-size: 2rem; font-weight: 800; font-family: 'Space Grotesk', sans-serif; color: {border_color}; margin-top: 8px; line-height: 1.1;">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_kpi_row(subjects=56, sentences=30, accuracy="82.4%", chance="3.3%"):
    """
    Helper to render a row of metric cards on the Home or Performance page.
    """
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Research Subjects", str(subjects), delta="60 Sessions Total", border_color="#00D4FF")
    with col2:
        render_metric_card("Spanish Sentences", str(sentences), delta="30 Classes (Daily Use)", border_color="#9D4EDD")
    with col3:
        render_metric_card("Decoding Accuracy", accuracy, delta="+79.1% Over Chance", border_color="#00FF9F")
    with col4:
        render_metric_card("Baseline Chance", chance, delta="30-class Uniform", border_color="#8B949E")
