import numpy as np
import plotly.graph_objects as go
from utils.feature_extractor import compute_spectrogram
from config import settings

def plot_spectrogram(channel_data, channel_name, fs=250.0):
    """
    Plots a time-frequency spectrogram for a single channel using Plotly Heatmap.
    channel_data shape: (timepoints,) -> (750,)
    """
    freqs, times, Sxx = compute_spectrogram(channel_data, fs=fs)
    
    # Convert spectrogram values to logarithmic scale (dB) for better dynamic range visualization
    Sxx_db = 10 * np.log10(Sxx + 1e-10)
    
    fig = go.Figure()
    
    # 1. Add spectrogram heatmap
    fig.add_trace(go.Heatmap(
        x=times,
        y=freqs,
        z=Sxx_db,
        colorscale='Plasma',
        colorbar=dict(
            title=dict(
                text="Power (dB)",
                side="right",
                font=dict(color="#8B949E", size=10)
            ),
            tickfont=dict(color="#8B949E")
        ),
        hoverinfo='text',
        text=[[f"Time: {t:.2f}s<br>Freq: {f:.1f}Hz<br>Power: {val:.1f} dB" 
               for t, val in zip(times, row)] for f, row in zip(freqs, Sxx_db)]
    ))
    
    # 2. Add horizontal lines for frequency band boundaries
    # Theta: 4-8Hz, Alpha: 8-13Hz, Beta: 13-30Hz, Gamma: 30-50Hz
    band_boundaries = [4.0, 8.0, 13.0, 30.0]
    band_names = {
        2.0: "Delta",
        6.0: "Theta",
        10.5: "Alpha",
        21.5: "Beta",
        40.0: "Gamma"
    }
    
    for boundary in band_boundaries:
        fig.add_hline(y=boundary, line_width=1.0, line_dash="dash", line_color="rgba(255, 255, 255, 0.3)")
        
    # Annotate frequency bands on the plot
    for y_pos, name in band_names.items():
        fig.add_annotation(
            x=0.05,
            y=y_pos,
            text=name,
            showarrow=False,
            font=dict(color="rgba(255, 255, 255, 0.6)", size=9),
            bgcolor="rgba(0, 0, 0, 0.5)",
            bordercolor="rgba(255, 255, 255, 0.2)",
            borderwidth=1,
            borderpad=2
        )
        
    # Add vertical line for stimulus onset (onset is 0.0s, the trial goes up to 3s)
    fig.add_vline(x=0.0, line_width=1.5, line_dash="dash", line_color="#FFB800", annotation_text="Onset")
    
    fig.update_layout(
        title=dict(
            text=f"Time-Frequency Spectrogram: Channel {channel_name}",
            font=dict(size=16, family="Space Grotesk", color="#00D4FF")
        ),
        xaxis=dict(
            title=dict(
                text="Time (seconds)",
                font=dict(color="#E6EDF3")
            ),
            gridcolor="#21262D",
            linecolor="#30363D",
            tickfont=dict(color="#8B949E")
        ),
        yaxis=dict(
            title=dict(
                text="Frequency (Hz)",
                font=dict(color="#E6EDF3")
            ),
            gridcolor="#21262D",
            linecolor="#30363D",
            tickfont=dict(color="#8B949E"),
            range=[0.5, 50.0]
        ),
        plot_bgcolor="#0D1117",
        paper_bgcolor="#0D1117",
        height=380,
        margin=dict(l=50, r=20, t=50, b=50)
    )
    
    return fig
