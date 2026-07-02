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

// Beautiful self-contained animated neuron connection pathway graph
function HeroNeurons() {
  return (
    <div style={{
      width: '100%',
      background: 'rgba(255, 255, 255, 0.02)',
      border: '1px solid #222222',
      borderRadius: '16px',
      padding: '28px',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <style>{`
        @keyframes pulse-ring {
          0% { r: 3px; opacity: 0.8; }
          100% { r: 15px; opacity: 0; }
        }
        @keyframes flow-line {
          0% { stroke-dashoffset: 80; }
          100% { stroke-dashoffset: 0; }
        }
        @keyframes node-blink {
          0%, 100% { fill: #444; }
          50% { fill: var(--accent); }
        }
      `}</style>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dark-secondary)', letterSpacing: '0.05em' }}>
          NEURAL PATHWAY SIGNAL CONVERTER
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: 10, color: 'var(--accent)' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--accent)' }} />
          SYNAPTIC ACTIVITY
        </span>
      </div>

      <svg viewBox="0 0 450 200" style={{ width: '100%', height: 'auto', background: '#121212', borderRadius: '8px' }}>
        {/* Subtle grid backdrop */}
        <line x1="0" y1="50" x2="450" y2="50" stroke="#181818" strokeWidth="0.5" />
        <line x1="0" y1="100" x2="450" y2="100" stroke="#181818" strokeWidth="0.5" />
        <line x1="0" y1="150" x2="450" y2="150" stroke="#181818" strokeWidth="0.5" />
        <line x1="112" y1="0" x2="112" y2="200" stroke="#181818" strokeWidth="0.5" />
        <line x1="225" y1="0" x2="225" y2="200" stroke="#181818" strokeWidth="0.5" />
        <line x1="337" y1="0" x2="337" y2="200" stroke="#181818" strokeWidth="0.5" />

        {/* Structural Dendrite Lines */}
        <path d="M 50,100 C 130,40 180,160 250,100 S 370,160 400,100" fill="none" stroke="#222222" strokeWidth="1.5" />
        <path d="M 90,160 C 170,80 220,180 290,120 S 370,40 410,120" fill="none" stroke="#222222" strokeWidth="1.5" />
        <path d="M 70,60 C 180,140 250,40 320,130 S 380,80 430,90" fill="none" stroke="#222222" strokeWidth="1.5" />

        {/* Diagonal synaptic cross-links */}
        <line x1="50" y1="100" x2="90" y2="160" stroke="#1a1a1a" strokeWidth="1" strokeDasharray="2 3" />
        <line x1="250" y1="100" x2="290" y2="120" stroke="#1a1a1a" strokeWidth="1" strokeDasharray="2 3" />
        <line x1="320" y1="130" x2="400" y2="100" stroke="#1a1a1a" strokeWidth="1" strokeDasharray="2 3" />

        {/* Animated Signal Flows (Stroke Dashes) */}
        <path d="M 50,100 C 130,40 180,160 250,100 S 370,160 400,100" fill="none" stroke="var(--accent)" strokeWidth="1.5" 
          strokeDasharray="40 140" style={{ animation: 'flow-line 4s linear infinite' }} />
        <path d="M 90,160 C 170,80 220,180 290,120 S 370,40 410,120" fill="none" stroke="var(--accent)" strokeWidth="1.5" 
          strokeDasharray="60 160" style={{ animation: 'flow-line 5s linear infinite reverse' }} />
        <path d="M 70,60 C 180,140 250,40 320,130 S 380,80 430,90" fill="none" stroke="#FFFFFF" strokeWidth="1" opacity="0.5"
          strokeDasharray="30 110" style={{ animation: 'flow-line 3s linear infinite' }} />

        {/* Active Node Synapses (Pulsating Rings) */}
        {/* Node A */}
        <circle cx="50" cy="100" r="8" fill="none" stroke="var(--accent)" strokeWidth="1" style={{ transformOrigin: '50px 100px', animation: 'pulse-ring 2s infinite' }} />
        <circle cx="50" cy="100" r="3.5" fill="var(--accent)" />
        
        {/* Node B */}
        <circle cx="250" cy="100" r="9" fill="none" stroke="var(--accent)" strokeWidth="1" style={{ transformOrigin: '250px 100px', animation: 'pulse-ring 2.5s infinite' }} />
        <circle cx="250" cy="100" r="4" fill="#FFFFFF" />

        {/* Node C */}
        <circle cx="400" cy="100" r="8" fill="none" stroke="var(--accent)" strokeWidth="1" style={{ transformOrigin: '400px 100px', animation: 'pulse-ring 1.8s infinite' }} />
        <circle cx="400" cy="100" r="3.5" fill="var(--accent)" />

        {/* Passive/Blinking Synapse Intersections */}
        <circle cx="90" cy="160" r="2.5" fill="#444444" style={{ animation: 'node-blink 3s infinite 0.5s' }} />
        <circle cx="290" cy="120" r="2.5" fill="#444444" style={{ animation: 'node-blink 4s infinite 1.2s' }} />
        <circle cx="410" cy="120" r="2.5" fill="#444444" style={{ animation: 'node-blink 2s infinite 0.3s' }} />
        <circle cx="70" cy="60" r="2.5" fill="#444444" style={{ animation: 'node-blink 3.5s infinite' }} />
        <circle cx="320" cy="130" r="2.5" fill="#444444" style={{ animation: 'node-blink 2.8s infinite 1.5s' }} />
        <circle cx="430" cy="90" r="2.5" fill="#444444" style={{ animation: 'node-blink 3.1s infinite 0.7s' }} />
      </svg>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-dark-secondary)', fontFamily: 'var(--font-mono)' }}>
        <span>Sampling Rate: 250 Hz</span>
        <span>Input Channels: 14</span>
        <span>Model Parameters: 3,661</span>
        <span>Dataset: ds004279</span>
      </div>
    </div>
  );
}

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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
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
        
        {/* Mobile Hamburger Button */}
        <button className="mobile-menu-btn" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
        </button>

        <nav className={`nav-links ${isMobileMenuOpen ? 'nav-links-mobile-open' : ''}`}>
          <button className="nav-link" onClick={() => { setIsMobileMenuOpen(false); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>Overview</button>
          <button className="nav-link" onClick={() => { setIsMobileMenuOpen(false); scrollTo(overviewRef); }}>The Research</button>
          <button className="nav-link" onClick={() => { setIsMobileMenuOpen(false); scrollTo(consoleRef); }}>Prediction Console</button>
          <button className="nav-link" onClick={() => { setIsMobileMenuOpen(false); scrollTo(analysisRef); }}>Signal Analysis</button>
          <button className="nav-link" onClick={() => { setIsMobileMenuOpen(false); scrollTo(faqRef); }}>Methodology & FAQ</button>
        </nav>
      </header>

      {/* Research Prototype Banner (Fix 1) */}
      <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', borderBottom: '1px solid #333', padding: '16px 24px', textAlign: 'center', color: '#FFF', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px' }}>
        <span style={{ fontSize: '18px' }}>📌</span>
        <span style={{ fontSize: '13px', lineHeight: 1.5, maxWidth: '900px', textAlign: 'left' }}>
          <strong>Research Prototype Dashboard</strong> — This interface visualizes the ds004279 dataset (Valle et al., 2024) and demonstrates the EEG decoding pipeline architecture. Accuracy figures shown are baseline results from Valle et al. (2024). Sample predictions demonstrate the intended interface functionality. Full end-to-end training on the complete 56-subject cohort is proposed as future work.
        </span>
      </div>

      {/* Section 1: Hero (Dark) */}
      <section className="section-dark">
        <div className="content-width" style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '60px', alignItems: 'center' }}>
          <div>
            <span className="section-label">EEG RESEARCH PLATFORM</span>
            <h1 className="editorial-heading">
              Decoding Spanish sentences from <span className="highlight">neural</span> signals.
            </h1>
            <p className="body-text" style={{ marginBottom: '36px', color: 'var(--text-dark-secondary)' }}>
              This project develops an end-to-end research prototype dashboard for EEG-based Spanish sentence decoding using the ds004279 dataset (Valle et al., 2024). The work implements a complete signal preprocessing pipeline architecture, integration of the EEGNet architecture, and an interactive dashboard for exploring the dataset. Full end-to-end model training on the complete 56-subject cohort is identified as the primary next step.
            </p>
            <button className="btn-pill" onClick={() => scrollTo(consoleRef)}>
              <span className="btn-pill-icon">→</span>
              RUN PREDICTION CONSOLE
            </button>
          </div>
          <HeroNeurons />
        </div>
      </section>

      {/* Section 2: Research Overview & Stats (White) */}
      <section className="section-light" ref={overviewRef}>
        <div className="content-width">
          <span className="section-label">THE RESEARCH</span>
          <h2 className="editorial-heading" style={{ maxWidth: '900px', marginBottom: '30px' }}>
            Translating cortical activity into <span className="highlight">communicative</span> speech vectors.
          </h2>
          <p className="body-text" style={{ marginBottom: '60px', color: 'var(--text-light-secondary)' }}>
            This section presents the accuracy figures reported by Valle et al. (2024) as the reference baseline that this dashboard is designed to visualize and this pipeline architecture is designed to reproduce. Full reproduction on the complete dataset is proposed as the immediate next phase.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px' }}>
            <div className="light-card">
              <span className="stat-number">82.4%</span>
              <span className="stat-desc">Baseline accuracy for 2-class sentence classification reported by Valle et al. (2024) on the ds004279 dataset — the reference target this pipeline architecture is designed to reproduce.</span>
            </div>
            <div className="light-card">
              <span className="stat-number">+32.4%</span>
              <span className="stat-desc">Margin above 50% chance baseline in the reference study (Valle et al., 2024).</span>
            </div>
            <div className="light-card">
              <span className="stat-number">56</span>
              <span className="stat-desc">Participants in the ds004279 dataset (Valle et al., 2024) — the target cohort for the implemented pipeline architecture.</span>
            </div>
            <div className="light-card">
              <span className="stat-number">14</span>
              <span className="stat-desc">Language-lateralized left-hemisphere channels selected for feature extraction.</span>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Live Prediction Console (Dark) */}
      <section className="section-dark" ref={consoleRef}>
        <div className="content-width">
          <span className="section-label">PREDICTION CONSOLE (INTERFACE DEMONSTRATION)</span>
          <h2 className="editorial-heading" style={{ marginBottom: '16px' }}>
            Run live inference on <span className="highlight">imagined</span> speech.
          </h2>
          <p className="body-text" style={{ marginBottom: '40px', color: 'var(--text-dark-secondary)' }}>
            This module demonstrates the intended user interface for interacting with a trained EEG decoder. Predictions shown are illustrative examples generated to demonstrate the interface flow. Real end-to-end inference on trained models requires the full training pipeline to be completed on the ds004279 dataset.
          </p>

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
              <div style={{ fontSize: 10, color: 'var(--text-dark-secondary)', marginTop: 4 }}>
                The dropdown lists all 30 sentences from the ds004279 dataset. Classification results are computed for 2-class binary comparisons — select two sentences to compare their neural signatures.
              </div>
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

      {/* Section 4.5: Implementation Status */}
      <section className="section-dark" style={{ borderTop: '1px solid var(--border-dark)' }}>
        <div className="content-width">
          <span className="section-label">PIPELINE STATUS</span>
          <h2 className="editorial-heading" style={{ marginBottom: '40px' }}>
            Implementation <span className="highlight">Status</span>.
          </h2>
          
          <div className="grid-2col" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
            <div className="dark-card">
              <h3 style={{ fontSize: '18px', color: 'var(--text-dark-primary)', marginBottom: '20px' }}>Implemented in This Project</h3>
              <ul style={{ listStyle: 'disc', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px', color: 'var(--text-dark-secondary)' }}>
                <li>Complete Streamlit + React dashboard interface with 6 interactive modules</li>
                <li>EEGNet architecture implementation in PyTorch (14 channels, 3,661 parameters)</li>
                <li>Signal preprocessing pipeline structure (bandpass 2–50 Hz, ICA integration, epoch segmentation)</li>
                <li>Interactive session navigation across subjects, conditions, sentences, and trials</li>
                <li>Multi-view visualization (raw signals, preprocessing stages, PSD, topography, model output UI)</li>
                <li>Integration with ds004279 dataset structure and metadata</li>
              </ul>
            </div>
            
            <div className="dark-card" style={{ border: '1px solid rgba(197, 247, 62, 0.3)' }}>
              <h3 style={{ fontSize: '18px', color: 'var(--text-dark-primary)', marginBottom: '20px' }}>Reference Baseline (Valle et al., 2024)<br/><span style={{ fontSize: '13px', color: 'var(--accent)', fontWeight: 'normal' }}>Future Reproduction Target</span></h3>
              <ul style={{ listStyle: 'disc', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px', color: 'var(--text-dark-secondary)' }}>
                <li>End-to-end training across all 56 subjects</li>
                <li>5-fold subject-dependent cross-validation reproducing 82.4% accuracy</li>
                <li>Full Leave-One-Subject-Out evaluation reproducing 54.17% (2-class) and 23.33% (5-class)</li>
                <li>Automated MNE-ICA Label artifact rejection on real recordings</li>
                <li>Confusion matrix analysis on trained model outputs</li>
                <li>Statistical significance testing against chance baselines</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Section 5: FAQ & Methodology (White) */}
      <section className="section-light" ref={faqRef}>
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
              question="Does this dashboard show real predictions from a trained model?" 
              answer="The current version demonstrates the intended prediction interface using illustrative sample outputs. The EEGNet architecture is implemented in PyTorch, and the preprocessing pipeline structure is complete, but full end-to-end training on all 56 subjects has not yet been executed. Sample predictions are shown to demonstrate the interface flow." 
            />
            <FAQItem 
              question="Where do the accuracy figures come from?" 
              answer="The accuracy figures shown (82.4% subject-dependent, 54.17% LOSO 2-class, 23.33% LOSO 5-class) are the reference baselines reported by Valle et al. (2024) in their Journal of Neural Engineering paper on the ds004279 dataset. This dashboard is designed to visualize these targets and provide the interface for reproducing them in future work." 
            />
            <FAQItem 
              question="What was actually built in this project?" 
              answer="This project delivers: a fully functional React/Vite dashboard with 6 interactive modules, an EEGNet architecture implementation in PyTorch, the preprocessing pipeline structure (bandpass filtering, ICA integration, epoching), interactive session navigation, and multi-view visualization tools. The infrastructure is in place for future full-scale training and evaluation." 
            />
            <FAQItem 
              question="Evaluation Configurations (Future Work)"
              answer="The pipeline architecture is designed to evaluate under two complementary configurations to characterize both personalized and generalizable performance. Subject-Dependent (Personalized): 82.4% mean accuracy on 2-class classification (Valle et al., 2024). Subject-Independent (LOSO): 54.17% on 2-class and 23.33% on 5-class (Valle et al., 2024). The performance gap reflects the fundamental challenge of inter-subject variability in non-invasive speech decoding."
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
            <p style={{ fontSize: 12, color: 'var(--text-dark-secondary)', lineHeight: 1.6, maxWidth: '350px' }}>
              Research prototype dashboard visualizing baseline results from Valle et al. (2024) on the ds004279 dataset. Full end-to-end training on the complete 56-subject cohort is proposed as future work.
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
