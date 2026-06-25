import { useState, useEffect } from 'react';
import { api } from '../api';
import WaveformChart from '../WaveformChart';

function OfflineAlert() {
  return (
    <div className="alert-card alert-warning">
      <span style={{ fontSize: 20 }}>⚠️</span>
      <div className="alert-message">
        <p><strong>Scientific Dataset is Offline</strong></p>
        <p>The backend API could not find the BIDS EEG dataset NPZ. Run the application inside the official Docker container on Hugging Face Spaces for full live data mode.</p>
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
              <td style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>{k}</td>
              <td style={{ color: 'var(--text-white)' }}>{String(v)}</td>
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
  const conditionName = metadata?.conditions?.[condition] || `Condition ${condition}`;

  return (
    <div>
      <span className="section-marker">[02] DATASET EXPLORER</span>
      <h1 style={{ fontSize: '1.8rem', marginBottom: 6 }}>Individual Trial Explorer</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
        Explore individual EEG trials and channel waveforms from the ds004279 BIDS dataset.
      </p>

      {!apiOnline && <OfflineAlert />}

      {/* Session Info Card */}
      <div className="glass-card" style={{ marginBottom: 24 }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>
          Selected Session
        </div>
        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent)' }}>
          Subject {subject} | Task: {conditionName} | Trial #{Number(trialIdx) + 1}
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-light)', marginTop: 6 }}>
          Target Spanish Phrase: <strong style={{ color: 'var(--text-white)' }}>
            &ldquo;{sentences[stimulusIdx] || '—'}&rdquo;
          </strong>
        </div>
      </div>

      {loading && (
        <div className="glass-card" style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading trial from BIDS dataset…</div>
          <div className="progress-container" style={{ maxWidth: 300, margin: '16px auto 0' }}>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: '60%', animation: 'none', background: 'var(--accent)' }} />
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="alert-card alert-error">
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
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', marginBottom: 12, textTransform: 'uppercase' }}>
              Trial Metadata
            </p>
            <MetadataTable meta={trialData.metadata} />

            <div style={{ marginTop: 20 }}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase' }}>
                Signal Shape
              </p>
              <div className="stat-grid">
                <div className="stat-item stat-item-accent">
                  <div className="stat-value" style={{ fontSize: '1.3rem' }}>{trialData.channels?.length}</div>
                  <div className="stat-label">Channels</div>
                </div>
                <div className="stat-item stat-item-purple">
                  <div className="stat-value" style={{ fontSize: '1.3rem' }}>{trialData.timepoints}</div>
                  <div className="stat-label">Timepoints</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value" style={{ fontSize: '1.3rem' }}>{trialData.sampling_rate} Hz</div>
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
