import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Resolve parent directory to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings
from utils import data_loader, preprocessor

def main():
    print("Generating scientific visualization plots for EEG Dashboard...")
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets'))
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Generate Synthetic EEG signal
    raw_data = data_loader.generate_synthetic_eeg(seed=101, has_artifacts=True)
    t = np.linspace(0, settings.TRIAL_DURATION, raw_data.shape[1])

    # Plot 1: Raw EEG Signals (Multichannel stacked plot)
    plt.figure(figsize=(10, 6), facecolor='#151D30')
    ax = plt.axes()
    ax.set_facecolor('#0B0F19')
    offset = 40.0
    for i, ch_name in enumerate(settings.CHANNELS):
        plt.plot(t, raw_data[i] - i * offset, color='#3A86FF', alpha=0.85, linewidth=1.2)
        plt.text(-0.15, -i * offset, ch_name, color='#F8FAFC', fontname='sans-serif', fontsize=9, fontweight='bold', ha='right', va='center')
    
    plt.title("Multichannel Raw EEG Signals (14 Channels)", color='#F8FAFC', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel("Time (seconds)", color='#94A3B8', fontsize=11)
    plt.ylabel("Channels (relative offset)", color='#94A3B8', fontsize=11)
    ax.tick_params(colors='#64748B')
    ax.spines['bottom'].set_color('#24324F')
    ax.spines['left'].set_color('#24324F')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.grid(color='#24324F', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, 'raw_eeg_plot.png'), dpi=150, facecolor='#151D30')
    plt.close()
    print("Saved raw_eeg_plot.png")

    # Plot 2: PSD Analysis (Power Spectral Density)
    plt.figure(figsize=(10, 5), facecolor='#151D30')
    ax = plt.axes()
    ax.set_facecolor('#0B0F19')
    
    # Calculate simple PSD using FFT
    freqs = np.fft.rfftfreq(raw_data.shape[1], d=1.0/settings.SAMPLING_RATE)
    for i in range(5): # plot first 5 channels for clarity
        fft_vals = np.abs(np.fft.rfft(raw_data[i]))
        psd = (fft_vals ** 2) / (settings.SAMPLING_RATE * raw_data.shape[1])
        # Smooth PSD a bit
        psd_smooth = np.convolve(psd, np.ones(5)/5, mode='same')
        plt.semilogy(freqs[1:100], psd_smooth[1:100], alpha=0.8, linewidth=1.5, label=settings.CHANNELS[i])

    # Highlight bands
    plt.axvspan(4, 8, color='#C4FF3D', alpha=0.08, label='Theta (4-8 Hz)')
    plt.axvspan(8, 13, color='#06D6A0', alpha=0.08, label='Alpha (8-13 Hz)')
    plt.axvspan(13, 30, color='#FFD166', alpha=0.08, label='Beta (13-30 Hz)')

    plt.title("EEG Power Spectral Density (PSD)", color='#F8FAFC', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel("Frequency (Hz)", color='#94A3B8', fontsize=11)
    plt.ylabel("Power (uV²/Hz)", color='#94A3B8', fontsize=11)
    plt.legend(facecolor='#151D30', edgecolor='#24324F', labelcolor='#F8FAFC')
    ax.tick_params(colors='#64748B')
    ax.spines['bottom'].set_color('#24324F')
    ax.spines['left'].set_color('#24324F')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.grid(color='#24324F', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, 'psd_analysis.png'), dpi=150, facecolor='#151D30')
    plt.close()
    print("Saved psd_analysis.png")

    # Plot 3: 2D Brain Topography
    plt.figure(figsize=(6, 6), facecolor='#151D30')
    ax = plt.axes()
    ax.set_facecolor('#0B0F19')
    
    # Draw simple head outline
    circle = plt.Circle((0, 0), 1.0, color='#64748B', fill=False, linewidth=2)
    ax.add_patch(circle)
    # Nose
    plt.plot([-0.1, 0, 0.1], [1.0, 1.1, 1.0], color='#64748B', linewidth=2)
    # Ears
    circle_l = plt.Circle((-1.05, 0), 0.1, color='#64748B', fill=False, linewidth=1.5)
    circle_r = plt.Circle((1.05, 0), 0.1, color='#64748B', fill=False, linewidth=1.5)
    ax.add_patch(circle_l)
    ax.add_patch(circle_r)

    # Plot fake channel values
    # Standard 10-20 coordinate mock positions for 14 channels
    ch_positions = {
        'AF3': (-0.35, 0.7), 'AF4': (0.35, 0.7),
        'F7': (-0.75, 0.45), 'F5': (-0.45, 0.45), 'F3': (-0.3, 0.45), 'F4': (0.3, 0.45), 'F8': (0.75, 0.45),
        'FC5': (-0.55, 0.2), 'FC6': (0.55, 0.2),
        'T7': (-0.9, 0.0), 'T8': (0.9, 0.0),
        'P7': (-0.75, -0.45), 'P8': (0.75, -0.45),
        'O1': (-0.35, -0.85), 'O2': (0.35, -0.85)
    }

    x = []
    y = []
    val = []
    for ch in settings.CHANNELS:
        if ch in ch_positions:
            pos = ch_positions[ch]
            x.append(pos[0])
            y.append(pos[1])
            # generate voltage-like value
            val.append(np.sin(pos[0]*3) * np.cos(pos[1]*3) * 5.0)

    # Plot filled contour map
    grid_x, grid_y = np.mgrid[-1:1:100j, -1:1:100j]
    from scipy.interpolate import griddata
    grid_z = griddata((x, y), val, (grid_x, grid_y), method='cubic')
    # Mask out coordinates outside head circle
    mask = grid_x**2 + grid_y**2 > 0.98
    grid_z[mask] = np.nan

    cs = plt.contourf(grid_x, grid_y, grid_z, levels=15, cmap='RdYlBu_r', alpha=0.85)
    plt.colorbar(cs, label="Voltage (uV)", ax=ax).ax.yaxis.label.set_color('#94A3B8')
    
    # Plot channel positions
    plt.scatter(x, y, color='#F8FAFC', edgecolors='#0B0F19', s=40, zorder=5)
    for ch_name, pos in ch_positions.items():
        if ch_name in settings.CHANNELS:
            plt.text(pos[0], pos[1] - 0.08, ch_name, color='#F8FAFC', fontname='sans-serif', fontsize=7, fontweight='bold', ha='center', zorder=10)

    plt.title("Brain Topography Mapping (2D Scalp)", color='#F8FAFC', fontsize=12, pad=15, fontweight='bold')
    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, 'brain_topomap.png'), dpi=150, facecolor='#151D30')
    plt.close()
    print("Saved brain_topomap.png")

    # Plot 4: Model Confusion Matrix
    plt.figure(figsize=(6, 5), facecolor='#151D30')
    ax = plt.axes()
    ax.set_facecolor('#0B0F19')
    
    # Generate mock 5x5 confusion matrix
    cm = np.array([
        [0.82, 0.05, 0.03, 0.07, 0.03],
        [0.08, 0.76, 0.05, 0.06, 0.05],
        [0.04, 0.06, 0.88, 0.01, 0.01],
        [0.10, 0.05, 0.02, 0.79, 0.04],
        [0.05, 0.04, 0.01, 0.05, 0.85]
    ])
    
    im = plt.imshow(cm, cmap='Blues', vmin=0, vmax=1)
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.yaxis.label.set_color('#94A3B8')
    cbar.ax.tick_params(colors='#64748B')
    
    classes = [f"Sent {i+1}" for i in range(5)]
    plt.xticks(range(5), classes, color='#F8FAFC', fontsize=9)
    plt.yticks(range(5), classes, color='#F8FAFC', fontsize=9)
    
    # Add values on cells
    for i in range(5):
        for j in range(5):
            text_color = '#F8FAFC' if cm[i, j] > 0.5 else '#64748B'
            plt.text(j, i, f"{cm[i,j]*100:.1f}%", ha='center', va='center', color=text_color, fontname='sans-serif', fontweight='bold', fontsize=9)

    plt.title("Imagined Speech Decoder Confusion Matrix", color='#F8FAFC', fontsize=12, pad=15, fontweight='bold')
    plt.xlabel("Predicted Sentence", color='#94A3B8', fontsize=10)
    plt.ylabel("True Sentence", color='#94A3B8', fontsize=10)
    
    ax.spines['bottom'].set_color('#24324F')
    ax.spines['left'].set_color('#24324F')
    ax.spines['top'].set_color('#24324F')
    ax.spines['right'].set_color('#24324F')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, 'confusion_matrix.png'), dpi=150, facecolor='#151D30')
    plt.close()
    print("Saved confusion_matrix.png")
    
    print("All scientific visualization plots generated successfully!")

if __name__ == "__main__":
    main()
