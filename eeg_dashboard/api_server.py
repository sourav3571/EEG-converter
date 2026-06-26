import os
import sys
import numpy as np
import torch
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Add the directory containing api_server.py to sys.path so we can import eeg_dashboard files
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from config import settings
from utils import data_loader, preprocessor, model_loader

app = FastAPI(
    title="EEG Spanish Speech Decoder API",
    description="REST API backend for decoding imagined Spanish speech from left-hemisphere EEG signals.",
    version="1.0.0"
)

# Enable CORS for frontend deployment (e.g. Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Map integer condition index → string key used in NPZ dataset
CONDITION_MAP = {
    0: "perception",
    1: "production",
    2: "rest",
    3: "preparation"
}

def map_condition(condition):
    """Convert integer condition to string key used in NPZ data."""
    if isinstance(condition, int):
        return CONDITION_MAP.get(condition, "perception")
    return condition

# Global database holder
NPZ_FILENAME = "language_average_2-50hz_icaLabel95confidence_eyes_60sessions.npz"
_candidate_paths = [
    os.path.join(current_dir, "../Large_Spanish_EEG/data/npz/" + NPZ_FILENAME),        # local development
    "/app/Large_Spanish_EEG/data/npz/" + NPZ_FILENAME,      # HF Spaces Docker
]
npz_path = next((p for p in _candidate_paths if os.path.exists(p)), None)

real_data = None
if npz_path:
    print(f"Loading BIDS EEG dataset from: {npz_path}")
    try:
        real_data = data_loader.load_real_dataset(npz_path)
        print("BIDS EEG dataset loaded successfully.")
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
else:
    print("WARNING: BIDS EEG dataset not found. API is offline for signal retrieval.")


class DecodeRequest(BaseModel):
    subject: str
    condition: int
    stimulus_idx: int
    trial_idx: int

class ContrastiveDecodeRequest(BaseModel):
    subject: str
    condition: int
    stimulus_idx: int
    trial_idx: int
    custom_sentences: Optional[List[str]] = None


@app.get("/")
def read_root():
    return {
        "title": "EEG Spanish Speech Decoder API",
        "status": "online",
        "dataset_loaded": real_data is not None,
        "docs_url": "/docs"
    }


@app.get("/api/status")
def get_status():
    # Detect which subject models are available
    _model_bases = [
        os.path.join(current_dir, "../Large_Spanish_EEG/models"),
        "/app/Large_Spanish_EEG/models",
    ]
    _model_base = next((b for b in _model_bases if os.path.isdir(b)), "../Large_Spanish_EEG/models")
    
    available_subjects = []
    if os.path.isdir(_model_base):
        for f in os.listdir(_model_base):
            if f.startswith("eegnet_subj_") and f.endswith("_stims2.pth"):
                parts = f.split("_")
                if len(parts) >= 3:
                    available_subjects.append(parts[2])
                    
    return {
        "dataset_loaded": real_data is not None,
        "dataset_path": npz_path,
        "models_directory": _model_base,
        "available_subject_specific_models": sorted(list(set(available_subjects))),
        "contrastive_model_available": os.path.exists(os.path.join(_model_base, "eegnet_contrastive.pth"))
    }


@app.get("/api/metadata")
def get_metadata():
    return {
        "subjects": settings.SUBJECTS,
        "conditions": settings.CONDITIONS,
        "sentences": settings.SENTENCES,
        "sentences_english": settings.SENTENCES_ENGLISH,
        "channels": settings.CHANNELS,
        "brain_regions": settings.CHANNEL_REGIONS
    }


