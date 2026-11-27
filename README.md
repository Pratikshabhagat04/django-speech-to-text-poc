# Speech Studio – Speech to Text POC

A Django web application for near-real-time Hindi, English and multilingual speech transcription using Faster-Whisper, Django Channels, WebSockets and SQLite.

## Features

- Browser microphone recording
- Audio chunks transmitted over WebSocket
- Local Faster-Whisper transcription
- Automatic language detection
- Hindi and English transcription support
- SQLite persistence
- Dashboard with search and transcription history
- Create, read, update and delete transcription records

## Requirements

- Python 3.10 or newer
- FFmpeg installed and available on PATH
- Microphone-enabled browser
- Internet connection for initial Python packages and model download

## Setup on Windows

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd speech_to_text_poc

python -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations transcriptions
python manage.py migrate
python manage.py createsuperuser

daphne -b 127.0.0.1 -p 8000 speech_project.asgi:application
```

Open http://127.0.0.1:8000/

## Setup on macOS/Linux

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd speech_to_text_poc

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations transcriptions
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 speech_project.asgi:application
```

## FFmpeg installation

Windows: install an FFmpeg build and add its `bin` directory to PATH.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

macOS:

```bash
brew install ffmpeg
```

Verify:

```bash
ffmpeg -version
```

## Whisper model configuration

The default model is `base`, which is a reasonable CPU POC choice. The first transcription downloads the model.

Windows PowerShell:

```powershell
$env:WHISPER_MODEL="small"
$env:WHISPER_DEVICE="cpu"
$env:WHISPER_COMPUTE_TYPE="int8"
```

For a GPU server with compatible CUDA libraries:

```bash
WHISPER_MODEL=small
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
```

Available model sizes include `tiny`, `base`, `small`, `medium` and `large-v3`. Larger models generally improve quality but require more compute and memory.

## How it works

1. The browser requests microphone permission.
2. MediaRecorder captures audio and emits WebM/Opus chunks every five seconds.
3. The browser sends the chunks over a WebSocket connection.
4. Django Channels appends the chunks to the current recording.
5. Faster-Whisper transcribes the accumulated audio on the server.
6. The latest transcript and detected language are returned to the browser.
7. When the user stops recording, the final transcript is saved in SQLite.
8. The dashboard displays saved records and provides CRUD operations.

## Important POC limitations

- This is near-real-time chunked transcription, not word-level streaming.
- The server reprocesses the accumulated recording after each chunk. This is simple for a POC but inefficient for long recordings.
- WebM/Opus decoding depends on FFmpeg.
- The in-memory Channels layer is intended for local single-process development. Use Redis for a multi-worker production deployment.
- The sample project does not include user authentication, rate limiting, audio retention, or production-grade access controls.
- Microphone access generally requires HTTPS when deployed, except on localhost.
- Automatic language detection can identify a dominant language, but mixed Hindi-English spelling and script selection can vary with the model.

## Production improvements

- Use Redis as the Channels layer.
- Add authentication and per-user transcription ownership.
- Use PostgreSQL for multi-user deployment.
- Add recording duration and file-size limits.
- Use a background task queue for model inference.
- Store only transcript text unless audio retention is explicitly required.
- Add HTTPS, environment-based secrets, logging and monitoring.

## GitHub publishing

```bash
git init
git add .
git commit -m "Initial speech to text POC"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/speech-to-text-poc.git
git push -u origin main
```

## Deployment

Deploy on a VM or container host that supports persistent disk, WebSockets, FFmpeg and sufficient RAM/CPU. Configure `ALLOWED_HOSTS`, `DEBUG=False`, a secure `SECRET_KEY`, HTTPS and a Redis channel layer before public deployment. A small server may need the `tiny` or `base` model.
