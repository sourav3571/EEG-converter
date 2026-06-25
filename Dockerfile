# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# EEG Imagined Spanish Sentence Decoder
# Large files (dataset + models) are stored in:
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

# Install Python packages (CPU-only PyTorch to keep image size manageable)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir huggingface_hub && \
    pip install --no-cache-dir -r requirements.txt \
        --extra-index-url https://download.pytorch.org/whl/cpu

# Copy all application code
COPY --chown=user:user . /app

# Download large files from HF Model repo at build time
# Dataset (4.5 GB) + Model weights (~1 MB each x 61 subjects)
RUN python -c " \
from huggingface_hub import snapshot_download; \
import os; \
print('Downloading dataset and model weights from HF Model repo...'); \
snapshot_download( \
    repo_id='souravbehera3571/eeg-spanish-speech-decoder-data', \
    local_dir='/app/Large_Spanish_EEG', \
    repo_type='model', \
    ignore_patterns=['*.git*', '*.gitattributes'] \
); \
print('Download complete!') \
"

# Switch to non-root user
USER user

# Expose port 7860 for Hugging Face Spaces
EXPOSE 7860

# Run the Streamlit app on port 7860
CMD ["streamlit", "run", "eeg_dashboard/app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]
