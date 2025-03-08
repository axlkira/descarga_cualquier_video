from typing import Optional
import yt_dlp
from pathlib import Path

class VideoDownloader:
    def __init__(self, output_path: str = "./downloads"):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def download_video(self, url: str, output_format: str = "mp4") -> Optional[str]:
        """
        Descarga un video de la URL proporcionada
        
        Args:
            url: URL del video a descargar
            output_format: Formato de salida (por defecto mp4)
            
        Returns:
            str: Ruta del archivo descargado o None si falla
        """
        ydl_opts = {
            'format': f'bestvideo[ext={output_format}]+bestaudio[ext=m4a]/best[ext={output_format}]/best',
            'outtmpl': str(self.output_path / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                return video_path
        except Exception as e:
            print(f"Error al descargar el video: {str(e)}")
            return None
