import { Brain, Zap, Users, Radio, Waves } from 'lucide-react';

const STATS = [
  { value: '82.4%', label: 'Decoder Accuracy' },
  { value: '+32.4%', label: 'Above Chance' },
  { value: '56', label: 'Cohort Subjects' },
  { value: '14', label: 'LH Channels' },
];

// Animated SVG brain electrode map
function BrainMap() {
  return (
    <div style={{
      background: 'radial-gradient(circle, #19191B 0%, #0E0E0E 100%)',
      border: '1px solid var(--border-default)',
      borderRadius: 12,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      aspectRatio: '4/3', width: '100%', overflow: 'hidden',
    }}>
      <svg viewBox="0 0 100 100" style={{ width: '85%', height: '85%' }}>
        {/* Brain outline */}
        <path d="M 50 15 C 20 15, 10 30, 10 50 C 10 70, 25 85, 45 85 C 48 85, 50 82, 50 80 C 50 82, 52 85, 55 85 C 75 85, 90 70, 90 50 C 90 30, 80 15, 50 15 Z"
          fill="none" stroke="#222225" strokeWidth="1.2" />
        <path d="M 50 15 C 40 25, 42 75, 50 80" fill="none" stroke="#1F1F1F" strokeWidth="0.8" />
        {/* Left-hemi connection paths */}
        <path d="M 25 40 Q 35 45 42 55" fill="none" stroke="var(--accent)" strokeWidth="0.5" strokeDasharray="1 1" opacity="0.3" />
        <path d="M 22 55 Q 33 60 48 65" fill="none" stroke="var(--accent)" strokeWidth="0.5" strokeDasharray="1 1" opacity="0.3" />
        <path d="M 30 70 Q 40 68 45 55" fill="none" stroke="var(--accent)" strokeWidth="0.5" strokeDasharray="1 1" opacity="0.3" />
        {/* Electrode dots */}
        {[
          { cx: 25, cy: 40, delay: '0s', label: 'F7' },
          { cx: 35, cy: 35, delay: '0.3s', label: 'F3' },
          { cx: 42, cy: 45, delay: '0.6s', label: 'C3' },
          { cx: 22, cy: 55, delay: '0.9s', label: 'FT7' },
          { cx: 30, cy: 58, delay: '1.2s', label: 'FC5' },
          { cx: 33, cy: 68, delay: '1.5s', label: 'T7' },
          { cx: 45, cy: 55, delay: '1.8s', label: 'CP5' },
          { cx: 48, cy: 65, delay: '2.1s', label: 'TP7' },
        ].map(({ cx, cy, delay, label }) => (
          <g key={label}>
            <circle cx={cx} cy={cy} r={2.5} fill="var(--accent)"
              style={{ animation: `pulse 2.5s ${delay} infinite ease-in-out` }} />
            <text x={cx + 3.5} y={cy + 1} fontSize={2.5} fill="rgba(200,230,255,0.4)"
              fontFamily="JetBrains Mono, monospace">{label}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

export default function HomePage({ setActivePage }) {
  return (
    <div>
      {/* Top nav bar */}
      <div className="status-indicator-bar">
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 600, color: 'var(--text-white)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
          NEURODECODE <span style={{ color: 'var(--accent)' }}>//</span> SPANISH DEC
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="pulse-dot" />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            BIDS DATASET ONLINE
          </span>
        </div>
      </div>

      {/* Hero Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 40, marginBottom: 60 }}>
        <div>
          <span className="section-marker">[01] EEG RESEARCH PLATFORM</span>
          <h1 className="hero-display-sans" style={{ marginBottom: 28 }}>
            Decoding <span className="hero-display-italic">imagined</span> Spanish sentences from{' '}
            <span className="hero-display-italic">neural</span> signals.
          </h1>
          <p style={{ fontSize: 15, lineHeight: 1.75, color: 'var(--text-light)', marginBottom: 36, maxWidth: 520, fontWeight: 300 }}>
            A brain-computer interface research initiative correlating auditory perception and silent production tasks.
            By targeting 14 language-lateralized left-hemisphere channels, we translate cortical processes into
            communication vectors.
          </p>
          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn-primary" onClick={() => setActivePage('prediction')}>
              <Brain size={14} /> Run Prediction Console
            </button>
            <button onClick={() => setActivePage('about')}
              style={{ background: 'transparent', border: '1px solid var(--border-default)', color: 'var(--text-light)', borderRadius: 100, padding: '12px 24px', fontSize: 13, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.target.style.borderColor = 'var(--accent)'; e.target.style.color = 'var(--text-white)'; }}
              onMouseLeave={e => { e.target.style.borderColor = 'var(--border-default)'; e.target.style.color = 'var(--text-light)'; }}>
              View Methodology
            </button>
          </div>
        </div>
        <BrainMap />
      </div>

      {/* Stats Strip */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 1,
        background: 'var(--border-default)', border: '1px solid var(--border-default)',
        borderRadius: 10, overflow: 'hidden', marginBottom: 48,
      }}>
        {STATS.map(({ value, label }) => (
          <div key={label} style={{ background: 'var(--bg-card)', padding: '24px 28px' }}>
            <div style={{ fontFamily: 'var(--font-sans)', fontSize: '40px', fontWeight: 500, color: 'var(--accent)', lineHeight: 1.1 }}>
              {value}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 4 }}>
              {label}
            </div>
          </div>
        ))}
      </div>

      {/* Feature Cards */}
      <div className="grid-3col">
        {[
          { icon: Waves, title: 'Live BIDS Dataset', desc: 'ds004279 OpenNeuro — 56 subjects, auditory perception and imagined speech conditions.', page: 'explorer' },
          { icon: Zap, title: 'EEGNet Decoder', desc: 'PyTorch EEGNet trained per-subject on 14 left-hemisphere language-lateralized channels.', page: 'prediction' },
          { icon: Radio, title: 'Zero-Shot Retrieval', desc: 'Multilingual SentenceTransformer cosine similarity — decode any candidate phrase.', page: 'prediction' },
        ].map(({ icon: Icon, title, desc, page }) => (
          <div key={title} className="glass-card" style={{ cursor: 'pointer' }} onClick={() => setActivePage(page)}>
            <div style={{ width: 36, height: 36, borderRadius: 8, background: 'rgba(91,157,249,0.08)', border: '1px solid rgba(91,157,249,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
              <Icon size={16} color="var(--accent)" />
            </div>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>{title}</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
