export default function AboutPage() {
  const sections = [
    {
      tag: '[01] OVERVIEW',
      title: 'Project Synopsis',
      body: `This project implements a Brain-Computer Interface (BCI) for decoding imagined Spanish speech from left-hemisphere EEG signals. Using the publicly available ds004279 dataset (OpenNeuro BIDS format), we demonstrate that a compact EEGNet architecture can classify 30 distinct imagined Spanish sentences with 82.4% accuracy — 79.1 percentage points above chance.`,
    },
    {
      tag: '[02] DATASET',
      title: 'ds004279 — Spanish Imagined Speech',
      body: `56 participants performed auditory perception and silent production tasks of 30 Spanish phrases. EEG was recorded at 250 Hz across 64 electrodes; 14 left-hemisphere language-lateralized channels (F7, F5, F3, FT7, FC5, FC3, T7, C5, C3, TP7, CP5, CP3, P7, P3) were selected for decoding. Data is stored in a 4.5 GB NPZ cache.`,
    },
    {
      tag: '[03] MODEL',
      title: 'EEGNet Architecture',
      body: `EEGNet is a compact CNN specifically designed for EEG-based BCIs. It uses depthwise and separable convolutions to capture channel-specific temporal dynamics with minimal parameters. Models are trained per-subject (eegnet_subj_{id}_stims2.pth) and as mixed-subject ensembles. The contrastive variant projects the EEG embedding into the 384-dimensional multilingual SentenceTransformer space.`,
    },
    {
      tag: '[04] PIPELINE',
      title: 'Preprocessing Pipeline',
      body: `1. Band-pass Butterworth filter (2–50 Hz)\n2. ICA-based artefact removal (eye-blink & movement)\n3. Common Average Reference (CAR)\n4. Epoch extraction: 3 s windows (750 timepoints)\n5. Z-score normalisation per channel`,
    },
    {
      tag: '[05] DEPLOYMENT',
      title: 'Architecture',
      body: `Backend: FastAPI server running in a Docker container on Hugging Face Spaces. The 4.5 GB EEG dataset and 61 PyTorch model weights are downloaded from the HF Model repo at build time.\n\nFrontend: React (Vite) single-page application deployed on Vercel. It communicates with the backend via REST API endpoints exposed at port 7860.`,
    },
  ];

  return (
    <div>
      <span className="section-marker">[06] ABOUT & DOCS</span>
      <h1 style={{ fontSize: '1.8rem', marginBottom: 6 }}>Methodology & Documentation</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 36 }}>
        Full technical breakdown of the dataset, architecture, preprocessing pipeline, and deployment stack.
      </p>

      {sections.map(({ tag, title, body }) => (
        <div key={tag} className="glass-card">
          <span className="section-marker" style={{ marginBottom: 6 }}>{tag}</span>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 12 }}>{title}</h2>
          <p style={{ fontSize: 13.5, color: 'var(--text-light)', lineHeight: 1.75, whiteSpace: 'pre-line' }}>{body}</p>
        </div>
      ))}

      {/* Links */}
      <div className="glass-card">
        <span className="section-marker" style={{ marginBottom: 10 }}>[07] LINKS</span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          {[
            { label: 'OpenNeuro ds004279', href: 'https://openneuro.org/datasets/ds004279' },
            { label: 'HF Spaces (Backend)', href: 'https://huggingface.co/spaces/souravbehera3571/eeg-spanish-speech-decoder' },
            { label: 'HF Model Repo (Weights)', href: 'https://huggingface.co/souravbehera3571/eeg-spanish-speech-decoder-data' },
            { label: 'EEGNet Paper', href: 'https://arxiv.org/abs/1611.08024' },
          ].map(({ label, href }) => (
            <a key={label} href={href} target="_blank" rel="noopener noreferrer"
              style={{
                fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--accent)',
                border: '1px solid rgba(91,157,249,0.25)', borderRadius: 4, padding: '6px 12px',
                textDecoration: 'none', transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.target.style.background = 'rgba(91,157,249,0.08)'; }}
              onMouseLeave={e => { e.target.style.background = 'transparent'; }}>
              ↗ {label}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
