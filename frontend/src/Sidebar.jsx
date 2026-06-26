import { Brain, LayoutDashboard, Waves, Activity, Map, Cpu, BookOpen, ChevronRight } from 'lucide-react';

const NAV_ITEMS = [
  { id: 'home',         label: 'Overview',          Icon: LayoutDashboard },
  { id: 'explorer',     label: 'Dataset Explorer',   Icon: Waves },
  { id: 'preprocessing',label: 'Signal Preprocessing',Icon: Activity },
  { id: 'frequency',    label: 'Frequency Analysis', Icon: Cpu },
  { id: 'topography',   label: 'Brain Topography',   Icon: Map },
  { id: 'prediction',   label: 'Model Prediction',   Icon: Brain },
  { id: 'about',        label: 'About & Docs',       Icon: BookOpen },
];

export default function Sidebar({ activePage, setActivePage, status, selectors, setSelectors, metadata }) {
  const { subjects = [], conditions = {}, sentences = {} } = metadata || {};

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="brand-header">
        NEURODECODE <span>//</span> ESP
      </div>

      {/* System Status Card */}
      <div style={{
        background: 'var(--bg-card)', border: '1px solid var(--border-default)',
        borderRadius: 8, padding: '14px', marginBottom: 20
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-muted)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            SYSTEM STATUS
          </span>
          {status === null ? (
            <span className="badge badge-warning">Connecting…</span>
          ) : status?.dataset_loaded ? (
            <span className="badge badge-live">LIVE DATA</span>
          ) : (
            <span className="badge badge-offline">DATASET OFFLINE</span>
          )}
        </div>
        {status && (
          <p style={{ fontSize: 11, color: 'var(--text-light)', marginTop: 10, lineHeight: 1.5 }}>
            {status.dataset_loaded
              ? 'Reading trials from ds004279 dataset.'
              : 'Dataset NPZ not found. Run in Docker container for full live mode.'}
          </p>
        )}
      </div>

      {/* Parameter Selectors */}
      {metadata && (
        <div style={{ marginBottom: 20 }}>
          <p className="sidebar-section-title" style={{ marginBottom: 12 }}>Session Parameters</p>

          <div className="form-group">
            <label className="form-label">Subject</label>
            <select className="select-custom" value={selectors.subject}
              onChange={e => setSelectors(s => ({ ...s, subject: e.target.value }))}>
              {subjects.map(s => <option key={s} value={s}>Subject {s}</option>)}
            </select>
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
      )}

      <hr style={{ borderColor: 'var(--border-default)', margin: '0 0 16px 0' }} />

      {/* Navigation */}
      <nav className="nav-menu">
        {NAV_ITEMS.map(({ id, label, Icon }) => (
          <button key={id} onClick={() => setActivePage(id)}
            className={`nav-item ${activePage === id ? 'active' : ''}`}
            style={{ width: '100%', textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer' }}>
            <Icon size={15} className="nav-icon" />
            {label}
            {activePage === id && <ChevronRight size={12} style={{ marginLeft: 'auto', opacity: 0.5 }} />}
          </button>
        ))}
      </nav>

      {/* Bottom footer */}
      <div style={{ marginTop: 'auto', paddingTop: 20, borderTop: '1px solid var(--border-default)' }}>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.6 }}>
          ds004279 · OpenNeuro<br />
          56 Subjects · 14 LH Channels<br />
          250 Hz Sampling Rate
        </p>
      </div>
    </aside>
  );
}