@app.get("/api/trial")
def get_trial(
    subject: str = Query(..., description="Subject ID, e.g. 01"),
    condition: int = Query(..., description="Condition index, e.g. 0 (perception) or 1 (production)"),
    stimulus_idx: int = Query(..., description="Stimulus index, 1-30"),
    trial_idx: int = Query(..., description="Trial index, 0-5"),
    preprocess: bool = Query(True, description="Whether to apply the preprocessing pipeline")
):
    if real_data is None:
        raise HTTPException(
            status_code=503,
            detail="Scientific BIDS EEG dataset is offline. Please ensure dataset is downloaded."
        )
    
    # Map integer condition → string
    condition_str = map_condition(condition)
        
    eeg_raw = data_loader.get_real_trial_data(
        real_data, subject, condition_str, stimulus_idx, trial_idx
    )
    
    if eeg_raw is None:
        raise HTTPException(
            status_code=404,
            detail=f"Trial data not found for Subject {subject}, Condition {condition_str}, Stimulus {stimulus_idx}, Trial {trial_idx}"
        )
        
    metadata = data_loader.get_demo_subject_metadata(subject, condition_str, stimulus_idx, trial_idx)
    
    response = {
        "metadata": metadata,
        "raw_signal": eeg_raw.tolist(),
        "channels": settings.CHANNELS,
        "sampling_rate": settings.SAMPLING_RATE,
        "timepoints": int(settings.SAMPLING_RATE * settings.TRIAL_DURATION)
    }
    
    if preprocess:
        # Run preprocessing pipeline
        seed = hash(f"{subject}_{condition_str}_{stimulus_idx}_{trial_idx}") % 100000
        eeg_clean, stats = preprocessor.run_preprocessing_pipeline(eeg_raw, seed=seed)
        response["clean_signal"] = eeg_clean.tolist()
        response["preprocessing_stats"] = stats
        
    return response


@app.post("/api/decode")
def decode_trial(req: DecodeRequest):
    if real_data is None:
        raise HTTPException(
            status_code=503,
            detail="Scientific BIDS EEG dataset is offline. Cannot perform inference."
        )
    
    # Map integer condition → string
    condition_str = map_condition(req.condition)
        
    eeg_raw = data_loader.get_real_trial_data(
        real_data, req.subject, condition_str, req.stimulus_idx, req.trial_idx
    )
    
    if eeg_raw is None:
        raise HTTPException(
            status_code=404,
            detail=f"Trial data not found for Subject {req.subject}, Condition {condition_str}, Stimulus {req.stimulus_idx}, Trial {req.trial_idx}"
        )
        
    # Preprocess
    seed = hash(f"{req.subject}_{condition_str}_{req.stimulus_idx}_{req.trial_idx}") % 100000
    eeg_clean, _ = preprocessor.run_preprocessing_pipeline(eeg_raw, seed=seed)
    
    # Run prediction
    res = model_loader.predict_trial(
        eeg_clean, req.subject, condition_str, true_label_idx=(req.stimulus_idx - 1), seed=seed
    )
    
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
        
    # Convert numpy array to list for JSON response
    if "probabilities" in res and isinstance(res["probabilities"], np.ndarray):
        res["probabilities"] = res["probabilities"].tolist()
    if "explanations" in res:
        if "time_saliency" in res["explanations"] and isinstance(res["explanations"]["time_saliency"], np.ndarray):
            res["explanations"]["time_saliency"] = res["explanations"]["time_saliency"].tolist()
            
    return res


@app.post("/api/decode-zero-shot")
def decode_contrastive(req: ContrastiveDecodeRequest):
    if real_data is None:
        raise HTTPException(
            status_code=503,
            detail="Scientific BIDS EEG dataset is offline. Cannot perform inference."
        )
    
    # Map integer condition → string
    condition_str = map_condition(req.condition)
        
    eeg_raw = data_loader.get_real_trial_data(
        real_data, req.subject, condition_str, req.stimulus_idx, req.trial_idx
    )
    
    if eeg_raw is None:
        raise HTTPException(
            status_code=404,
            detail=f"Trial data not found for Subject {req.subject}, Condition {condition_str}, Stimulus {req.stimulus_idx}, Trial {req.trial_idx}"
        )
        
    # Preprocess
    seed = hash(f"{req.subject}_{condition_str}_{req.stimulus_idx}_{req.trial_idx}_zero") % 100000
    eeg_clean, _ = preprocessor.run_preprocessing_pipeline(eeg_raw, seed=seed)
    
    # Run contrastive retrieval prediction
    res = model_loader.predict_contrastive_trial(
        eeg_clean, req.subject, condition_str, 
        true_label_idx=(req.stimulus_idx - 1),
        custom_sentences=req.custom_sentences,
        seed=seed
    )
    
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
        
    # Format outputs for JSON serialization
    if "standard_similarities" in res and isinstance(res["standard_similarities"], np.ndarray):
        res["standard_similarities"] = res["standard_similarities"].tolist()
    if "explanations" in res:
        if "time_saliency" in res["explanations"] and isinstance(res["explanations"]["time_saliency"], np.ndarray):
            res["explanations"]["time_saliency"] = res["explanations"]["time_saliency"].tolist()
            
    return res


@app.get("/api/history")
def get_history():
    history_data = model_loader.get_training_history()
    return history_data