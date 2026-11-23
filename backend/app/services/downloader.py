import yt_dlp
import os
import subprocess
from pathlib import Path

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")

def download_video(url: str, job_id: str) -> dict:
    """Download video using yt-dlp. Best quality under 1080p. Extract audio separately."""
    output_dir = Path(STORAGE_PATH) / "downloads" / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
        'outtmpl': str(output_dir / 'video.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'extract_audio': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)
        if not video_path.endswith('.mp4'):
            video_path = str(output_dir / 'video.mp4')
        
        audio_path = str(output_dir / 'audio.wav')
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1', audio_path
        ], check=True, capture_output=True)
        
        return {
            'video_path': video_path,
            'audio_path': audio_path,
            'duration': info.get('duration', 0),
            'title': info.get('title', 'Unknown'),
            'thumbnail': info.get('thumbnail')
        }
