from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db, Job, Clip
from app.schemas import JobCreate, JobResponse, ClipResponse, RerenderRequest
from app.services import downloader, transcriber, highlighter, renderer
import uuid
import os
from pathlib import Path

router = APIRouter()
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")

def process_job(job_id: str, url: str):
    db = next(get_db())
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or job.status == "cancelled":
            return
        job.status = "downloading"
        job.stage = "Downloading video"
        job.progress = 10
        db.commit()
        dl_info = downloader.download_video(url, job_id)
        video_path = dl_info["video_path"]
        audio_path = dl_info["audio_path"]
        job.status = "transcribing"
        job.stage = "Transcribing audio"
        job.progress = 35
        db.commit()
        segments = transcriber.transcribe_audio(audio_path)
        job.status = "scoring"
        job.stage = "Finding viral highlights"
        job.progress = 60
        db.commit()
        highlights = highlighter.find_highlights(segments)
        job.status = "rendering"
        job.stage = "Rendering clips"
        job.progress = 75
        db.commit()
        for i, h in enumerate(highlights[:10]):
            clip_id = str(uuid.uuid4())
            render_result = renderer.render_clip(video_path, h["start"], h["end"], segments, clip_id)
            clip = Clip(
                id=clip_id,
                job_id=job_id,
                start=h["start"],
                end=h["end"],
                title=h.get("title", f"Clip {i+1}"),
                virality_score=h.get("virality_score", 70),
                reason=h.get("reason", ""),
                transcript=h.get("transcript", ""),
                video_path=render_result["video_path"],
                thumbnail_path=render_result["thumbnail_path"]
            )
            db.add(clip)
        job.status = "completed"
        job.stage = "Done"
        job.progress = 100
        db.commit()
    except Exception as e:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error = str(e)
            db.commit()
        print(f"Job {job_id} failed: {e}")
    finally:
        db.close()

@router.post("/jobs", response_model=JobResponse)
async def create_job(payload: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    job = Job(id=job_id, url=payload.url, status="pending", progress=0, stage="Queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(process_job, job_id, payload.url)
    return JobResponse(id=job.id, url=job.url, status=job.status, progress=job.progress, stage=job.stage, created_at=job.created_at, clips=[])

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    clips = db.query(Clip).filter(Clip.job_id == job_id).order_by(Clip.virality_score.desc()).all()
    clip_responses = []
    for c in clips:
        video_url = f"/storage/clips/{Path(c.video_path).name}" if c.video_path else None
        thumb_url = f"/storage/thumbnails/{Path(c.thumbnail_path).name}" if c.thumbnail_path else None
        clip_responses.append(ClipResponse(
            id=c.id, start=c.start, end=c.end, title=c.title,
            virality_score=c.virality_score, reason=c.reason,
            transcript=c.transcript, video_url=video_url, thumbnail_url=thumb_url
        ))
    return JobResponse(
        id=job.id, url=job.url, status=job.status, progress=job.progress,
        stage=job.stage, error=job.error, created_at=job.created_at, clips=clip_responses
    )

@router.post("/clips/{clip_id}/rerender")
async def rerender_clip(clip_id: str, payload: RerenderRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return {"message": "Rerender queued", "clip_id": clip_id}

@router.get("/clips/{clip_id}/download")
async def download_clip(clip_id: str, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip or not clip.video_path:
        raise HTTPException(status_code=404, detail="Clip not found")
    from fastapi.responses import FileResponse
    return FileResponse(clip.video_path, media_type="video/mp4", filename=f"{clip.title[:30]}.mp4")
