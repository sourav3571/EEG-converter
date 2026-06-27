import { useState, useEffect } from 'react';
import { api } from '../api';
import WaveformChart from '../WaveformChart';

const PIPELINE_STEPS = [
  { num: '01', title: 'Band-Pass Filter', desc: 'Butterworth 2nd-order IIR filter: 2–50 Hz passband. Removes slow DC drift and high-frequency muscle artefacts.' },
  { num: '02', title: 'ICA Artefact Removal', desc: 'Independent Component Analysis — identifies and removes eye-blink and movement artefacts from 14-channel signal.' },
  { num: '03', title: 'Common Average Reference', desc: 'Re-references each channel to the average of all 14 left-hemisphere channels to reduce common-mode noise.' },
  { num: '04', title: 'Epoch Extraction', desc: 'Extracts fixed 3-second trial epochs time-locked to stimulus onset. Shape: (14 ch × 750 samples).' },
  { num: '05', title: 'Amplitude Normalisation', desc: 'Z-scores each channel across the trial to normalise amplitude scale differences between subjects.' },
];

export default function PreprocessingPage({ selectors, metadata, apiOnline }) {
  const [trialData, setTrialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { subject, condition, stimulusIdx, trialIdx } = selectors;

  useEffect(() => {
    if (!apiOnline) return;
    setLoading(true);
    setError(null);
    api.getTrial(subject, condition, stimulusIdx, trialIdx, true)
      .then(d => { setTrialData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [subject, condition, stimulusIdx, trialIdx, apiOnline]);

  return (
    <div>
      {!apiOnline && (
        <div className="alert-card alert-warning" style={{ color: 'var(--text-light-primary)', borderColor: '#E0E0E0', backgroundColor: '#F8F8F8' }}>
          <span>⚠️</span>
          <div className="alert-message">
            <strong>Dataset Offline</strong> — preprocessing cannot run without the BIDS EEG dataset.
          </div>
        </div>
      )}

      {/* Pipeline Steps */}
      <div className="glass-card" style={{ marginBottom: 24 }}>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-light-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
          Preprocessing Pipeline Stages
        </p>
        <div>
          {PIPELINE_STEPS.map(({ num, title, desc }) => (
            <div key={num} className="step-card" style={{ display: 'flex', gap: 16, padding: '16px 0', borderBottom: '1px solid var(--border-light)' }}>
              <div className="step-num" style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 'bold', color: 'var(--text-light-primary)', width: 32 }}>{num}</div>
              <div>
                <div style={{ fontWeight: 600, color: 'var(--text-light-primary)', marginBottom: 4 }}>{title}</div>
                <div style={{ fontSize: 13, color: 'var(--text-light-secondary)', lineHeight: 1.6 }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {loading && (
        <div className="glass-card" style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 13, color: 'var(--text-light-secondary)' }}>Running preprocessing pipeline…</div>
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
          {/* Raw signal */}
          <div className="glass-card">
            <WaveformChart
              data={trialData.raw_signal}
              channels={trialData.channels}
              title="① Raw EEG (Pre-Processing)"
            />
          </div>
          {/* Clean signal */}
          <div className="glass-card">
            <WaveformChart
              data={trialData.clean_signal || trialData.raw_signal}
              channels={trialData.channels}
              title="⑤ Clean EEG (Post-Processing)"
            />
          </div>

          {/* Stats */}
          {trialData.preprocessing_stats && (
            <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-light-secondary)', textTransform: 'uppercase', marginBottom: 16 }}>
                Processing Statistics
              </p>
              <div className="stat-grid">
                {Object.entries(trialData.preprocessing_stats).map(([k, v]) => (
                  <div key={k} className="stat-item stat-item-accent">
                    <div className="stat-value" style={{ fontSize: '1.2rem' }}>{typeof v === 'number' ? v.toFixed(4) : String(v)}</div>
                    <div className="stat-label">{k.replace(/_/g, ' ')}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
