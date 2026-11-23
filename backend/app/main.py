from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ClipForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.netlify.app",
        "https://*.netlify.com",
    ],
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage_path = os.getenv("STORAGE_PATH", "./storage")
os.makedirs(storage_path, exist_ok=True)
os.makedirs(os.path.join(storage_path, "clips"), exist_ok=True)
os.makedirs(os.path.join(storage_path, "thumbnails"), exist_ok=True)
os.makedirs(os.path.join(storage_path, "downloads"), exist_ok=True)

app.mount("/storage", StaticFiles(directory=storage_path), name="storage")

from app.routers import jobs
app.include_router(jobs.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "ClipForge API is running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}
