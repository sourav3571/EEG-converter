import numpy as np
import plotly.graph_objects as go
from config import settings

def plot_eeg_waveforms(eeg_data, fs=250.0, scaling_factor=1.0, title="EEG Waveform Viewer"):
    """
    Plots stacked multi-channel EEG signals using Plotly.
    eeg_data shape: (channels, timepoints) -> (14, 750)
    scaling_factor: multiplier for scaling signal amplitudes (helpful to control overlap)
    """
    n_channels, n_samples = eeg_data.shape
    time = np.linspace(0, settings.TRIAL_DURATION, n_samples)
    
    # Calculate spacing based on maximum signal amplitude
    max_amp = np.max(np.abs(eeg_data))
    spacing = max_amp * 1.5 * scaling_factor
    if spacing == 0:
        spacing = 10.0
        
    fig = go.Figure()
    
    # Iterate in reverse order so the first channels (e.g. F7) appear at the top
    for ch_idx in range(n_channels - 1, -1, -1):
        ch_name = settings.CHANNELS[ch_idx]
        region = settings.CHANNEL_REGIONS[ch_name]
        color = settings.REGION_COLORS[region]
        
        # Calculate Y-offset
        y_offset = ch_idx * spacing
        # Apply scaling and offset
        y_signal = eeg_data[ch_idx] * scaling_factor + y_offset
        
        # Add trace
        fig.add_trace(go.Scatter(
            x=time,
            y=y_signal,
            mode='lines',
            name=ch_name,
            line=dict(color=color, width=1.5),
            hoverinfo='text',
            text=[f"Channel: {ch_name}<br>Region: {region}<br>Time: {t:.3f}s<br>Amp: {val:.2f} µV" 
                  for t, val in zip(time, eeg_data[ch_idx])],
            legendgroup=region,
            showlegend=(ch_name in ['F7', 'FT7', 'FC5', 'T7', 'C5', 'TP7', 'CP5', 'P7']) # Show one legend item per region
        ))
        
    # Configure custom Y-axis ticks
    tick_vals = [i * spacing for i in range(n_channels)]
    tick_text = settings.CHANNELS
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=14, family="JetBrains Mono", color="#C4FF3D")
        ),
        xaxis=dict(
            title=dict(
                text="Time (seconds)",
                font=dict(color="#8B949E", family="JetBrains Mono", size=10)
            ),
            gridcolor="#1F1F1F",
            linecolor="#2A2A2A",
            tickfont=dict(color="#8B949E", family="JetBrains Mono")
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_text,
            gridcolor="#1F1F1F",
            linecolor="#2A2A2A",
            tickfont=dict(color="#FFFFFF", size=11, family="JetBrains Mono"),
            zeroline=False
        ),
        plot_bgcolor="#0A0A0A",
        paper_bgcolor="#0A0A0A",
        height=520,
        margin=dict(l=60, r=20, t=50, b=50),
        hovermode='closest',
        legend=dict(
            title=dict(text="Brain Regions", font=dict(color="#FFFFFF", family="JetBrains Mono", size=10)),
            font=dict(color="#8B949E", size=9, family="Inter"),
            bgcolor="rgba(10, 10, 10, 0.8)",
            bordercolor="var(--border-default)",
            borderwidth=1,
            x=1.02,
            y=1.0
        )
    )
    
    # Add vertical reference lines for trial sections (onset is at 0s, duration is 3s)
    fig.add_vline(x=0.0, line_width=1.5, line_dash="dash", line_color="#C4FF3D", annotation_text="Stimulus Onset", annotation_font=dict(family="JetBrains Mono", size=10, color="#C4FF3D"))
    
    return fig
