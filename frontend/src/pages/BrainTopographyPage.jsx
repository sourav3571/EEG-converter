// Brain Topography page — renders a 2D scalp map of channel amplitudes from live data

const CHANNEL_POSITIONS = {
  'F7':  { x: 20, y: 28 }, 'F5':  { x: 28, y: 25 }, 'F3':  { x: 36, y: 23 },
  'FC5': { x: 22, y: 40 }, 'FC3': { x: 31, y: 37 }, 'C5':  { x: 22, y: 52 },
  'C3':  { x: 32, y: 50 }, 'CP5': { x: 22, y: 63 }, 'CP3': { x: 33, y: 61 },
  'T7':  { x: 16, y: 50 }, 'TP7': { x: 18, y: 62 }, 'P7':  { x: 22, y: 74 },
  'P5':  { x: 30, y: 72 }, 'P3':  { x: 38, y: 70 },
};

function lerp(a, b, t) { return a + (b - a) * t; }
function amplitudeToColor(norm) {
  // Clean monochrome scale: Light grey to dark slate/black
  const stops = [
    [240, 240, 240], [200, 200, 200], [150, 150, 150], [80, 80, 80], [14, 14, 14]
  ];
  const t = Math.max(0, Math.min(1, norm)) * (stops.length - 1);
  const i = Math.floor(t);
  const f = t - i;
  const [r1, g1, b1] = stops[Math.min(i, stops.length - 1)];
  const [r2, g2, b2] = stops[Math.min(i + 1, stops.length - 1)];
  return `rgb(${Math.round(lerp(r1,r2,f))},${Math.round(lerp(g1,g2,f))},${Math.round(lerp(b1,b2,f))})`;
}

function TopoMap({ amplitudes, channels }) {
  if (!amplitudes || !channels) return null;
  const vals = amplitudes.map(v => {
    const arr = Array.isArray(v) ? v : [];
    return arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
  });
  const mn = Math.min(...vals);
  const mx = Math.max(...vals) || 1;

  return (
    <svg viewBox="0 0 100 100" style={{ width: '100%', maxWidth: 420, display: 'block', margin: '0 auto', background: '#FFFFFF' }}>
      {/* Head circle */}
      <circle cx={50} cy={50} r={42} fill="#FFFFFF" stroke="#E0E0E0" strokeWidth={1} />
      {/* Nose */}
      <path d="M 46 10 Q 50 5 54 10" fill="none" stroke="#E0E0E0" strokeWidth={0.8} />
      {/* Electrode bubbles */}
      {channels.map((ch, i) => {
        const pos = CHANNEL_POSITIONS[ch];
        if (!pos) return null;
        const norm = (vals[i] - mn) / (mx - mn);
        const color = amplitudeToColor(norm);
        // Determine text color based on bubble brightness
        const textColor = norm > 0.6 ? '#FFFFFF' : '#000000';
        return (
          <g key={ch}>
            <circle cx={pos.x} cy={pos.y} r={5.5} fill={color} stroke="#E0E0E0" strokeWidth={0.5} opacity={0.9} />
            <text x={pos.x} y={pos.y + 1} textAnchor="middle" dominantBaseline="middle"
              fontSize={2.2} fill={textColor} fontFamily="var(--font-mono)" fontWeight="bold"
              style={{ userSelect: 'none' }}>{ch}</text>
          </g>
        );
      })}
      {/* Colourbar legend */}
      <defs>
        <linearGradient id="cb" x1="0" x2="1">
          <stop offset="0%" stopColor="#F0F0F0" />
          <stop offset="100%" stopColor="#0E0E0E" />
        </linearGradient>
      </defs>
      <rect x={10} y={92} width={80} height={4} fill="url(#cb)" rx={2} />
      <text x={10} y={99} fontSize={2.5} fill="#888888" fontFamily="var(--font-mono)">MIN (μV)</text>
      <text x={88} y={99} fontSize={2.5} fill="#888888" fontFamily="var(--font-mono)" textAnchor="end">MAX (μV)</text>
    </svg>
  );
}

export default function BrainTopographyPage({ selectors, metadata, apiOnline, trialData }) {
  const sentences = metadata?.sentences || {};
  const conditionName = Object.values(metadata?.conditions || {})[selectors.condition] || '';

  return (
    <div>
      {!apiOnline && (
        <div className="alert-card alert-warning">
          <span>⚠️</span>
          <div className="alert-message"><strong>Dataset Offline</strong> — topographic maps require live EEG data.</div>
        </div>
      )}

      {trialData ? (
        <div className="grid-2col">
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: 32 }}>
            <TopoMap amplitudes={trialData.raw_signal} channels={trialData.channels} />
            <div style={{ marginTop: 16, fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-light-secondary)', textAlign: 'center', lineHeight: 1.8 }}>
              Subject {selectors.subject} · {conditionName} · Trial #{Number(selectors.trialIdx) + 1}<br />
              Stimulus: &ldquo;{sentences[selectors.stimulusIdx]}&rdquo;
            </div>
          </div>

          {/* Channel amplitude table */}
          <div className="glass-card">
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-light-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 14 }}>
              Channel Mean Amplitudes
            </p>
            <div className="saliency-list">
              {trialData.channels?.map((ch, i) => {
                const arr = trialData.raw_signal?.[i] || [];
                const mean = arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(4) : '—';
                return (
                  <div key={ch} className="saliency-row" style={{ backgroundColor: '#FFFFFF', border: '1px solid #E0E0E0' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-light-primary)', fontWeight: 'bold' }}>{ch}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-light-secondary)' }}>{mean} μV</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        apiOnline && (
          <div className="glass-card" style={{ textAlign: 'center', padding: 40 }}>
            <p style={{ color: 'var(--text-light-secondary)' }}>Navigate to Dataset Explorer first to load trial data.</p>
          </div>
        )
      )}
    </div>
  );
}
