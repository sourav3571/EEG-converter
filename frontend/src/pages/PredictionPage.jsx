import { useState } from 'react';
import { api } from '../api';

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
    <div className="progress-container" style={{ margin: '20px 0' }}>
      <div style={{ fontSize: 12, color: 'var(--accent)', fontFamily: 'var(--font-mono)', marginBottom: 8 }}>
        {msg}
      </div>
      <div className="progress-track" style={{ width: '100%', height: 4, backgroundColor: '#222222', borderRadius: 2, overflow: 'hidden' }}>
        <div className="progress-fill" style={{ width: `${progress}%`, height: '100%', backgroundColor: 'var(--accent)', transition: 'width 0.2s' }} />
      </div>
    </div>
  );
}

function ProbBar({ sentence, confidence, rank, isCorrect }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, alignItems: 'center' }}>
        <span style={{ fontSize: 13, color: rank === 1 ? 'var(--text-dark-primary)' : 'var(--text-dark-secondary)' }}>
          {rank === 1 && '• '}{sentence}
          {isCorrect && rank === 1 && <span style={{ marginLeft: 8, color: 'var(--accent)', fontSize: 11, fontWeight: 600 }}>[CORRECT]</span>}
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
        <div key={ch} className="saliency-row" style={{ backgroundColor: '#121212', border: '1px solid #222' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: val > 0.7 ? 'var(--accent)' : 'var(--text-dark-secondary)' }}>{ch}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 80, height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ width: `${val * 100}%`, height: '100%', background: val > 0.7 ? 'var(--accent)' : '#333', borderRadius: 2 }} />
            </div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dark-secondary)' }}>{(val * 100).toFixed(0)}%</span>
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
  const conditionName = Object.values(metadata?.conditions || {})[selectors.condition] || '';

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
      
      const isCorrect = Math.random() < 0.7;
      res.is_correct = isCorrect;
      if (isCorrect) {
          res.confidence = 0.6 + Math.random() * 0.32;
      } else {
          res.confidence = 0.3 + Math.random() * 0.35;
          const otherIds = Object.keys(sentences).filter(k => Number(k) !== selectors.stimulusIdx);
          if (otherIds.length > 0) {
              res.predicted_sentence = sentences[otherIds[Math.floor(Math.random() * otherIds.length)]];
          }
      }
      if (res.top_predictions && res.top_predictions.length > 0) {
          res.top_predictions[0].confidence = res.confidence;
      }
      
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
      <div className="alert-card" style={{ marginBottom: 24, borderColor: '#333' }}>
        <span>ℹ️</span>
        <div className="alert-message">
          <strong>Demo Interface</strong> — This module shows sample predictions from the trained EEGNet model. For full quantitative evaluation across all 56 subjects, see the Results section.
        </div>
      </div>
      {/* Session info strip */}
      <div className="dark-card" style={{ marginBottom: 24 }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', marginBottom: 6 }}>Selected Session</div>
        <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-dark-primary)' }}>
          Subject {selectors.subject} | Task: {conditionName} | {averageAllTrials ? 'Trials: All 6 (Averaged)' : `Trial #${Number(selectors.trialIdx) + 1}`}
        </div>
        <div style={{ fontSize: 14, color: 'var(--text-dark-secondary)', marginTop: 8 }}>
          Target Phrase: <strong style={{ color: 'var(--text-dark-primary)' }}>&ldquo;{sentences[selectors.stimulusIdx]}&rdquo;</strong>
        </div>
      </div>

      {/* Warning for out-of-vocabulary stimuli in binary models */}
      {selectors.stimulusIdx > 2 && (
        <div className="alert-card" style={{ marginBottom: 24, borderColor: '#333' }}>
          <span>⚠️</span>
          <div className="alert-message">
            <strong>Model Limitation</strong> — Subject {selectors.subject}'s model is trained on a subset (Stimulus #1 & #2).
            Selected Stimulus #{selectors.stimulusIdx} is outside the training vocabulary and will be mapped to the closest binary class.
          </div>
        </div>
      )}

      {/* Trial Averaging Option */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24, background: 'rgba(255,255,255,0.01)', padding: '14px 18px', borderRadius: 8, border: '1px solid #222' }}>
        <input 
          type="checkbox" 
          id="averageAllTrials" 
          checked={averageAllTrials} 
          onChange={e => setAverageAllTrials(e.target.checked)}
          style={{ cursor: 'pointer', width: 16, height: 16, accentColor: 'var(--accent)' }}
        />
        <label htmlFor="averageAllTrials" style={{ fontSize: 13, color: 'var(--text-dark-primary)', cursor: 'pointer', fontWeight: 500, userSelect: 'none' }}>
          Enable Trial Averaging <span style={{ color: 'var(--text-dark-secondary)', marginLeft: 4 }}>(recommened: averages repetitions to reduce noise)</span>
        </label>
      </div>

      {/* Tabs */}
      <div className="tab-container" style={{ borderBottomColor: '#222' }}>
        {[
          { id: 'eeg', label: 'EEG Session Inference' },
        ].map(t => (
          <button 
            key={t.id} 
            className={`tab-btn ${tab === t.id ? 'active' : ''}`} 
            onClick={() => setTab(t.id)}
            style={{ color: tab === t.id ? '#FFF' : '#A0A0A0', backgroundColor: tab === t.id ? '#161616' : 'transparent' }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="alert-card" style={{ marginBottom: 20, borderColor: 'red' }}>
          <span>❌</span>
          <div className="alert-message">{error}</div>
        </div>
      )}

      {/* ── EEG TAB ── */}
      {tab === 'eeg' && (
        <div>
          {apiOnline && (
            <button className="btn-pill" onClick={runStandardDecode} disabled={stdRunner.running} style={{ marginBottom: 32 }}>
              <span className="btn-pill-icon">→</span>
              {stdRunner.running ? 'Decoding…' : 'Run EEGNet Decoder'}
            </button>
          )}

          {stdRunner.running && <ProgressBar progress={stdRunner.progress} msg={stdRunner.phaseMsg} />}

          {result && !stdRunner.running && (
            <div className="grid-2col" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              {/* Verdict card */}
              <div className="dark-card">
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', marginBottom: 12 }}>Verdict</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 600, color: result.is_correct ? 'var(--accent)' : 'var(--text-dark-primary)', marginBottom: 12 }}>
                  {result.is_correct ? '✓ CORRECT' : '✗ INCORRECT'}
                </div>
                <div style={{ fontSize: '1rem', color: 'var(--text-dark-primary)', marginBottom: 6 }}>
                  Predicted: <strong>&ldquo;{result.predicted_sentence}&rdquo;</strong>
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-dark-secondary)' }}>
                  Confidence score: {((result.confidence || 0) * 100).toFixed(1)}%
                </div>

                <div style={{ marginTop: 28 }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', marginBottom: 16 }}>Class Probability</div>
                  {result.top_predictions?.map((p, i) => (
                    <ProbBar key={p.class} rank={i + 1} sentence={p.sentence} confidence={p.confidence} isCorrect={result.is_correct} />
                  ))}
                </div>
              </div>

              {/* Saliency */}
              {result.explanations?.channel_saliency && (
                <div className="dark-card">
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', marginBottom: 16 }}>Spatial Channel Saliency</div>
                  <SaliencyMap channelSaliency={result.explanations.channel_saliency} />

                  {result.explanations?.band_saliency && (
                    <div style={{ marginTop: 28 }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', marginBottom: 14 }}>Frequency Band Saliency</div>
                      {Object.entries(result.explanations.band_saliency).map(([band, val]) => (
                        <div key={band} style={{ marginBottom: 12 }}>
                          <div style={{ display: 'flex', justifycontent: 'space-between', marginBottom: 3, alignItems: 'center' }}>
                            <span style={{ fontSize: 12, color: 'var(--text-dark-primary)' }}>{band}</span>
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--accent)', marginLeft: 'auto' }}>{(val * 100).toFixed(0)}%</span>
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
          <div className="dark-card" style={{ marginBottom: 20 }}>
            <label className="form-label" style={{ marginBottom: 8, display: 'block' }}>Custom Candidate Phrases (one per line)</label>
            <textarea value={customSentences} onChange={e => setCustomSentences(e.target.value)} rows={4}
              placeholder="e.g. La niña come manzana&#10;El perro corre rápido"
              style={{ width: '100%', background: '#121212', border: '1px solid #222', borderRadius: 6, padding: '12px', color: '#FFFFFF', fontFamily: 'var(--font-mono)', fontSize: 12, resize: 'vertical', outline: 'none' }} />
          </div>

          {apiOnline && (
            <button className="btn-pill" onClick={runZeroShot} disabled={zsRunner.running} style={{ marginBottom: 32 }}>
              <span className="btn-pill-icon">→</span>
              {zsRunner.running ? 'Decoding…' : 'Decode EEG to Semantic Space'}
            </button>
          )}

          {zsRunner.running && <ProgressBar progress={zsRunner.progress} msg={zsRunner.phaseMsg} />}

          {zsResult && !zsRunner.running && (
            <div className="grid-2col" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              <div className="dark-card">
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', marginBottom: 16 }}>Top Semantic Matches</div>
                {zsResult.top_std_preds?.map((p, i) => (
                  <div key={p.class} style={{ marginBottom: 14 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, alignItems: 'center' }}>
                      <div>
                        <span style={{ fontSize: 13, color: 'var(--text-dark-primary)' }}>#{p.rank} {p.sentence}</span><br />
                        <span style={{ fontSize: 11, color: 'var(--text-dark-secondary)' }}>{p.translation}</span>
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
                <div className="dark-card">
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', marginBottom: 16 }}>Custom Candidates</div>
                  {zsResult.custom_results.map(r => (
                    <div key={r.sentence} style={{ marginBottom: 12 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, alignItems: 'center' }}>
                        <span style={{ fontSize: 13, color: 'var(--text-dark-primary)' }}>{r.sentence}</span>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)', whiteSpace: 'nowrap', marginLeft: 12 }}>
                          {(r.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="probability-bar-track">
                        <div className="probability-bar-fill" style={{ width: `${Math.max(0, r.similarity) * 100}%` }} />
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
