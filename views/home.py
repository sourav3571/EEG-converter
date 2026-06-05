import streamlit as st
from config import settings

def render():
    """
    Renders the custom premium agency-style Overview / Landing page.
    """
    # 1. Top navigation (Logo left, status indicator right)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-default); padding: 15px 0 25px 0; margin-bottom: 50px;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-white);">
            NEURODECODE <span style="color: var(--accent);">//</span> SPANISH DEC
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: var(--accent); animation: pulse 2s infinite ease-in-out;"></span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent);">BIDS DATASET ONLINE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Main Hero Layout Split (Left text columns, Right SVG artwork)
    col1, col2 = st.columns([1.3, 1.0])

    with col1:
        # Section Label
        st.markdown('<span class="section-marker">[01] EEG RESEARCH PLATFORM</span>', unsafe_allow_html=True)

        # Hero Heading with mixed typography & underlines
        st.markdown("""
        <h1 class="hero-display-sans" style="margin-bottom: 30px;">
            Decoding <span class="hero-display-italic">imagined</span> Spanish sentences from <span class="hero-display-italic">neural</span> signals.
        </h1>
        """, unsafe_allow_html=True)

        # Editorial Tagline Description
        st.markdown("""
        <p style="font-size: 15px; line-height: 1.7; color: var(--text-light); margin-bottom: 40px; max-width: 540px; font-weight: 300;">
            A brain-computer interface research initiative correlating auditory perception and silent production tasks. By targetting 14 language-lateralized left-hemisphere channels, we translate cortical processes into english communication vectors.
        </p>
        """, unsafe_allow_html=True)

        # Action Buttons Row
        btn_cols = st.columns([1.1, 1.0])
        with btn_cols[0]:
            if st.button("Run Prediction Console"):
                st.session_state.active_page = "Model Prediction"
                st.rerun()
        with btn_cols[1]:
            # Second button styled inline or through class
            if st.button("View Methodology"):
                st.session_state.active_page = "About & Docs"
                st.rerun()

    with col2:
        # Right visual: Glowing animated SVG Neural/Electrode map
        svg_html = '<div class="brain-hero-visual"><svg class="brain-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M 50 15 C 20 15, 10 30, 10 50 C 10 70, 25 85, 45 85 C 48 85, 50 82, 50 80 C 50 82, 52 85, 55 85 C 75 85, 90 70, 90 50 C 90 30, 80 15, 50 15 Z" fill="none" stroke="#2A2A2A" stroke-width="1" /><path d="M 50 15 C 40 25, 42 75, 50 80" fill="none" stroke="#1F1F1F" stroke-width="0.8" /><path d="M 25 40 Q 35 45 42 55" fill="none" stroke="var(--accent)" stroke-width="0.5" stroke-dasharray="1 1" opacity="0.6" /><path d="M 22 55 Q 33 60 48 65" fill="none" stroke="var(--accent)" stroke-width="0.5" stroke-dasharray="1 1" opacity="0.6" /><path d="M 30 70 Q 40 68 45 55" fill="none" stroke="var(--accent)" stroke-width="0.5" stroke-dasharray="1 1" opacity="0.6" /><circle class="electrode-dot" cx="25" cy="40" r="3" fill="var(--accent)" /><circle class="electrode-dot" cx="35" cy="35" r="3" fill="var(--accent)" style="animation-delay: 0.3s;" /><circle class="electrode-dot" cx="42" cy="45" r="3" fill="var(--accent)" style="animation-delay: 0.6s;" /><circle class="electrode-dot" cx="22" cy="55" r="3" fill="var(--accent)" style="animation-delay: 0.9s;" /><circle class="electrode-dot" cx="30" cy="58" r="3" fill="var(--accent)" style="animation-delay: 1.2s;" /><circle class="electrode-dot" cx="33" cy="68" r="3" fill="var(--accent)" style="animation-delay: 1.5s;" /><circle class="electrode-dot" cx="45" cy="55" r="3" fill="var(--accent)" style="animation-delay: 1.8s;" /><circle class="electrode-dot" cx="48" cy="65" r="3" fill="var(--accent)" style="animation-delay: 2.1s;" /><text x="18" y="38" font-family="monospace" font-size="2" fill="var(--text-muted)">F7</text><text x="36" y="31" font-family="monospace" font-size="2" fill="var(--text-muted)">F3</text><text x="16" y="55" font-family="monospace" font-size="2" fill="var(--text-muted)">FT7</text><text x="47" y="53" font-family="monospace" font-size="2" fill="var(--text-muted)">C3</text><text x="51" y="65" font-family="monospace" font-size="2" fill="var(--text-muted)">T7</text></svg></div>'
        st.markdown(svg_html, unsafe_allow_html=True)

    # 3. Bottom Row Credibility Stats Strip
    st.markdown("""
    <div class="stat-strip">
        <div class="stat-strip-item">
            ★ DECODER ACCURACY // <span>82.4%</span>
        </div>
        <div class="stat-strip-item">
            ★ ABOVE CHANCE // <span>+79.1%</span>
        </div>
        <div class="stat-strip-item">
            ★ COHORT SUBJECTS // <span>56 PARTICIPANTS</span>
        </div>
        <div class="stat-strip-item">
            ★ SIGNAL SOURCE // <span>14 LH CHANNELS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
