import { useState } from 'react';
import { api } from '../api';
import { Brain, Zap } from 'lucide-react';

const PHASES_STANDARD = [
  'Loading EEG trial epochs from NPZ…',
  'Applying Butterworth 2–50 Hz filter…',
  'Removing ocular (ICA) noise channels…',
  'Re-referencing (Common Average Reference)…',
  'Performing EEGNet forward neural pass…',
  'Generating saliency maps & confidence distributions…',
];

const PHASES_ZERO = [
  'Extracting EEG epochs…',
  'Preprocessing signal & filtering noise…',
  'Loading contrastive projection network…',
  'Mapping EEG to 384D multilingual embedding space…',
  'Computing cosine similarity with 30 standard candidates…',
];

function useDecodeRunner(phases) {
  const [progress, setProgress] = useState(0);
  const [phaseMsg, setPhaseMsg] = useState('');
  const [running, setRunning] = useState(false);

  async function runAnimation() {
    setRunning(true);
    for (let i = 0; i < phases.length; i++) {
      setPhaseMsg(phases[i]);
      setProgress(Math.round(((i + 1) / phases.length) * 100));
      await new Promise(r => setTimeout(r, 200));
    }
    setRunning(false);
  }

  return { progress, phaseMsg, running, runAnimation };
}

function ProgressBar({ progress, msg }) {
  return (
    <div className="progress-container">
      <div style={{ fontSize: 12, color: 'var(--accent)', fontFamily: 'var(--font-mono)', marginBottom: 8 }}>
        {msg}
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}

function ProbBar({ sentence, confidence, rank, isCorrect }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, alignItems: 'center' }}>
        <span style={{ fontSize: 12, color: rank === 1 ? 'var(--text-white)' : 'var(--text-light)' }}>
          {rank === 1 && '🥇 '}{rank === 2 && '🥈 '}{rank === 3 && '🥉 '}
          {sentence}
          {isCorrect && rank === 1 && <span style={{ marginLeft: 8, color: 'var(--success)', fontSize: 11 }}>✓ CORRECT</span>}
        </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)' }}>
          {(confidence * 100).toFixed(1)}%
        </span>
      </div>
      <div className="probability-bar-track">
        <div className="probability-bar-fill" style={{ width: `${confidence * 100}%` }} />
      </div>
    </div>
  );
}

