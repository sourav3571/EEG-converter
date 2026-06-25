import matplotlib.pyplot as plt
import numpy as np

def generate_timeline():
    fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
    ax.set_xlim(1920, 2030)
    ax.set_ylim(-1, 1)
    
    # Draw timeline axis line
    ax.axhline(0, color='black', lw=2, zorder=1)
    
    milestones = [
        (1924, "Hans Berger\nFirst EEG", 0.3),
        (1973, "Jacques Vidal\nBCI Framework", -0.5),
        (2018, "Lawhern et al.\nEEGNet", 0.4),
        (2024, "Valle et al.\nds004279 cross-sub", -0.4)
    ]
    
    for year, text, offset in milestones:
        # Draw point
        ax.scatter(year, 0, color='darkblue', s=80, zorder=2)
        # Draw line to label
        ax.plot([year, year], [0, offset], color='gray', linestyle='--', lw=1, zorder=1)
        # Add text
        align = 'bottom' if offset > 0 else 'top'
        ax.text(year, offset + (0.05 if offset > 0 else -0.05), f"**{year}**\n{text}", 
                ha='center', va=align, fontsize=8, color='black', weight='bold',
                bbox=dict(boxstyle="round,pad=0.3", fc="aliceblue", ec="darkblue", lw=0.5))
        
    ax.get_xaxis().set_major_formatter(plt.FormatStrFormatter('%g'))
    ax.set_xticks([1924, 1950, 1973, 2000, 2018, 2024])
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='x', labelsize=8)
    
    plt.tight_layout()
    plt.savefig('eeg_timeline.png', bbox_inches='tight')
    plt.close()

def generate_eegnet_flow():
    fig, ax = plt.subplots(figsize=(8, 2.5), dpi=150)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 10)
    
    blocks = [
        (5, 2.5, 15, 5, "Input EEG\n1 x 14 x 750", "lavender"),
        (25, 2.5, 15, 5, "Temporal Conv\n8 filters\n1 x 125", "lightyellow"),
        (45, 2.5, 15, 5, "Spatial Depthwise\nD=2\n14 x 1", "lightcyan"),
        (65, 2.5, 15, 5, "Separable Conv\n16 filters\n1 x 16", "honeydew"),
        (85, 2.5, 12, 5, "Classifier\nSoftmax\nN=5 classes", "mistyrose")
    ]
    
    for x, y, w, h, text, color in blocks:
        # Draw box
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='darkblue', lw=1.5, zorder=2)
        ax.add_patch(rect)
        # Add text
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=7, color='black', weight='bold')
        
    # Draw arrows
    for i in range(len(blocks) - 1):
        x1 = blocks[i][0] + blocks[i][2]
        x2 = blocks[i+1][0]
        y = 5.0
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", lw=2, color='darkblue', shrinkA=2, shrinkB=2))
        
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('eegnet_flow.png', bbox_inches='tight')
    plt.close()

def generate_performance_scaling():
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
    classes = [2, 5, 30]
    
    dep_acc = [83.5, 55.0, 18.5]
    indep_acc = [68.0, 36.5, 9.2]
    chance = [50.0, 20.0, 3.3]
    
    ax.plot(classes, dep_acc, marker='o', lw=2, color='darkgreen', label='Subject-Dependent')
    ax.plot(classes, indep_acc, marker='s', lw=2, color='darkblue', label='Subject-Independent')
    ax.plot(classes, chance, '--', color='red', lw=1.5, label='Chance Level')
    
    for x, y in zip(classes, dep_acc):
        ax.annotate(f"{y}%", (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8, weight='bold', color='darkgreen')
    for x, y in zip(classes, indep_acc):
        ax.annotate(f"{y}%", (x, y), textcoords="offset points", xytext=(0,-12), ha='center', fontsize=8, weight='bold', color='darkblue')
    for x, y in zip(classes, chance):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(12,-3), ha='left', fontsize=7, style='italic', color='red')

    ax.set_xscale('log')
    ax.set_xticks(classes)
    ax.get_xaxis().set_major_formatter(plt.FormatStrFormatter('%g'))
    ax.set_xlabel("Number of Sentence Classes", fontsize=9, weight='bold')
    ax.set_ylabel("Classification Accuracy (%)", fontsize=9, weight='bold')
    ax.set_title("Decoding Performance vs. Number of Sentence Classes", fontsize=10, weight='bold', pad=10)
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend(fontsize=8, loc='upper right')
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('performance_scaling.png', bbox_inches='tight')
    plt.close()

