from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import uvicorn
from core.downloader import VideoDownloader
from core.url_parser import URLParser

app = FastAPI(title="Video Downloader API")
downloader = VideoDownloader()

class VideoRequest(BaseModel):
    url: str
    format: str = "mp4"

@app.post("/download/")
async def download_video(video_request: VideoRequest):
    if not URLParser.is_supported_url(video_request.url):
        raise HTTPException(status_code=400, detail="URL no soportada")
    
    video_path = downloader.download_video(video_request.url, video_request.format)
    
    if not video_path:
        raise HTTPException(status_code=500, detail="Error al descargar el video")
    
    return {"status": "success", "file_path": video_path}

@app.get("/video/{video_name}")
async def get_video(video_name: str):
    video_path = Path("./downloads") / video_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    return FileResponse(path=video_path)

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)
