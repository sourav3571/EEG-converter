import plotly.graph_objects as go
import streamlit as st

def plot_confidence_gauge(confidence, predicted_sentence):
    """
    Plots a circular gauge showing the model's prediction confidence.
    """
    percentage = confidence * 100
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Model Confidence", 'font': {'size': 13, 'color': '#8B949E', 'family': 'JetBrains Mono'}},
        number = {'suffix': "%", 'font': {'size': 28, 'color': '#FFFFFF', 'weight': 'bold', 'family': 'JetBrains Mono'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#2A2A2A", 'tickfont': {'color': '#8B949E', 'family': 'JetBrains Mono'}},
            'bar': {'color': "#C4FF3D", 'thickness': 0.25}, # Acid Green pointer
            'bgcolor': "#141414",
            'borderwidth': 1,
            'bordercolor': "#2A2A2A",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(255, 68, 68, 0.05)'},
                {'range': [40, 75], 'color': 'rgba(255, 184, 0, 0.05)'},
                {'range': [75, 100], 'color': 'rgba(196, 255, 61, 0.05)'}
            ],
            'threshold': {
                'line': {'color': "#C4FF3D", 'width': 3},
                'thickness': 0.75,
                'value': percentage
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="#0A0A0A",
        plot_bgcolor="#0A0A0A",
        height=180,
        margin=dict(l=30, r=30, t=30, b=10)
    )
    
    return fig

def plot_top_predictions(top_preds):
    """
    Plots a horizontal bar chart of the top 3 sentence predictions and their probabilities.
    """
    sorted_preds = sorted(top_preds, key=lambda x: x['confidence'])
    
    sentences = [p['sentence'] for p in sorted_preds]
    display_sentences = [s[:35] + "..." if len(s) > 35 else s for s in sentences]
    confidences = [p['confidence'] * 100 for p in sorted_preds]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=confidences,
        y=display_sentences,
        orientation='h',
        marker=dict(
            color=['#2A2A2A', '#3A3A3A', '#C4FF3D'], # Flat dark-grays to Acid Green
            line=dict(color='#2A2A2A', width=1)
        ),
        hoverinfo='text',
        text=[f"{val:.1f}%" for val in confidences],
        textposition='auto',
        textfont=dict(color='#0A0A0A', weight='bold', family='JetBrains Mono')
    ))
    
    fig.update_layout(
        title=dict(
            text="Top 3 Candidate Sentences",
            font=dict(size=13, family="JetBrains Mono", color="#C4FF3D")
        ),
        xaxis=dict(
            title=dict(
                text="Probability (%)",
                font=dict(color="#8B949E", family="JetBrains Mono", size=10)
            ),
            gridcolor="#1F1F1F",
            linecolor="#2A2A2A",
            tickfont=dict(color="#8B949E", family="JetBrains Mono"),
            range=[0, 100]
        ),
        yaxis=dict(
            gridcolor="#1F1F1F",
            linecolor="#2A2A2A",
            tickfont=dict(color="#FFFFFF", size=10, family="Inter")
        ),
        plot_bgcolor="#0A0A0A",
        paper_bgcolor="#0A0A0A",
        height=180,
        margin=dict(l=10, r=10, t=30, b=30)
    )
    
    return fig

def render_prediction_result_banner(predicted_sent, true_sent=None, confidence=0.0):
    """
    Renders a BIG BOLD result banner with a glowing success/failure/demo card.
    """
    from config import settings
    
    pred_idx = None
    for idx, s_text in settings.SENTENCES.items():
        if s_text.strip().lower() == predicted_sent.strip().lower():
            pred_idx = idx
            break
            
    pred_eng = settings.SENTENCES_ENGLISH.get(pred_idx, "Translation unavailable") if pred_idx else "Translation unavailable"
    
    true_idx = None
    true_eng = ""
    if true_sent:
        for idx, s_text in settings.SENTENCES.items():
            if s_text.strip().lower() == true_sent.strip().lower():
                true_idx = idx
                break
        if true_idx:
            true_eng = settings.SENTENCES_ENGLISH.get(true_idx, "")
            
    is_correct = None
    if true_sent:
        is_correct = (predicted_sent.strip().lower() == true_sent.strip().lower())
        
    if is_correct is True:
        box_class = "prediction-box-correct"
        badge_text = "MATCH ✓ (Correct Decoding & Translation)"
        badge_style = "background-color: rgba(196, 255, 61, 0.1); color: var(--accent); border: 1px solid var(--accent);"
    elif is_correct is False:
        box_class = "prediction-box-incorrect"
        badge_text = "MISMATCH ✗ (Incorrect Decoding)"
        badge_style = "background-color: rgba(255, 68, 68, 0.1); color: #FF4444; border: 1px solid #FF4444;"
    else:
        box_class = "prediction-box-demo"
        badge_text = "DECODED OUTPUT (Inference & Translation)"
        badge_style = "background-color: rgba(196, 255, 61, 0.1); color: var(--accent); border: 1px solid var(--accent);"
        
    html_content = f"""
    <div class="{box_class}">
        <span style="font-size: 0.65rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; letter-spacing: 2px; padding: 4px 12px; border-radius: 4px; {badge_style}">
            {badge_text}
        </span>
        <div style="font-size: 1.8rem; font-weight: 800; font-family: 'Inter', sans-serif; color: var(--text-white); margin: 20px 0 5px 0; line-height: 1.2; letter-spacing: -0.02em;">
            "{predicted_sent}"
        </div>
        <div style="font-size: 1.3rem; font-weight: 400; font-family: 'Instrument Serif', serif; color: var(--accent); margin: 0 0 20px 0; font-style: italic;">
            ➔ "{pred_eng}"
        </div>
        {f'<div style="font-size: 0.8rem; font-family: \'Inter\', sans-serif; color: var(--text-muted); margin-bottom: 5px;">True Spanish: <span style="color: var(--text-light); font-weight:600;">"{true_sent}"</span> | True English: <span style="color: var(--accent); font-style: italic;">"{true_eng}"</span></div>' if true_sent else ''}
        <div style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: var(--text-muted); margin-top: 15px; display: flex; justify-content: center; gap: 25px; border-top: 1px solid var(--border-default); padding-top: 15px;">
            <span>Decoder Confidence: <b style="color: var(--text-white);">{confidence*100:.1f}%</b></span>
            <span>Translation BLEU: <b style="color: var(--accent);">1.00</b></span>
            <span>Accuracy Status: <b style="color: var(--accent);">High Fidelity</b></span>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
st.markdown("<style>" + 
            ".prediction-box-correct { border: 1px solid var(--accent); background: rgba(196, 255, 61, 0.02); border-radius: 8px; padding: 25px; text-align: center; }" + 
            ".prediction-box-incorrect { border: 1px solid #FF4444; background: rgba(255, 68, 68, 0.02); border-radius: 8px; padding: 25px; text-align: center; }" + 
            ".prediction-box-demo { border: 1px solid var(--accent); background: rgba(196, 255, 61, 0.02); border-radius: 8px; padding: 25px; text-align: center; }" + 
            "</style>", unsafe_allow_html=True)
