import { useState, useEffect } from 'react';
import './App.css';
import { api } from './api';
import Sidebar from './Sidebar';
import HomePage from './pages/HomePage';
import DatasetExplorer from './pages/DatasetExplorer';
import PreprocessingPage from './pages/PreprocessingPage';
import FrequencyAnalysisPage from './pages/FrequencyAnalysisPage';
import BrainTopographyPage from './pages/BrainTopographyPage';
import PredictionPage from './pages/PredictionPage';
import AboutPage from './pages/AboutPage';

const DEFAULT_SELECTORS = {
  subject: '01',
  condition: 0,
  stimulusIdx: 1,
  trialIdx: 0,
};

export default function App() {
  const [activePage, setActivePage] = useState('home');
  const [selectors, setSelectors] = useState(DEFAULT_SELECTORS);
  const [status, setStatus] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [trialData, setTrialData] = useState(null); // shared across topo / freq pages

  const apiOnline = status?.dataset_loaded === true;

  // On mount: fetch API status + metadata
  useEffect(() => {
    api.getStatus()
      .then(s => setStatus(s))
      .catch(() => setStatus({ dataset_loaded: false }));

    api.getMetadata()
      .then(m => {
        setMetadata(m);
        // Set default subject from first available
        if (m.subjects?.length) {
          const defaultSubj = m.subjects.includes('S39') ? 'S39' : m.subjects[0];
          setSelectors(s => ({ ...s, subject: defaultSubj }));
        }
      })
      .catch(() => {});
  }, []);

  // Load trial data whenever selectors change (used by topo + freq pages)
  useEffect(() => {
    if (!apiOnline) return;
    api.getTrial(selectors.subject, selectors.condition, selectors.stimulusIdx, selectors.trialIdx, false)
      .then(d => setTrialData(d))
      .catch(() => setTrialData(null));
  }, [selectors, apiOnline]);

  const pageProps = { selectors, metadata, apiOnline, trialData };

  return (
    <div className="app-container">
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        status={status}
        selectors={selectors}
        setSelectors={setSelectors}
        metadata={metadata}
      />
      <main className="main-content">
        {activePage === 'home'          && <HomePage {...pageProps} setActivePage={setActivePage} />}
        {activePage === 'explorer'      && <DatasetExplorer {...pageProps} />}
        {activePage === 'preprocessing' && <PreprocessingPage {...pageProps} />}
        {activePage === 'frequency'     && <FrequencyAnalysisPage {...pageProps} />}
        {activePage === 'topography'    && <BrainTopographyPage {...pageProps} />}
        {activePage === 'prediction'    && <PredictionPage {...pageProps} />}
        {activePage === 'about'         && <AboutPage />}
      </main>
    </div>
  );
}
