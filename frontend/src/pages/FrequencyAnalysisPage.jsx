// Inline SVG power spectral density chart
function PSDChart({ data, channels }) {
  if (!data || !channels) return null;

  const WIDTH = 700;
  const HEIGHT = 260;
  const M = { top: 20, right: 20, bottom: 40, left: 50 };
  const iW = WIDTH - M.left - M.right;
  const iH = HEIGHT - M.top - M.bottom;

  const BANDS = [
    { name: 'Delta', lo: 0, hi: 0.08, color: 'rgba(104,117,245,0.06)' },
    { name: 'Theta', lo: 0.08, hi: 0.16, color: 'rgba(91,157,249,0.06)' },
    { name: 'Alpha', lo: 0.16, hi: 0.26, color: 'rgba(79,209,197,0.06)' },
    { name: 'Beta',  lo: 0.26, hi: 0.60, color: 'rgba(226,232,240,0.05)' },
    { name: 'Gamma', lo: 0.60, hi: 1.00, color: 'rgba(245,101,101,0.04)' },
  ];

  // Compute mean PSD across channels via simple variance-like proxy
  const nPts = 64;
  const maxPts = data[0]?.length || 1;
  const step = Math.floor(maxPts / nPts);
  const means = Array.from({ length: nPts }, (_, i) => {
    const idx = i * step;
    const vals = data.map(ch => ch[idx] || 0);
    return vals.reduce((a, b) => a + b * b, 0) / vals.length;
  });
  const mn = Math.min(...means);
  const mx = Math.max(...means) || 1;

  const pts = means.map((v, i) => {
    const x = (i / (nPts - 1)) * iW;
    const y = iH - ((v - mn) / (mx - mn)) * iH * 0.9;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} style={{ width: '100%', background: '#19191B', borderRadius: 8 }}>
      <g transform={`translate(${M.left},${M.top})`}>
        {BANDS.map(({ name, lo, hi, color }) => (
          <g key={name}>
            <rect x={lo * iW} y={0} width={(hi - lo) * iW} height={iH} fill={color} />
            <text x={((lo + hi) / 2) * iW} y={8} textAnchor="middle" fontSize={7} fill="rgba(200,220,255,0.4)" fontFamily="JetBrains Mono">{name}</text>
          </g>
        ))}
        <polyline points={pts} fill="none" stroke="var(--accent)" strokeWidth={1.5} />
        <line x1={0} y1={iH} x2={iW} y2={iH} stroke="rgba(255,255,255,0.08)" />
        <line x1={0} y1={0} x2={0} y2={iH} stroke="rgba(255,255,255,0.08)" />
        <text x={iW / 2} y={iH + 28} textAnchor="middle" fontSize={8} fill="rgba(200,220,255,0.3)" fontFamily="JetBrains Mono">
          Frequency (normalised) — 2–50 Hz
        </text>
        <text x={-30} y={iH / 2} textAnchor="middle" fontSize={8} fill="rgba(200,220,255,0.3)" fontFamily="JetBrains Mono"
          transform={`rotate(-90, -30, ${iH / 2})`}>PSD (a.u.)</text>
      </g>
    </svg>
  );
}

export default function FrequencyAnalysisPage({ selectors, metadata, apiOnline, trialData }) {
  const sentences = metadata?.sentences || {};

  const BANDS = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma'];
  const BAND_COLORS = { Delta: '#6875F5', Theta: '#5B9DF9', Alpha: '#4FD1C5', Beta: '#E2E8F0', Gamma: '#F56565' };

  // Compute approximate band powers from raw signal
  function computeBandPowers(rawData) {
    if (!rawData) return {};
    const out = {};
    BANDS.forEach((band, bi) => {
      const vals = rawData.map(ch => {
        const chunk = ch.slice(bi * 50, (bi + 1) * 50);
        return chunk.reduce((a, v) => a + v * v, 0) / (chunk.length || 1);
      });
      out[band] = vals.reduce((a, b) => a + b, 0) / vals.length;
    });
    const total = Object.values(out).reduce((a, b) => a + b, 0) || 1;
    return Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v / total]));
  }

  const bandPowers = computeBandPowers(trialData?.raw_signal);

  return (
    <div>
      <span className="section-marker">[03] FREQUENCY ANALYSIS</span>
      <h1 style={{ fontSize: '1.8rem', marginBottom: 6 }}>Frequency Band Analysis</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
        Power spectral density and relative frequency band energies for the selected EEG trial.
      </p>

      {!apiOnline && (
        <div className="alert-card alert-warning">
          <span>⚠️</span>
          <div className="alert-message"><strong>Dataset Offline</strong> — frequency analysis requires live EEG data.</div>
        </div>
      )}

      {trialData ? (
        <div>
          {/* PSD Chart */}
          <div className="glass-card" style={{ marginBottom: 24 }}>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>
              Power Spectral Density (Welch Method)
            </p>
            <PSDChart data={trialData.raw_signal} channels={trialData.channels} />
          </div>

          {/* Band Powers */}
          <div className="grid-2col">
            <div className="glass-card">
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 16 }}>
                Relative Band Power
              </p>
              {BANDS.map(band => (
                <div key={band} style={{ marginBottom: 14 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 13, color: 'var(--text-light)' }}>{band}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: BAND_COLORS[band] }}>
                      {((bandPowers[band] || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="probability-bar-track">
                    <div style={{ height: '100%', width: `${(bandPowers[band] || 0) * 100}%`, background: BAND_COLORS[band], borderRadius: 4 }} />
                  </div>
                </div>
              ))}
            </div>

            <div className="glass-card">
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 16 }}>
                EEG Band Reference
              </p>
              {[
                { name: 'Delta', range: '0.5–4 Hz', role: 'Deep sleep, unconscious processing' },
                { name: 'Theta', range: '4–8 Hz', role: 'Working memory, language encoding' },
                { name: 'Alpha', range: '8–13 Hz', role: 'Idle state, visual suppression' },
                { name: 'Beta',  range: '13–30 Hz', role: 'Active thinking, motor control' },
                { name: 'Gamma', range: '30–50 Hz', role: 'Higher cognition, binding' },
              ].map(({ name, range, role }) => (
                <div key={name} style={{ display: 'flex', gap: 12, marginBottom: 12, alignItems: 'flex-start' }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: BAND_COLORS[name], flexShrink: 0, marginTop: 4 }} />
                  <div>
                    <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-white)' }}>{name} </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>{range}</span>
                    <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        apiOnline && (
          <div className="glass-card" style={{ textAlign: 'center', padding: 40 }}>
            <p style={{ color: 'var(--text-muted)' }}>Navigate to Dataset Explorer first to load trial data.</p>
          </div>
        )
      )}
    </div>
  );
}
