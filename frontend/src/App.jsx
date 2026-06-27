import { useState, useEffect, useRef } from 'react';
import './App.css';
import { api } from './api';
import DatasetExplorer from './pages/DatasetExplorer';
import PreprocessingPage from './pages/PreprocessingPage';
import FrequencyAnalysisPage from './pages/FrequencyAnalysisPage';
import BrainTopographyPage from './pages/BrainTopographyPage';
import PredictionPage from './pages/PredictionPage';

const DEFAULT_SELECTORS = {
  subject: 'S39',
  condition: 0,
  stimulusIdx: 1,
  trialIdx: 0,
};

// Simple clean SVG line waveform preview for the hero section
function HeroWaveform() {
  const points = Array.from({ length: 120 }, (_, i) => {
    const x = (i / 119) * 450;
    const y = 80 + Math.sin(i * 0.15) * 15 + Math.cos(i * 0.4) * 8 + Math.sin(i * 0.05) * 25;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  return (
    <div style={{
      width: '100%',
      background: 'rgba(255, 255, 255, 0.02)',
      border: '1px solid #222222',
      borderRadius: '16px',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          LIVE EEG WAVEFORM PREVIEW (14-CH CH-01)
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: 10, color: 'var(--accent)' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--accent)' }} />
          ACQUISITION ACTIVE
        </span>
      </div>
      <svg viewBox="0 0 450 160" style={{ width: '100%', height: 'auto', background: '#121212', borderRadius: '8px' }}>
        <path d={points} fill="none" stroke="var(--accent)" strokeWidth="1.5" opacity="0.95" />
        {/* Simple grid lines */}
        <line x1="0" y1="80" x2="450" y2="80" stroke="#222" strokeDasharray="2 4" />
        <line x1="150" y1="0" x2="150" y2="160" stroke="#222" strokeDasharray="2 4" />
        <line x1="300" y1="0" x2="300" y2="160" stroke="#222" strokeDasharray="2 4" />
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-dark-secondary)', fontFamily: 'var(--font-mono)' }}>
        <span>0.0s</span>
        <span>1.5s</span>
        <span>3.0s</span>
      </div>
    </div>
  );
}

// Accordion FAQ item component
function FAQItem({ question, answer }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className={`faq-item ${isOpen ? 'faq-item-open' : ''}`}>
      <div className="faq-question" onClick={() => setIsOpen(!isOpen)}>
        <span>{question}</span>
        <span className="faq-toggle">{isOpen ? '−' : '+'}</span>
      </div>
      {isOpen && (
        <div className="faq-answer">
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [selectors, setSelectors] = useState(DEFAULT_SELECTORS);
  const [status, setStatus] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [trialData, setTrialData] = useState(null);
  const [analysisTab, setAnalysisTab] = useState('waveform');

  const apiOnline = status?.dataset_loaded === true;

  // Refs for smooth scrolling
  const consoleRef = useRef(null);
  const analysisRef = useRef(null);
  const faqRef = useRef(null);
  const overviewRef = useRef(null);

  const scrollTo = (ref) => {
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // On mount: fetch API status + metadata
  useEffect(() => {
    api.getStatus()
      .then(s => setStatus(s))
      .catch(() => setStatus({ dataset_loaded: false }));

    api.getMetadata()
      .then(m => {
        setMetadata(m);
        if (m.subjects?.length) {
          const defaultSubj = m.subjects.includes('S39') ? 'S39' : m.subjects[0];
          setSelectors(s => ({ ...s, subject: defaultSubj }));
        }
      })
      .catch(() => {});
  }, []);

  // Load trial data whenever selectors change
  useEffect(() => {
    if (!apiOnline) return;
    api.getTrial(selectors.subject, selectors.condition, selectors.stimulusIdx, selectors.trialIdx, false)
      .then(d => setTrialData(d))
      .catch(() => setTrialData(null));
  }, [selectors, apiOnline]);

  const pageProps = { selectors, metadata, apiOnline, trialData };

  const { subjects = [], conditions = {}, sentences = {} } = metadata || {};

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="top-header">
        <a href="#" className="brand-logo">
          <span className="brand-star" />
          <span>Neurodecode</span>
        </a>
        <nav className="nav-links">
          <button className="nav-link" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>Overview</button>
          <button className="nav-link" onClick={() => scrollTo(overviewRef)}>The Research</button>
          <button className="nav-link" onClick={() => scrollTo(consoleRef)}>Prediction Console</button>
          <button className="nav-link" onClick={() => scrollTo(analysisRef)}>Signal Analysis</button>
          <button className="nav-link" onClick={() => scrollTo(faqRef)}>Methodology & FAQ</button>
        </nav>
      </header>

      {/* Section 1: Hero (Dark) */}
      <section className="section-dark">
        <div className="content-width" style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '60px', alignItems: 'center' }}>
          <div>
            <span className="section-label">EEG RESEARCH PLATFORM</span>
            <h1 className="editorial-heading">
              Decoding Spanish sentences from <span className="highlight">neural</span> signals.
            </h1>
            <p className="body-text" style={{ marginBottom: '36px', color: 'var(--text-dark-secondary)' }}>
              An advanced brain-computer interface system correlating auditory perception and silent production tasks. 
              By targeting 14 language-lateralized left-hemisphere channels, we translate cortical processes into 
              communication vectors.
            </p>
            <button className="btn-pill" onClick={() => scrollTo(consoleRef)}>
              <span className="btn-pill-icon">→</span>
              RUN PREDICTION CONSOLE
            </button>
          </div>
          <HeroWaveform />
        </div>
      </section>

      {/* Section 2: Research Overview & Stats (White) */}
      <section className="section-light" ref={overviewRef}>
        <div className="content-width">
          <span className="section-label">THE RESEARCH</span>
          <h2 className="editorial-heading" style={{ maxWidth: '800px', marginBottom: '60px' }}>
            Translating cortical activity into <span className="highlight">communicative</span> speech vectors.
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px' }}>
            <div className="light-card">
              <span className="stat-number">82.4%</span>
              <span className="stat-desc">Mean Decoder Accuracy across subjects under 5-fold cross-validation.</span>
            </div>
            <div className="light-card">
              <span className="stat-number">+79.1%</span>
              <span className="stat-desc">Decoder accuracy margin achieved above chance levels.</span>
            </div>
            <div className="light-card">
              <span className="stat-number">56</span>
              <span className="stat-desc">Cohort subjects tested under auditory and imagined stimuli conditions.</span>
            </div>
            <div className="light-card">
              <span className="stat-number">14</span>
              <span className="stat-desc">Language-lateralized left-hemisphere channels extracted for feature vectors.</span>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Live Prediction Console (Dark) */}
      <section className="section-dark" ref={consoleRef}>
        <div className="content-width">
          <span className="section-label">PREDICTION CONSOLE</span>
          <h2 className="editorial-heading" style={{ marginBottom: '40px' }}>
            Run live inference on <span className="highlight">imagined</span> speech.
          </h2>

          {/* Session Parameters Selector */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px',
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid var(--border-dark)',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '32px'
          }}>
            <div className="form-group">
              <label className="form-label">Subject</label>
              <select className="select-custom" value={selectors.subject}
                onChange={e => setSelectors(s => ({ ...s, subject: e.target.value }))}>
                {subjects.map(s => <option key={s} value={s}>Subject {s}</option>)}
              </select>
              <div style={{ fontSize: 10, color: 'var(--text-dark-secondary)', marginTop: 4 }}>
                ⭐ High yield subjects: <strong style={{ color: 'var(--accent)' }}>S39</strong>, <strong>S17</strong>, <strong>S25</strong>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Condition</label>
              <select className="select-custom" value={selectors.condition}
                onChange={e => setSelectors(s => ({ ...s, condition: Number(e.target.value) }))}>
                {Object.entries(conditions).map(([key, name], idx) => (
                  <option key={key} value={idx}>{name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Linguistic Stimulus</label>
              <select className="select-custom" value={selectors.stimulusIdx}
                onChange={e => setSelectors(s => ({ ...s, stimulusIdx: Number(e.target.value) }))}>
                {Object.entries(sentences).map(([idx, sentence]) => (
                  <option key={idx} value={idx}>[{idx}] {sentence}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Trial Repetition</label>
              <select className="select-custom" value={selectors.trialIdx}
                onChange={e => setSelectors(s => ({ ...s, trialIdx: Number(e.target.value) }))}>
                {[0,1,2,3,4,5].map(i => <option key={i} value={i}>Trial #{i+1}</option>)}
              </select>
            </div>
          </div>

          {/* Interactive Prediction Dashboard */}
          <PredictionPage {...pageProps} />
        </div>
      </section>

      {/* Section 4: Signal & Preprocessing Analysis (White) */}
      <section className="section-light" ref={analysisRef}>
        <div className="content-width">
          <span className="section-label">SIGNAL ANALYSIS</span>
          <h2 className="editorial-heading" style={{ marginBottom: '40px' }}>
            Explore multi-channel raw and <span className="highlight">preprocessed</span> waveforms.
          </h2>

          {/* Tabs Container */}
          <div className="tab-container">
            <button className={`tab-btn ${analysisTab === 'waveform' ? 'active' : ''}`} onClick={() => setAnalysisTab('waveform')}>
              Waveform Explorer
            </button>
            <button className={`tab-btn ${analysisTab === 'preprocessing' ? 'active' : ''}`} onClick={() => setAnalysisTab('preprocessing')}>
              Signal Preprocessing
            </button>
            <button className={`tab-btn ${analysisTab === 'frequency' ? 'active' : ''}`} onClick={() => setAnalysisTab('frequency')}>
              Frequency Bands
            </button>
            <button className={`tab-btn ${analysisTab === 'topography' ? 'active' : ''}`} onClick={() => setAnalysisTab('topography')}>
              Brain Topography
            </button>
          </div>

          {/* Tab Render Area */}
          <div style={{ minHeight: '400px' }}>
            {analysisTab === 'waveform' && <DatasetExplorer {...pageProps} />}
            {analysisTab === 'preprocessing' && <PreprocessingPage {...pageProps} />}
            {analysisTab === 'frequency' && <FrequencyAnalysisPage {...pageProps} />}
            {analysisTab === 'topography' && <BrainTopographyPage {...pageProps} />}
          </div>
        </div>
      </section>

      {/* Section 5: FAQ & Methodology (White) */}
      <section className="section-light" ref={faqRef} style={{ borderTop: '1px solid var(--border-light)' }}>
        <div className="content-width" style={{ maxWidth: '800px' }}>
          <span className="section-label">FAQ</span>
          <h2 className="editorial-heading" style={{ marginBottom: '40px' }}>
            Frequently asked <span className="highlight">questions</span> about the pipeline.
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <FAQItem 
              question="What BIDS dataset is used for model training?" 
              answer="This project utilizes the ds004279 dataset from OpenNeuro. It contains raw and preprocessed EEG recordings from 56 participants performing auditory perception (listening) and silent production (imagining) of 30 distinct Spanish sentences." 
            />
            <FAQItem 
              question="How does the signal preprocessing pipeline work?" 
              answer="The signal undergoes a robust 5-stage pipeline: (1) Bandpass filtering between 2–50 Hz to remove DC drift and muscle artifact noise, (2) Independent Component Analysis (ICA) to isolate and reject eye-blink artifacts, (3) Common Average Referencing (CAR), (4) Epoch extraction time-locked to stimulus onset (3 seconds), and (5) Z-score normalization per channel." 
            />
            <FAQItem 
              question="What is the architecture of the EEGNet decoder?" 
              answer="EEGNet is a highly compact convolutional neural network specifically optimized for EEG-based Brain-Computer Interfaces. It leverages depthwise and separable convolutions to extract spatial-temporal features directly from lateralized brain activity, requiring far fewer parameters than traditional CNNs." 
            />
            <FAQItem 
              question="How does the zero-shot multilingual retrieval work?" 
              answer="We train a projection layer contrastively to map high-dimensional EEG embeddings directly into a 384-dimensional multilingual SentenceTransformer embedding space. This allows the system to compare the EEG representation with arbitrary custom sentences based on cosine similarity, facilitating zero-shot decoding." 
            />
            <FAQItem 
              question="What are the deployment and hosting details?" 
              answer="The backend API is hosted on Hugging Face Spaces using FastAPI inside a Docker container, which handles downloading the 4.5 GB BIDS dataset and the trained model weights. The frontend is built on React/Vite and hosted on Vercel." 
            />
          </div>
        </div>
      </section>

      {/* Section 6: Footer (Dark) */}
      <footer className="section-dark" style={{ borderTop: '1px solid var(--border-dark)', padding: '60px 80px' }}>
        <div className="content-width" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '40px' }}>
          <div>
            <a href="#" className="brand-logo" style={{ marginBottom: '16px' }}>
              <span className="brand-star" />
              <span>Neurodecode</span>
            </a>
            <p style={{ fontSize: 12, color: 'var(--text-dark-secondary)', lineHeight: 1.6, maxWidth: '300px' }}>
              Open-source brain-computer interface research decoding silent production tasks from BIDS EEG datasets.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '80px', flexWrap: 'wrap' }}>
            <div>
              <h4 style={{ fontSize: 12, color: 'var(--text-dark-primary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>References</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: 12 }}>
                <li><a href="https://openneuro.org/datasets/ds004279" target="_blank" rel="noreferrer" style={{ color: 'var(--text-dark-secondary)', textDecoration: 'none' }}>↗ OpenNeuro ds004279</a></li>
                <li><a href="https://arxiv.org/abs/1611.08024" target="_blank" rel="noreferrer" style={{ color: 'var(--text-dark-secondary)', textDecoration: 'none' }}>↗ EEGNet Publication</a></li>
              </ul>
            </div>
            <div>
              <h4 style={{ fontSize: 12, color: 'var(--text-dark-primary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Repository</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: 12 }}>
                <li><a href="https://huggingface.co/spaces/souravbehera3571/eeg-spanish-speech-decoder" target="_blank" rel="noreferrer" style={{ color: 'var(--text-dark-secondary)', textDecoration: 'none' }}>↗ Hugging Face Space</a></li>
                <li><a href="https://github.com/sourav3571/EEG-converter" target="_blank" rel="noreferrer" style={{ color: 'var(--text-dark-secondary)', textDecoration: 'none' }}>↗ GitHub Source</a></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="content-width" style={{ marginTop: '60px', paddingTop: '20px', borderTop: '1px solid #222222', display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-dark-secondary)' }}>
          <span>© {new Date().getFullYear()} Neurodecode. Open Source Initiative.</span>
          <span>ds004279 · 250 Hz Sampling · 14 Channels</span>
        </div>
      </footer>
    </div>
  );
}
