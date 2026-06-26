import os
import sys
from huggingface_hub import HfApi

api = HfApi()
repo_id = "souravbehera3571/eeg-spanish-speech-decoder-data"
local_file = r"D:\EEG decoder\Large_Spanish_EEG\data\npz\language_average_2-50hz_icaLabel95confidence_eyes_60sessions.npz"
repo_path = "data/npz/language_average_2-50hz_icaLabel95confidence_eyes_60sessions.npz"

print(f"Initializing Hugging Face LFS upload for {local_file}...", flush=True)
if not os.path.exists(local_file):
    print(f"Error: Local file not found at {local_file}", file=sys.stderr, flush=True)
    sys.exit(1)

try:
    api.upload_file(
        path_or_fileobj=local_file,
        path_in_repo=repo_path,
        repo_id=repo_id,
        repo_type="model",
    )
    print("SUCCESS: Upload completed!", flush=True)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr, flush=True)
    sys.exit(1)
