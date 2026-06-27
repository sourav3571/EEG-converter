#!/bin/bash
echo "Starting EEG Decoder Backend (FastAPI on http://localhost:7860)..."
uvicorn eeg_dashboard.api_server:app --reload --port 7860 &
BACKEND_PID=$!

echo "Starting EEG Decoder Frontend (React/Vite)..."
cd frontend
npm run dev

# Terminate backend when frontend exits
kill $BACKEND_PID
