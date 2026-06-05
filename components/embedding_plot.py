import numpy as np
import plotly.graph_objects as go
from config import settings

def plot_tsne_embeddings(n_trials_per_sentence=10, seed=42):
    """
    Generates and plots a simulated t-SNE embedding space of EEG trials.
    Points are clustered around sentence centroids to show semantic grouping.
    """
    np.random.seed(seed)
    
    # Define 30 centroids in a 2D space (using a spiral or circle to separate them nicely)
    n_classes = 30
    angles = np.linspace(0, 4 * np.pi, n_classes)
    radii = np.linspace(2, 8, n_classes)
    centroids_x = radii * np.cos(angles)
    centroids_y = radii * np.sin(angles)
    
    x_data = []
    y_data = []
    labels = []
    sentence_texts = []
    hover_texts = []
    subjects = []
    
    # Generate points around each centroid
    for i in range(n_classes):
        sent_id = i + 1
        sent_text = settings.SENTENCES[sent_id]
        cx, cy = centroids_x[i], centroids_y[i]
        
        # Add random scatter (lower variance = tight clusters, higher = overlapping)
        # We use moderate variance to make it look realistic (some overlapping, some distinct)
        spread = 0.8
        xs = np.random.normal(cx, spread, n_trials_per_sentence)
        ys = np.random.normal(cy, spread, n_trials_per_sentence)
        
        for trial in range(n_trials_per_sentence):
            x_data.append(xs[trial])
            y_data.append(ys[trial])
            labels.append(f"Sentence {sent_id}")
            sentence_texts.append(sent_text)
            sub = np.random.choice(settings.SUBJECTS)
            subjects.append(sub)
            
            txt = (f"<b>Class:</b> {sent_id}<br>"
                   f"<b>Sentence:</b> {sent_text}<br>"
                   f"<b>Subject:</b> {sub}<br>"
                   f"<b>Trial:</b> Run #{trial+1}<br>"
                   f"<b>t-SNE X:</b> {xs[trial]:.2f}<br>"
                   f"<b>t-SNE Y:</b> {ys[trial]:.2f}")
            hover_texts.append(txt)
            
    fig = go.Figure()
    
    # Plot points using a continuous color scale but distinct classes
    # To avoid having 30 legend items cluttering the UI, we group them
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        marker=dict(
            size=7,
            color=np.repeat(np.arange(n_classes), n_trials_per_sentence),
            colorscale='Rainbow',
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Sentence Class ID",
                    font=dict(color="#8B949E", size=10)
                ),
                tickvals=list(range(0, 30, 5)),
                ticktext=[f"S{i+1}" for i in range(0, 30, 5)],
                tickfont=dict(color="#8B949E")
            ),
            line=dict(width=0.5, color='rgba(0,0,0,0.5)')
        ),
        text=hover_texts,
        hoverinfo='text',
        name="EEG Trials"
    ))
    
    # Add a few representative annotations to help supervisors understand the space
    for ann_idx in [1, 11, 23]:
        sent_text = settings.SENTENCES[ann_idx]
        short_text = sent_text[:20] + "..." if len(sent_text) > 20 else sent_text
        fig.add_annotation(
            x=centroids_x[ann_idx-1],
            y=centroids_y[ann_idx-1] + 1.2,
            text=f"Class {ann_idx}: '{short_text}'",
            showarrow=True,
            arrowhead=1,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="#E6EDF3",
            font=dict(color="#00D4FF", size=9),
            bgcolor="rgba(22, 27, 34, 0.9)",
            bordercolor="#30363D",
            borderwidth=1
        )
        
    fig.update_layout(
        title=dict(
            text="t-SNE Clustering of EEG Latent Representations",
            font=dict(size=18, family="Space Grotesk", color="#00D4FF")
        ),
        xaxis=dict(
            title=dict(
                text="t-SNE Dimension 1",
                font=dict(color="#E6EDF3")
            ),
            gridcolor="#21262D",
            linecolor="#30363D",
            tickfont=dict(color="#8B949E")
        ),
        yaxis=dict(
            title=dict(
                text="t-SNE Dimension 2",
                font=dict(color="#E6EDF3")
            ),
            gridcolor="#21262D",
            linecolor="#30363D",
            tickfont=dict(color="#8B949E")
        ),
        plot_bgcolor="#0D1117",
        paper_bgcolor="#0D1117",
        height=550,
        margin=dict(l=50, r=20, t=50, b=50),
        hovermode='closest'
    )
    
    return fig
