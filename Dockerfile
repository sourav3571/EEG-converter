# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# EEG Imagined Spanish Sentence Decoder — Full Live Mode
# Dataset (4.5 GB) + Model weights are downloaded from:
#   https://huggingface.co/souravbehera3571/eeg-spanish-speech-decoder-data

FROM python:3.12-slim

# Set environmental variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with UID 1000 (required by HF Spaces)
RUN useradd -m -u 1000 user

# Set working directory
WORKDIR /app

# Copy requirements first (layer cache optimization)
COPY --chown=user:user requirements.txt /app/requirements.txt

# Install Python packages (CPU-only PyTorch)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir huggingface_hub && \
    pip install --no-cache-dir -r requirements.txt \
        --extra-index-url https://download.pytorch.org/whl/cpu

# Copy all application code
COPY --chown=user:user . /app

# Download EVERYTHING from the HF Model repo:
#   - data/npz/*.npz  → 4.5 GB real EEG dataset (enables Live Data Mode)
#   - models/*.pth    → 61 trained EEGNet subject weights (enables real predictions)
RUN python -c "\
from huggingface_hub import snapshot_download; \
print('Downloading full EEG dataset + model weights from HF...'); \
snapshot_download( \
    repo_id='souravbehera3571/eeg-spanish-speech-decoder-data', \
    local_dir='/app/Large_Spanish_EEG', \
    repo_type='model' \
); \
print('All files downloaded — Live Data Mode enabled!') \
"

# Switch to non-root user
USER user

# Expose port 7860 for Hugging Face Spaces
EXPOSE 7860

# Run the FastAPI app on port 7860
CMD ["uvicorn", "eeg_dashboard.api_server:app", "--host", "0.0.0.0", "--port", "7860"]
