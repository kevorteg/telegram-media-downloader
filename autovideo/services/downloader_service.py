import os
import yt_dlp
from autovideo.config.settings import settings
from autovideo.utils.logger import logger
from autovideo.utils.file_utils import ensure_directory

class DownloaderService:
    def __init__(self):
        self.download_path = settings.DOWNLOAD_PATH
        ensure_directory(self.download_path)

    def download_video(self, url: str, progress_callback=None) -> list[dict]:
        """
        Descarga video(s) dado un URL.
        Retorna una lista de diccionarios con metadatos: [{'path': str, 'width': int, 'height': int, ...}]
        Args:
            url (str): URL del video
            progress_callback (callable, optional): Función que recibe el porcentaje (str) como argumento.
        """
        if "x.com" in url:
             url = url.replace("x.com", "twitter.com")

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
        
        # MULTI-STAGE DOWNLOAD LOGIC
        # Attempt 1: Standard generic download (No Cookies)
        # Attempt 2: If failed & Twitter, try gallery-dl hybrid
        # Attempt 3: If failed & cookies exist, try with cookies

        # Configuration for Stage 1 (Clean)
        stage1_opts = ydl_opts.copy() # No cookies attached yet
        
        logger.info(f"Attempt 1: Generic download for {url}")
        result = self._try_download(stage1_opts, url, progress_callback)
        if result: return result

        # Attempt 2: Twitter/X Hybrid (gallery-dl)
        if "twitter.com" in url or "x.com" in url:
            logger.info("Attempt 2: Twitter Hybrid Strategy")
            direct_url = self._extract_twitter_direct_url(url, cookies_path)
            if direct_url:
                # Download direct URL without cookies (CDN usually allows it)
                result = self._try_download(stage1_opts, direct_url, progress_callback)
                if result: return result
        
        # Attempt 3: Authenticated Download (Last Resort)
        if os.path.exists(cookies_path):
             logger.info(f"Attempt 3: Authenticated download using cookies")
             stage3_opts = ydl_opts.copy()
             stage3_opts['cookiefile'] = cookies_path
             result = self._try_download(stage3_opts, url, progress_callback)
             if result: return result

        logger.error(f"All download attempts failed for {url}")
        return []

    def _extract_twitter_direct_url(self, url, cookies_path):
        try:
            import subprocess
            import sys
            cmd = [
                sys.executable, "-m", "gallery_dl",
                "--cookies", cookies_path if os.path.exists(cookies_path) else None,
                "--get-urls",
                url
            ]
            cmd = [arg for arg in cmd if arg is not None]
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                lines = process.stdout.strip().splitlines()
                valid_urls = [line for line in lines if line.startswith("http")]
                if valid_urls:
                    return valid_urls[0]
        except Exception as e:
            logger.error(f"gallery-dl extraction failed: {e}")
        return None

    def _try_download(self, opts, url, progress_callback):
        results = []
        try:
            # Re-attach progress hook contextually
            if progress_callback:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            p = d.get('_percent_str', '0%').replace('%','')
                            progress_callback(p)
                        except: pass
                opts['progress_hooks'] = [progress_hook]

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
            if 'entries' in info:
                entries = info['entries']
            else:
                entries = [info]

            for entry in entries:
                if not entry: continue
                filename = ydl.prepare_filename(entry)
                results.append({
                    'path': filename,
                    'width': entry.get('width'),
                    'height': entry.get('height'),
                    'title': entry.get('title'),
                    'duration': entry.get('duration')
                })
            return results
        except Exception as e:
            logger.warning(f"Download attempt failed: {e}")
            return None

downloader_service = DownloaderService()
