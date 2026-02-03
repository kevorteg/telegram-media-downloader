import os
import yt_dlp
from autovideo.config.settings import settings
from autovideo.utils.logger import logger
from autovideo.utils.file_utils import ensure_directory

class DownloaderService:
    def __init__(self):
        self.download_path = settings.DOWNLOAD_PATH
        ensure_directory(self.download_path)

    def download_video(self, url: str) -> list[dict]:
        """
        Descarga video(s) dado un URL.
        Retorna una lista de diccionarios con metadatos: [{'path': str, 'width': int, 'height': int, ...}]
        """
        ydl_opts = {
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(id)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'overwrites': True,
            # Permitir playlists para soportar galerías de Twitter (varios videos en un tweet)
            'noplaylist': False,
            'extract_flat': False,
        }

        # Usar archivo cookies.txt si existe (la opción más robusta)
        cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies.txt')
        
        if os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
            logger.info(f"Usando cookies desde: {cookies_path}")
        else:
            # Fallback a cookies del navegador
            ydl_opts['cookiesfrombrowser'] = ('firefox', 'chrome', 'edge')

        ydl_opts['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

        results = []

        try:
            logger.info(f"Iniciando descarga de: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Si es una playlist/galería
                if 'entries' in info:
                    entries = info['entries']
                else:
                    entries = [info]

                for entry in entries:
                    if not entry: continue
                    filename = ydl.prepare_filename(entry)
                    
                    # A veces yt-dlp dice que descargó mkv pero lo fusionó a mp4, verificar extensión
                    # o confiar en prepare_filename.
                    
                    results.append({
                        'path': filename,
                        'width': entry.get('width'),
                        'height': entry.get('height'),
                        'title': entry.get('title'),
                        'duration': entry.get('duration')
                    })
                    
                logger.info(f"Descarga completada. Archivos: {len(results)}")
                return results

        except Exception as e:
            logger.error(f"Error al descargar {url}: {e}")
            return []

downloader_service = DownloaderService()
