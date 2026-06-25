// Central API client — points to the Hugging Face Spaces FastAPI backend
const API_BASE = import.meta.env.VITE_API_URL || 'https://souravbehera3571-eeg-spanish-speech-decoder.hf.space';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } });
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errBody.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  getStatus: () => request('/api/status'),
  getMetadata: () => request('/api/metadata'),
  getTrial: (subject, condition, stimulusIdx, trialIdx, preprocess = true) =>
    request(`/api/trial?subject=${subject}&condition=${condition}&stimulus_idx=${stimulusIdx}&trial_idx=${trialIdx}&preprocess=${preprocess}`),
  decode: (body) =>
    request('/api/decode', { method: 'POST', body: JSON.stringify(body) }),
  decodeZeroShot: (body) =>
    request('/api/decode-zero-shot', { method: 'POST', body: JSON.stringify(body) }),
  getHistory: () => request('/api/history'),
};
