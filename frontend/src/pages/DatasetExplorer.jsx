import { useState, useEffect } from 'react';
import { api } from '../api';
import WaveformChart from '../WaveformChart';

function OfflineAlert() {
  return (
    <div className="alert-card alert-warning" style={{ color: 'var(--text-light-primary)', borderColor: '#E0E0E0', backgroundColor: '#F8F8F8' }}>
      <span style={{ fontSize: 20 }}>⚠️</span>
      <div className="alert-message">
        <p><strong>Scientific Dataset is Offline</strong></p>
        <p style={{ color: 'var(--text-light-secondary)', marginTop: 4 }}>
          The backend API could not find the BIDS EEG dataset NPZ. Run the application inside the official Docker container on Hugging Face Spaces for full live data mode.
        </p>
      </div>
    </div>
  );
}

function MetadataTable({ meta }) {
  if (!meta) return null;
  return (
    <div className="custom-table-container">
      <table className="custom-table">
        <tbody>
          {Object.entries(meta).map(([k, v]) => (
            <tr key={k}>
              <td style={{ color: 'var(--text-light-secondary)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>{k}</td>
              <td style={{ color: 'var(--text-light-primary)', fontWeight: 500 }}>{String(v)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function DatasetExplorer({ selectors, metadata, apiOnline }) {
  const [trialData, setTrialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { subject, condition, stimulusIdx, trialIdx } = selectors;

  useEffect(() => {
    if (!apiOnline) return;
    setLoading(true);
    setError(null);
    api.getTrial(subject, condition, stimulusIdx, trialIdx, false)
      .then(d => { setTrialData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [subject, condition, stimulusIdx, trialIdx, apiOnline]);

  const sentences = metadata?.sentences || {};
  const conditionName = Object.values(metadata?.conditions || {})[condition] || `Condition ${condition}`;

  return (
    <div>
      {!apiOnline && <OfflineAlert />}

      {/* Session Info Card */}
      <div className="glass-card" style={{ marginBottom: 24 }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-light-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>
          Selected Session
        </div>
        <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-light-primary)' }}>
          Subject {subject} | Task: {conditionName} | Trial #{Number(trialIdx) + 1}
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-light-secondary)', marginTop: 8 }}>
          Target Spanish Phrase: <strong style={{ color: 'var(--text-light-primary)' }}>
            &ldquo;{sentences[stimulusIdx] || '—'}&rdquo;
          </strong>
        </div>
      </div>

      {loading && (
        <div className="glass-card" style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 13, color: 'var(--text-light-secondary)' }}>Loading trial from BIDS dataset…</div>
          <div className="progress-container" style={{ maxWidth: 300, margin: '16px auto 0' }}>
            <div className="progress-track" style={{ width: '100%', height: 4, backgroundColor: '#E0E0E0', borderRadius: 2, overflow: 'hidden' }}>
              <div className="progress-fill" style={{ width: '60%', height: '100%', background: '#0E0E0E' }} />
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="alert-card alert-error" style={{ borderColor: 'red' }}>
          <span>❌</span>
          <div className="alert-message"><strong>Error:</strong> {error}</div>
        </div>
      )}

      {trialData && !loading && (
        <div className="grid-2col">
          {/* Waveform */}
          <div className="glass-card">
            <WaveformChart
              data={trialData.raw_signal}
              channels={trialData.channels}
              title="Raw EEG Signal — Top 3 Left-Hemisphere Channels"
            />
          </div>

          {/* Metadata */}
          <div className="glass-card">
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-light-secondary)', marginBottom: 12, textTransform: 'uppercase' }}>
              Trial Metadata
            </p>
            <MetadataTable meta={trialData.metadata} />

            <div style={{ marginTop: 24 }}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-light-secondary)', marginBottom: 14, textTransform: 'uppercase' }}>
                Signal Shape
              </p>
              <div className="stat-grid">
                <div className="stat-item stat-item-accent">
                  <div className="stat-value">{trialData.channels?.length}</div>
                  <div className="stat-label">Channels</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{trialData.timepoints}</div>
                  <div className="stat-label">Timepoints</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{trialData.sampling_rate} Hz</div>
                  <div className="stat-label">Sampling Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
