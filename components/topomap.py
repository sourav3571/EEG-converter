import numpy as np
import scipy.interpolate as interpolate
import plotly.graph_objects as go
from config import settings

# Approximate 2D coordinates (x, y) for 14 left-hemisphere language channels
# Projected on a unit circle where x is Left(-) to Right(+), y is Posterior(-) to Anterior(+)
CHANNEL_COORDS = {
    'F7':  (-0.707,  0.350),
    'F5':  (-0.520,  0.500),
    'F3':  (-0.350,  0.650),
    'FT7': (-0.850,  0.150),
    'FC5': (-0.600,  0.220),
    'T7':  (-0.950,  0.000),
    'C5':  (-0.700,  0.000),
    'C3':  (-0.450,  0.000),
    'TP7': (-0.850, -0.150),
    'CP5': (-0.600, -0.220),
    'CP3': (-0.450, -0.220),
    'P7':  (-0.707, -0.350),
    'P5':  (-0.520, -0.500),
    'P3':  (-0.350, -0.650)
}

def interpolate_scalp_grid(channels, values, grid_size=100):
    """
    Interpolates sparse electrode values onto a regular 2D grid for contour plotting.
    Filters out grid points outside the circular head boundary (r > 1.0).
    """
    # Extract coordinates
    coords = np.array([CHANNEL_COORDS[ch] for ch in channels])
    
    # Create grid
    xi = np.linspace(-1.1, 1.1, grid_size)
    yi = np.linspace(-1.1, 1.1, grid_size)
    X, Y = np.meshgrid(xi, yi)
    
    # Radial distance from center (for head boundary masking)
    R = np.sqrt(X**2 + Y**2)
    
    # Perform cubic interpolation (fallback to linear if cubic fails due to geometry)
    try:
        zi = interpolate.griddata(coords, values, (X, Y), method='cubic')
    except Exception:
        zi = interpolate.griddata(coords, values, (X, Y), method='linear')
        
    # Mask values outside the head boundary (radius = 1.0)
    zi[R > 1.0] = np.nan
    
    return xi, yi, zi

def draw_head_outline(fig):
    """
    Adds head circle, nose, and ears drawings to a Plotly figure.
    """
    # 1. Main Head Circle (Radius = 1.0)
    fig.add_shape(type="circle",
        xref="x", yref="y",
        x0=-1.0, y0=-1.0, x1=1.0, y1=1.0,
        line=dict(color="#333333", width=2.0)
    )
    
    # 2. Nose (triangle at the top: y around 1.0 to 1.1)
    fig.add_shape(type="path",
        xref="x", yref="y",
        path="M -0.1 1.0 L 0 1.15 L 0.1 1.0 Z",
        fillcolor="#0A0A0A",
        line=dict(color="#333333", width=2.0)
    )
    
    # 3. Left Ear (arc/semi-ellipse on the left side: x around -1.0)
    fig.add_shape(type="path",
        xref="x", yref="y",
        path="M -1.0 0.15 C -1.1 0.1, -1.1 -0.1, -1.0 -0.15",
        line=dict(color="#333333", width=1.5)
    )
    
    # 4. Right Ear (arc/semi-ellipse on the right side: x around 1.0)
    fig.add_shape(type="path",
        xref="x", yref="y",
        path="M 1.0 0.15 C 1.1 0.1, 1.1 -0.1, 1.0 -0.15",
        line=dict(color="#333333", width=1.5)
    )
    
    return fig
 
def plot_topomap(channels, values, title="Brain Topography Map", value_range=None):
    """
    Creates a beautiful 2D scalp topography plot with color contour mapping.
    """
    xi, yi, zi = interpolate_scalp_grid(channels, values)
    
    # Auto-calculate symmetric color scale range based on values if not specified
    if value_range is None:
        max_val = max(1.0, np.max(np.abs(values)))
        value_range = [-max_val, max_val]
        
    fig = go.Figure()
    
    # 1. Add the interpolated contour map
    fig.add_trace(go.Contour(
        x=xi,
        y=yi,
        z=zi,
        colorscale='RdBu_r', # Red is positive amplitude, Blue is negative
        zmin=value_range[0],
        zmax=value_range[1],
        line=dict(width=0.5, color='rgba(255,255,255,0.15)'),
        contours=dict(showlabels=False),
        colorbar=dict(
            title=dict(
                text="Amplitude (µV)",
                side="right",
                font=dict(color="#8B949E", size=9, family="JetBrains Mono")
            ),
            tickfont=dict(color="#8B949E", size=8, family="JetBrains Mono"),
            thickness=12,
            len=0.75
        ),
        hoverinfo='none',
        showscale=True
    ))
    
    # 2. Add head shape outlines
    fig = draw_head_outline(fig)
    
    # 3. Add electrode positions as scatter dots
    coords_x = [CHANNEL_COORDS[ch][0] for ch in channels]
    coords_y = [CHANNEL_COORDS[ch][1] for ch in channels]
    
    fig.add_trace(go.Scatter(
        x=coords_x,
        y=coords_y,
        mode='markers+text',
        marker=dict(size=7, color='#0A0A0A', line=dict(width=1.5, color='#C4FF3D')),
        text=channels,
        textposition="top center",
        textfont=dict(size=8, color='#FFFFFF', weight='bold', family="JetBrains Mono"),
        name="Electrodes",
        hoverinfo='text',
        texttemplate='%{text}', # Shows electrode label on chart
        hovertext=[f"Electrode: {ch}<br>Voltage: {val:.2f} µV<br>Region: {settings.CHANNEL_REGIONS[ch]}" 
                   for ch, val in zip(channels, values)]
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=12, family="JetBrains Mono", color="#C4FF3D"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.3, 1.3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.3, 1.3]),
        plot_bgcolor="#0A0A0A",
        paper_bgcolor="#0A0A0A",
        width=380,
        height=380,
        margin=dict(l=10, r=10, t=45, b=10),
        showlegend=False
    )
    
    return fig
