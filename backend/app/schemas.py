from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobCreate(BaseModel):
    url: str
    target_duration: int = 30  # 10, 20, 30, 45, 60
    quality: str = "1080p"     # "720p" or "1080p"

class ClipResponse(BaseModel):
    id: str
    start: float
    end: float
    title: str
    virality_score: int
    reason: str
    transcript: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    url: str
    status: str
    progress: int
    stage: str
    error: Optional[str] = None
    created_at: datetime
    clips: List[ClipResponse] = []

class RerenderRequest(BaseModel):
    start: float
    end: float
