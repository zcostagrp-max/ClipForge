# ClipForge

AI-powered video clipping app. Paste a YouTube / TikTok / Instagram / direct video URL and get 5–12 polished vertical short clips with burned-in captions.

## Features

- URL ingestion via yt-dlp (YouTube, Twitch, TikTok, Instagram, direct MP4)
- Local transcription with faster-whisper (word-level timestamps)
- AI highlight detection (Claude 3.5 Sonnet / GPT-4o, with heuristic fallback)
- Automatic 9:16 crop + Bangers-style captions (white text, black outline, 4–6 words/line)
- Clean Next.js dashboard with live progress
- Download / preview clips

## Tech Stack

- **Frontend**: Next.js 15 (App Router) + TypeScript + Tailwind
- **Backend**: FastAPI + BackgroundTasks
- **Video**: yt-dlp + ffmpeg
- **Transcription**: faster-whisper
- **Storage**: Local filesystem (easy to swap for S3)
- **DB**: SQLite

## Quick Start (Local)

### Prerequisites

- Python 3.10+
- Node.js 18+
- ffmpeg installed (`brew install ffmpeg` or `apt install ffmpeg`)
- (Optional) GPU for faster transcription

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and/or ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

First transcription will download the Whisper model (base is recommended for MVP).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### 3. Docker (optional)

```bash
docker compose up --build
```

## Deploy Frontend to Netlify

The Next.js frontend is ready for Netlify. The heavy Python backend (yt-dlp + ffmpeg + Whisper) must be hosted separately (Railway, Render, Fly.io, etc.).

### 1. Deploy Backend first (example: Railway)

- Push the `backend/` folder to a Railway project
- Set environment variables from `backend/.env.example`
- Note the public URL (e.g. `https://clipforge-api.up.railway.app`)
- CORS already allows `*.netlify.app` origins

### 2. Deploy Frontend to Netlify

1. Push this repo to GitHub
2. In Netlify: **Add new site → Import from Git**
3. Set **Base directory** to `frontend`
4. Build command: `npm run build`
5. Publish directory: leave blank (Netlify Next.js plugin handles it)
6. Add environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: your backend URL (from step 1)
7. Deploy

The `frontend/netlify.toml` configures the Next.js plugin and Node 20.

### Local Netlify preview

```bash
cd frontend
npm install -g netlify-cli
netlify dev
```

## Environment Variables

See `backend/.env.example` and `frontend/.env.example`

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for best highlight detection
- Without keys, a keyword heuristic is used
- `WHISPER_MODEL_SIZE=base` (or `small` / `tiny` for speed)
- `NEXT_PUBLIC_API_URL` — points the frontend at your backend

## API Endpoints

- `POST /api/jobs` — start job `{ "url": "https://..." }`
- `GET /api/jobs/{id}` — status + clips
- `GET /api/clips/{id}/download` — download MP4
- `POST /api/clips/{id}/rerender` — re-cut with new start/end

## Caption Style

Captions use the Bangers font style:
- Big white text
- Thick black outline
- Max ~5 words per line
- Positioned in the lower-middle (above typical Instagram username bar)

## Notes

- Videos up to ~3 hours are supported (transcription time depends on hardware)
- Private / geo-restricted videos will fail gracefully
- For production, swap local storage for S3 and add Celery + Redis for job queue
- Rerender is partially implemented (stores new times; full re-render requires original video path)

## License

MIT
