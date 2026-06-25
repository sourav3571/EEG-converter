@echo off
echo ===================================================
echo   EEG Spanish Decoder — Hugging Face Space Deployer
echo ===================================================
echo.
echo Remote is already configured to:
git remote get-url hf
echo.
echo Starting deployment push...
echo.
echo [IMPORTANT] The 4.5 GB dataset is tracked via Git LFS. Pushing will take 
echo several minutes (or longer) depending on your internet upload bandwidth.
echo.
echo When prompted for credentials:
echo   - Username: souravbehera3571
echo   - Password: Use a Hugging Face Access Token (with WRITE permission)
echo.

git push hf main --force

echo.
echo ===================================================
echo   Push complete!
echo   Go to https://huggingface.co/spaces/souravbehera3571/eeg-spanish-speech-decoder
echo   to monitor the build progress.
echo ===================================================
echo.
pause
