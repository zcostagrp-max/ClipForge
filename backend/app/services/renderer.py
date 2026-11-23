import subprocess
import os
from pathlib import Path

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")

def generate_srt(segments: list, start_offset: float = 0) -> str:
    lines = []
    idx = 1
    current_line = []
    current_start = None
    for seg in segments:
        words = seg.get("words", [])
        if not words:
            text = seg["text"]
            words_list = text.split()
            if not words_list:
                continue
            duration = seg["end"] - seg["start"]
            word_dur = duration / len(words_list)
            words = [{"word": w, "start": seg["start"] + i*word_dur, "end": seg["start"] + (i+1)*word_dur} for i, w in enumerate(words_list)]
        for word in words:
            wstart = word["start"] - start_offset
            wend = word["end"] - start_offset
            if wstart < 0:
                continue
            if current_start is None:
                current_start = wstart
            current_line.append(word["word"])
            if len(current_line) >= 5 or (wend - current_start) > 3.5:
                text = " ".join(current_line)
                lines.append(f"{idx}\n{format_time(current_start)} --> {format_time(wend)}\n{text}\n")
                idx += 1
                current_line = []
                current_start = None
    if current_line and current_start is not None:
        text = " ".join(current_line)
        lines.append(f"{idx}\n{format_time(current_start)} --> {format_time(current_start + 2)}\n{text}\n")
    return "\n".join(lines)

def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def render_clip(video_path: str, start: float, end: float, transcript_segments: list, clip_id: str) -> dict:
    output_dir = Path(STORAGE_PATH) / "clips"
    output_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir = Path(STORAGE_PATH) / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    out_video = str(output_dir / f"{clip_id}.mp4")
    out_thumb = str(thumb_dir / f"{clip_id}.jpg")
    srt_path = str(output_dir / f"{clip_id}.srt")
    clip_segments = [s for s in transcript_segments if s["end"] > start and s["start"] < end]
    srt_content = generate_srt(clip_segments, start_offset=start)
    with open(srt_path, "w") as f:
        f.write(srt_content)
    style = "FontName=Bangers,FontSize=80,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=6,Shadow=2,Alignment=2,MarginV=180"
    fontsdir = "/usr/share/fonts/SlidesCarnival/google/Bangers"
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", video_path,
        "-vf", f"crop=ih*9/16:ih,scale=1080:1920,setsar=1,subtitles={srt_path}:fontsdir={fontsdir}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        out_video
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start + 1), "-i", video_path,
        "-vframes", "1", "-vf", "crop=ih*9/16:ih,scale=540:960",
        out_thumb
    ], check=True, capture_output=True)
    return {"video_path": out_video, "thumbnail_path": out_thumb}
