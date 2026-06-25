export default function WaveformChart({ data, channels, title = 'EEG Signal', color = 'var(--accent)' }) {
  if (!data || !channels) return null;

  const WIDTH = 800;
  const HEIGHT = 320;
  const MARGIN = { top: 10, right: 20, bottom: 30, left: 50 };
  const innerW = WIDTH - MARGIN.left - MARGIN.right;
  const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;

  // Show top 3 channels stacked
  const displayChannels = channels.slice(0, 3);
  const rowH = innerH / displayChannels.length;

  const COLORS = ['#00F0FF', '#BD00FF', '#10B981'];

  return (
    <div style={{ width: '100%' }}>
      <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>
        {title}
      </p>
      <div style={{ width: '100%', overflowX: 'auto' }}>
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} style={{ width: '100%', background: '#0A0A12', borderRadius: 8 }}>
          <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
            {displayChannels.map((ch, ci) => {
              const row = data[ci] || [];
              if (!row.length) return null;

              const yMin = Math.min(...row);
              const yMax = Math.max(...row);
              const yRange = yMax - yMin || 1;
              const yOffset = ci * rowH + rowH / 2;

              const pts = row.map((v, i) => {
                const x = (i / (row.length - 1)) * innerW;
                const y = yOffset + ((v - (yMin + yMax) / 2) / yRange) * (rowH * 0.9);
                return `${x.toFixed(1)},${y.toFixed(1)}`;
              }).join(' ');

              return (
                <g key={ch}>
                  {/* grid line */}
                  <line x1={0} y1={ci * rowH} x2={innerW} y2={ci * rowH}
                    stroke="rgba(255,255,255,0.03)" strokeWidth={1} />
                  {/* channel label */}
                  <text x={-6} y={yOffset + 4} textAnchor="end"
                    fill={COLORS[ci % COLORS.length]} fontSize={9}
                    fontFamily="JetBrains Mono, monospace">{ch}</text>
                  {/* waveform */}
                  <polyline points={pts} fill="none"
                    stroke={COLORS[ci % COLORS.length]} strokeWidth={1.2} opacity={0.9} />
                </g>
              );
            })}
            {/* X axis */}
            <line x1={0} y1={innerH} x2={innerW} y2={innerH} stroke="rgba(255,255,255,0.08)" />
            <text x={innerW / 2} y={innerH + 22} textAnchor="middle"
              fill="rgba(255,255,255,0.3)" fontSize={9} fontFamily="JetBrains Mono, monospace">
              Time (samples) — 3 s @ 250 Hz
            </text>
          </g>
        </svg>
      </div>
    </div>
  );
}
