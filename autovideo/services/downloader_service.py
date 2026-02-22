import os
import yt_dlp
from autovideo.config.settings import settings
from autovideo.utils.logger import logger
from autovideo.utils.file_utils import ensure_directory

class DownloaderService:
    def __init__(self):
        self.download_path = settings.DOWNLOAD_PATH
        ensure_directory(self.download_path)

    def download_video(self, url: str, progress_callback=None, format_id=None) -> list[dict]:
        """
        Descarga video(s) dado un URL.
        Retorna una lista de diccionarios con metadatos: [{'path': str, 'width': int, 'height': int, ...}]
        Args:
            url (str): URL del video
            progress_callback (callable, optional): Función que recibe el porcentaje (str) como argumento.
            format_id (str, optional): ID del formato seleccionado (yt-dlp format id)
        """
        if "x.com" in url:
             url = url.replace("x.com", "twitter.com")

        ydl_opts = {
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(id)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'remux_video': 'mp4',
            'quiet': True,
            'overwrites': True,
            # Estabilización de red
            'socket_timeout': 40,
            'retries': 5,
            'fragment_retries': 5,
            'nocheckcertificate': True,
            # Permitir playlists para soportar galerías de Twitter
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
        result = self._try_download(stage1_opts, url, progress_callback, format_id)
        if result: return result

        # Attempt 2: Twitter/X Hybrid (gallery-dl)
        if "twitter.com" in url or "x.com" in url:
            logger.info("Attempt 2: Twitter Hybrid Strategy")
            direct_url = self._extract_twitter_direct_url(url, cookies_path)
            if direct_url:
                # Download direct URL without cookies (CDN usually allows it)
                result = self._try_download(stage1_opts, direct_url, progress_callback, format_id)
                if result: return result
        
        # Attempt 3: Authenticated Download (Last Resort)
        if os.path.exists(cookies_path):
             logger.info(f"Attempt 3: Authenticated download using cookies")
             stage3_opts = ydl_opts.copy()
             stage3_opts['cookiefile'] = cookies_path
             result = self._try_download(stage3_opts, url, progress_callback, format_id)
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

    def get_available_formats(self, url: str) -> list[dict]:
        """Extrae los formatos disponibles (resoluciones) para un URL."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            # Usar cookies si existen
            cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies.txt')
            if os.path.exists(cookies_path):
                ydl_opts['cookiefile'] = cookies_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                formats = []
                # Filtrar solo formatos de video con audio o combinados
                seen_heights = set()
                
                raw_formats = info.get('formats', [])
                # Ordenar por altura descendente
                raw_formats.sort(key=lambda x: x.get('height') or 0, reverse=True)

                for f in raw_formats:
                    h = f.get('height')
                    if h and h not in seen_heights and h >= 144:
                        # Solo calidades comunes para no saturar el menú
                        if h in [144, 240, 360, 480, 720, 1080, 1440, 2160]:
                            formats.append({
                                'id': f['format_id'],
                                'height': h,
                                'ext': f.get('ext', 'mp4'),
                                'note': f.get('format_note', '')
                            })
                            seen_heights.add(h)
                
                # Si no hay formatos estándar, devolver el mejor
                if not formats:
                    formats.append({'id': 'best', 'height': 'Auto', 'ext': 'mp4', 'note': 'Mejor calidad'})
                
                return formats[:6] # Limitar a 6 opciones para Telegram
        except Exception as e:
            logger.error(f"Error extrayendo formatos: {e}")
            return [{'id': 'best', 'height': 'Auto', 'ext': 'mp4', 'note': 'Default'}]

    def _try_download(self, opts, url, progress_callback, format_id=None):
        results = []
        try:
            if format_id and format_id != 'best':
                # Seleccionar el formato específico + mejor audio, forzando mp4
                opts['format'] = f"{format_id}+bestaudio/best"
                opts['merge_output_format'] = 'mp4'
                opts['remux_video'] = 'mp4'

            # Re-attach progress hook contextually
            if progress_callback:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            # Intentar obtener el % de varias formas
                            p_str = d.get('_percent_str')
                            if p_str:
                                p = p_str.replace('%','').strip()
                            else:
                                # Calcular manualmente si falta el string
                                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                                downloaded = d.get('downloaded_bytes', 0)
                                if total:
                                    p = str(round((downloaded / total) * 100))
                                else:
                                    p = "0"
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
                    'duration': entry.get('duration'),
                    'original_url': url
                })
            return results
        except Exception as e:
            logger.warning(f"Download attempt failed: {e}")
            return None

downloader_service = DownloaderService()