function SaliencyMap({ channelSaliency }) {
  if (!channelSaliency) return null;
  const sorted = Object.entries(channelSaliency).sort(([, a], [, b]) => b - a);
  return (
    <div className="saliency-list">
      {sorted.map(([ch, val]) => (
        <div key={ch} className={`saliency-row ${val > 0.7 ? 'saliency-row-high' : ''}`}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: val > 0.7 ? 'var(--accent)' : 'var(--text-muted)' }}>{ch}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 80, height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ width: `${val * 100}%`, height: '100%', background: val > 0.7 ? 'var(--accent)' : 'var(--border-default)', borderRadius: 2 }} />
            </div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>{(val * 100).toFixed(0)}%</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function PredictionPage({ selectors, metadata, apiOnline }) {
  const [tab, setTab] = useState('eeg');
  const [result, setResult] = useState(null);
  const [zsResult, setZsResult] = useState(null);
  const [error, setError] = useState(null);
  const [customSentences, setCustomSentences] = useState('');
  const [averageAllTrials, setAverageAllTrials] = useState(true);

  const stdRunner = useDecodeRunner(PHASES_STANDARD);
  const zsRunner = useDecodeRunner(PHASES_ZERO);

  const sentences = metadata?.sentences || {};
  const conditionName = metadata?.conditions?.[selectors.condition] || '';

  async function runStandardDecode() {
    setError(null);
    await stdRunner.runAnimation();
    try {
      const res = await api.decode({
        subject: selectors.subject,
        condition: selectors.condition,
        stimulus_idx: selectors.stimulusIdx,
        trial_idx: selectors.trialIdx,
        average_all_trials: averageAllTrials,
      });
      setResult(res);
    } catch (e) {
      setError(e.message);
    }
  }

  async function runZeroShot() {
    setError(null);
    await zsRunner.runAnimation();
    try {
      const custom = customSentences.split('\n').map(s => s.trim()).filter(Boolean);
      const res = await api.decodeZeroShot({
        subject: selectors.subject,
        condition: selectors.condition,
        stimulus_idx: selectors.stimulusIdx,
        trial_idx: selectors.trialIdx,
        custom_sentences: custom,
        average_all_trials: averageAllTrials,
      });
      setZsResult(res);
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <span className="section-marker">[05] MODEL PREDICTION</span>
      <h1 style={{ fontSize: '1.8rem', marginBottom: 6 }}>EEG Decoding Console</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
        Run EEGNet decoding or zero-shot semantic retrieval on the selected EEG trial.
      </p>

      {!apiOnline && (
        <div className="alert-card alert-warning">
          <span>⚠️</span>
          <div className="alert-message">
            <strong>Dataset Offline</strong> — decoding requires the live BIDS EEG dataset and trained model weights.
            Run in the official Docker container on Hugging Face Spaces.
          </div>
        </div>
      )}

      {/* Session info strip */}
      <div className="glass-card" style={{ marginBottom: 24 }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Selected Session</div>
        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent)' }}>
          Subject {selectors.subject} | Task: {conditionName} | {averageAllTrials ? 'Trials: All 6 (Averaged)' : `Trial #${Number(selectors.trialIdx) + 1}`}
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-light)', marginTop: 4 }}>
          Target: <strong style={{ color: 'var(--text-white)' }}>&ldquo;{sentences[selectors.stimulusIdx]}&rdquo;</strong>
        </div>
      </div>

      {/* Warning for out-of-vocabulary stimuli in binary models */}
      {selectors.stimulusIdx > 2 && (
        <div className="alert-card alert-warning" style={{ marginBottom: 24 }}>
          <span>⚠️</span>
          <div className="alert-message">
            <strong>Model Limit Warning</strong> — Subject {selectors.subject}'s model is a binary classifier trained on 2 sentences (Stimulus #1 & #2).
            Selected Stimulus #{selectors.stimulusIdx} is outside the training set and will be forced into a 2-class prediction.
          </div>
        </div>
      )}

      {/* Trial Averaging Option */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24, background: 'rgba(255,255,255,0.02)', padding: '12px 16px', borderRadius: 8, border: '1px solid var(--border-default)' }}>
        <input 
          type="checkbox" 
          id="averageAllTrials" 
          checked={averageAllTrials} 
          onChange={e => setAverageAllTrials(e.target.checked)}
          style={{ cursor: 'pointer', width: 16, height: 16, accentColor: 'var(--accent)' }}
        />
        <label htmlFor="averageAllTrials" style={{ fontSize: 13, color: 'var(--text-white)', cursor: 'pointer', fontWeight: 500, userSelect: 'none' }}>
          🧬 Enable Trial Averaging <span style={{ color: 'var(--accent)', marginLeft: 4 }}>(averages all 6 repetitions to cancel background brain noise)</span>
        </label>
      </div>

      {/* Tabs */}
      <div className="tab-container">
        {[
          { id: 'eeg', label: '⚡ EEG Session Inference' },
          { id: 'zs', label: '🔬 Zero-Shot Semantic Retrieval' },
        ].map(t => (
          <button key={t.id} className={`tab-btn ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="alert-card alert-error" style={{ marginBottom: 20 }}>
          <span>❌</span>
          <div className="alert-message">{error}</div>
        </div>
      )}

      {/* ── EEG TAB ── */}
      {tab === 'eeg' && (
        <div>
          {apiOnline && (
            <button className="btn-primary" onClick={runStandardDecode} disabled={stdRunner.running} style={{ marginBottom: 24 }}>
              <Brain size={14} />
              {stdRunner.running ? 'Decoding…' : 'Run EEGNet Decoder'}
            </button>
          )}

          {stdRunner.running && <ProgressBar progress={stdRunner.progress} msg={stdRunner.phaseMsg} />}

          {result && !stdRunner.running && (
            <div className="grid-2col">
              {/* Verdict card */}
              <div className="glass-card">
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>Decoding Result</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: result.is_correct ? 'var(--success)' : 'var(--warning)', marginBottom: 8 }}>
                  {result.is_correct ? '✓ CORRECT' : '✗ INCORRECT'}
                </div>
                <div style={{ fontSize: '1rem', color: 'var(--text-white)', marginBottom: 4 }}>
                  Predicted: <strong>&ldquo;{result.predicted_sentence}&rdquo;</strong>
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>
                  Confidence: {((result.confidence || 0) * 100).toFixed(1)}%
                </div>

                <div style={{ marginTop: 24 }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>Top Predictions</div>
                  {result.top_predictions?.map((p, i) => (
                    <ProbBar key={p.class} rank={i + 1} sentence={p.sentence} confidence={p.confidence} isCorrect={result.is_correct} />
                  ))}
                </div>
              </div>

              {/* Saliency */}
              {result.explanations?.channel_saliency && (
                <div className="glass-card">
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 14 }}>Channel Saliency</div>
                  <SaliencyMap channelSaliency={result.explanations.channel_saliency} />

                  {result.explanations?.band_saliency && (
                    <div style={{ marginTop: 20 }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 10 }}>Band Saliency</div>
                      {Object.entries(result.explanations.band_saliency).map(([band, val]) => (
                        <div key={band} style={{ marginBottom: 10 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                            <span style={{ fontSize: 12, color: 'var(--text-light)' }}>{band}</span>
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>{(val * 100).toFixed(0)}%</span>
                          </div>
                          <div className="probability-bar-track">
                            <div className="probability-bar-fill" style={{ width: `${val * 100}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── ZERO-SHOT TAB ── */}
      {tab === 'zs' && (
        <div>
          <div className="glass-card" style={{ marginBottom: 20 }}>
            <label className="form-label" style={{ marginBottom: 8, display: 'block' }}>Custom Candidate Sentences (one per line, optional)</label>
            <textarea value={customSentences} onChange={e => setCustomSentences(e.target.value)} rows={4}
              placeholder="e.g. La niña come manzana&#10;El perro corre rápido"
              style={{ width: '100%', background: 'var(--bg-main)', border: '1px solid var(--border-default)', borderRadius: 6, padding: '10px 12px', color: 'var(--text-white)', fontFamily: 'var(--font-mono)', fontSize: 12, resize: 'vertical', outline: 'none' }} />
          </div>

          {apiOnline && (
            <button className="btn-primary" onClick={runZeroShot} disabled={zsRunner.running} style={{ marginBottom: 24 }}>
              <Zap size={14} />
              {zsRunner.running ? 'Decoding…' : 'Decode EEG to Semantic Space'}
            </button>
          )}

          {zsRunner.running && <ProgressBar progress={zsRunner.progress} msg={zsRunner.phaseMsg} />}

          {zsResult && !zsRunner.running && (
            <div className="grid-2col">
              <div className="glass-card">
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>Top Semantic Matches</div>
                {zsResult.top_std_preds?.map((p, i) => (
                  <div key={p.class} style={{ marginBottom: 14 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <div>
                        <span style={{ fontSize: 12, color: 'var(--text-light)' }}>#{p.rank} {p.sentence}</span><br />
                        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{p.translation}</span>
                      </div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)', whiteSpace: 'nowrap', marginLeft: 12 }}>
                        {(p.similarity * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="probability-bar-track">
                      <div className="probability-bar-fill" style={{ width: `${Math.max(0, p.similarity) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>

              {zsResult.custom_results?.length > 0 && (
                <div className="glass-card">
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>Custom Candidate Results</div>
                  {zsResult.custom_results.map(r => (
                    <div key={r.sentence} style={{ marginBottom: 12 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontSize: 12, color: 'var(--text-light)' }}>{r.sentence}</span>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent-secondary)', whiteSpace: 'nowrap', marginLeft: 12 }}>
                          {(r.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="probability-bar-track">
                        <div className="probability-bar-fill" style={{ width: `${Math.max(0, r.similarity) * 100}%`, background: 'var(--accent-secondary)' }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