def generate_preprocessing_flow():
    fig, ax = plt.subplots(figsize=(8, 2.2), dpi=150)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 10)
    
    steps = [
        (5, 2.5, 16, 5, "Raw Scalp EEG\n64 Chans @ 500 Hz", "lightblue"),
        (26, 2.5, 16, 5, "Butterworth Bandpass\n2 Hz - 50 Hz", "lightyellow"),
        (47, 2.5, 16, 5, "Infomax ICA\n45 Components", "lightcyan"),
        (68, 2.5, 16, 5, "MNE-ICA Label\nConfidence >= 95%", "honeydew"),
        (89, 2.5, 8, 5, "Clean EEG\nEpochs", "lavender")
    ]
    
    for x, y, w, h, text, color in steps:
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='darkblue', lw=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=7.5, color='black', weight='bold')
        
    for i in range(len(steps) - 1):
        x1 = steps[i][0] + steps[i][2]
        x2 = steps[i+1][0]
        y = 5.0
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", lw=2, color='darkblue', shrinkA=2, shrinkB=2))
        
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('preprocessing_flow.png', bbox_inches='tight')
    plt.close()

def generate_sensor_layout():
    fig, ax = plt.subplots(figsize=(4.5, 4.5), dpi=150)
    
    # Head outline circle
    head = plt.Circle((0, 0), 1.0, color='aliceblue', ec='darkblue', lw=2, fill=True, zorder=1)
    ax.add_patch(head)
    
    # Nose
    ax.plot([-0.1, 0, 0.1], [1.0, 1.1, 1.0], color='darkblue', lw=2)
    # Ears
    ax.plot([-1.0, -1.05, -1.0], [0.1, 0, -0.1], color='darkblue', lw=2)
    ax.plot([1.0, 1.05, 1.0], [0.1, 0, -0.1], color='darkblue', lw=2)
    
    # Highlighted channels (Broca's & Wernicke's)
    highlighted = {
        'F3': (-0.4, 0.5, 'Broca'), 'F5': (-0.6, 0.45, 'Broca'), 'F7': (-0.8, 0.35, 'Broca'),
        'T7': (-0.9, -0.1, 'Wernicke'), 'FT7': (-0.85, 0.15, 'Wernicke'), 'FC5': (-0.65, 0.2, 'Wernicke')
    }
    
    # Other random channels for context
    context_chans = [
        ('Fz', (0, 0.6)), ('Cz', (0, 0)), ('Pz', (0, -0.6)), ('O1', (-0.3, -0.85)), ('O2', (0.3, -0.85)),
        ('F4', (0.4, 0.5)), ('C3', (-0.45, 0)), ('C4', (0.45, 0)), ('P3', (-0.4, -0.5)), ('P4', (0.4, -0.5)),
        ('T8', (0.9, -0.1)), ('F8', (0.8, 0.35))
    ]
    
    for name, (x, y) in context_chans:
        ax.scatter(x, y, color='white', edgecolor='gray', s=100, zorder=2)
        ax.text(x, y, name, ha='center', va='center', fontsize=6, color='gray', weight='bold')
        
    for name, (x, y, region) in highlighted.items():
        color = 'gold' if region == 'Broca' else 'lightgreen'
        ax.scatter(x, y, color=color, edgecolor='darkblue', s=150, zorder=3)
        ax.text(x, y, name, ha='center', va='center', fontsize=7, color='black', weight='bold')
        
    # Legend
    ax.scatter([], [], color='gold', edgecolor='darkblue', s=100, label="Broca's Area (Frontal)")
    ax.scatter([], [], color='lightgreen', edgecolor='darkblue', s=100, label="Wernicke's Area (Temporal)")
    ax.legend(loc='lower center', fontsize=7, framealpha=0.9)
    
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('sensor_layout.png', bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    generate_timeline()
    generate_eegnet_flow()
    generate_performance_scaling()
    generate_preprocessing_flow()
    generate_sensor_layout()
    print("Successfully generated all report plots!")
