import numpy as np
import plotly.graph_objects as go
from config import settings

def plot_confusion_matrix(cm_data, normalize=False):
    """
    Plots an interactive 30x30 confusion matrix for Spanish sentences.
    cm_data: numpy array of shape (30, 30)
    """
    n_classes = cm_data.shape[0]
    
    if normalize:
        row_sums = cm_data.sum(axis=1, keepdims=True)
        # Avoid division by zero
        row_sums[row_sums == 0] = 1.0
        display_data = (cm_data / row_sums) * 100
        z_suffix = "%"
        colorscale = 'Viridis'
        zmin, zmax = 0, 100
    else:
        display_data = cm_data
        z_suffix = " trials"
        colorscale = 'Blues'
        zmin, zmax = 0, np.max(cm_data)
        
    labels_short = [f"S{i}" for i in range(1, n_classes + 1)]
    
    # Generate hover text
    hover_text = []
    for true_idx in range(n_classes):
        row_text = []
        for pred_idx in range(n_classes):
            true_sent = settings.SENTENCES[true_idx + 1]
            pred_sent = settings.SENTENCES[pred_idx + 1]
            val = display_data[true_idx, pred_idx]
            count = cm_data[true_idx, pred_idx]
            
            txt = (f"<b>True Sentence ({true_idx+1}):</b> {true_sent}<br>"
                   f"<b>Predicted Sentence ({pred_idx+1}):</b> {pred_sent}<br>"
                   f"<b>Value:</b> {val:.1f}{z_suffix}<br>"
                   f"<b>Raw Count:</b> {int(count)} trials")
            row_text.append(txt)
        hover_text.append(row_text)
        
    fig = go.Figure()
    
    fig.add_trace(go.Heatmap(
        x=labels_short,
        y=labels_short,
        z=display_data,
        colorscale=colorscale,
        zmin=zmin,
        zmax=zmax,
        hoverinfo='text',
        text=hover_text,
        colorbar=dict(
            title=dict(
                text="Accuracy" if normalize else "Counts",
                font=dict(color="#8B949E", size=10)
            ),
            tickfont=dict(color="#8B949E")
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="Interactive Confusion Matrix (30x30 Sentences)",
            font=dict(size=18, family="Space Grotesk", color="#00D4FF")
        ),
        xaxis=dict(
            title=dict(
                text="Predicted Sentence Index",
                font=dict(color="#E6EDF3")
            ),
            gridcolor="#21262D",
            linecolor="#30363D",
            tickfont=dict(color="#8B949E", size=9)
        ),
        yaxis=dict(
            title=dict(
                text="True Sentence Index",
                font=dict(color="#E6EDF3")
            ),
            gridcolor="#21262D",
            linecolor="#30363D",
            tickfont=dict(color="#8B949E", size=9),
            autorange="reversed" # Matrix diagonal goes from top-left to bottom-right
        ),
        plot_bgcolor="#0D1117",
        paper_bgcolor="#0D1117",
        height=650,
        width=700,
        margin=dict(l=50, r=20, t=50, b=50)
    )
    
    return fig
