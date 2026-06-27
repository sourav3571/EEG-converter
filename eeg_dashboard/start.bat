@echo off
echo Starting EEG Decoder Backend (FastAPI on http://localhost:7860)...
start "EEG Backend" cmd /k "uvicorn api_server:app --reload --port 7860"

echo Starting EEG Decoder Frontend (React/Vite)...
cd ../frontend
npm run dev
