# ClipForge

AI-powered video clipping app. Paste a YouTube / TikTok / Instagram / direct video URL and get polished vertical short clips with burned-in captions.

## Deploy to Netlify (recommended)

1. Push this repo to GitHub (already done: https://github.com/zcostagrp-max/ClipForge)
2. In Netlify → **Add new site → Import from Git**
3. Select the repo
4. **Base directory**: `frontend`
5. **Build command**: `npm run build`
6. **Publish directory**: `.next`
7. Deploy

The site will work immediately in **demo mode** (simulated progress + sample clips).

To connect a real backend later, add this environment variable in Netlify:
- Key: `NEXT_PUBLIC_API_URL`
- Value: your FastAPI backend URL (e.g. `https://your-api.railway.app`)

## Local development

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Backend (optional)

The Python FastAPI backend lives in `/backend`. It handles real video download, transcription (faster-whisper), AI highlight detection, and ffmpeg rendering. Deploy it separately on Railway, Render, or Fly.io, then point the frontend at it via `NEXT_PUBLIC_API_URL`.

## Features

- Clean dark UI with live progress
- Demo mode works out of the box on Netlify
- Real backend integration when `NEXT_PUBLIC_API_URL` is set
- 9:16 vertical clips with caption styling
- Virality scoring

## License

MIT
