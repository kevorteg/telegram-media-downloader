import asyncio
import yt_dlp
from telegram.ext import ContextTypes
from autovideo.config.settings import settings
from autovideo.services.history_service import history_service
from autovideo.services.downloader_service import downloader_service
from autovideo.services.video_service import video_service
from autovideo.services.publish_service import publish_service
from autovideo.utils.logger import logger
import os

class TwitterMonitorService:
    async def check_new_likes(self, context: ContextTypes.DEFAULT_TYPE):
        if not settings.TWITTER_USERNAME:
            logger.warning("No se puede monitorear likes: TWITTER_USERNAME no configurado.")
            return

        user_url = f"https://twitter.com/{settings.TWITTER_USERNAME}/likes"
        logger.info(f"Revisando nuevos likes en: {user_url}")

        # Configuración para solo OBTENER URLs, no descargar aún
        ydl_opts = {
            'extract_flat': True,  # No descargar videos, solo metadatos
            'playlistend': 20,     # Revisar solo los últimos 20 likes
            'quiet': True,
            'ignoreerrors': True,
        }
        
        # Usar credenciales si existen
        cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies.txt')
        
        if os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
        elif settings.TWITTER_USERNAME and settings.TWITTER_PASSWORD:
             # Fallback antiguo (probablemente no funcione)
            ydl_opts['username'] = settings.TWITTER_USERNAME
            ydl_opts['password'] = settings.TWITTER_PASSWORD

        new_urls = []

        try:
            # Ejecutar yt-dlp en un hilo/proceso aparte para no bloquear el bot
            # Nota: yt-dlp puede ser lento obteniendo la playlist
            loop = asyncio.get_running_loop()
            
            def fetch_playlist():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(user_url, download=False)

            result = await loop.run_in_executor(None, fetch_playlist)
            
            if result and 'entries' in result:
                for entry in result['entries']:
                    if not entry: continue
                    url = entry.get('url') or entry.get('webpage_url')
                    if url and not history_service.has_processed(url):
                        # Es un like nuevo (o no procesado)
                        new_urls.append(url)
                        # IMPORTANTE: Invertimos el orden para procesar del más viejo al más nuevo de este lote
                        # pero como 'entries' suele venir ordenado, simplemente los recolectamos.

        except Exception as e:
            logger.error(f"Error al obtener likes: {e}")
            return

        # Procesar los nuevos likes
        if new_urls:
            logger.info(f"Encontrados {len(new_urls)} nuevos likes. Procesando...")
            
            # Procesar en orden inverso (del más antiguo en la lista al más reciente)
            # para mantener cronología si es relevante
            for url in reversed(new_urls):
                try:
                    logger.info(f"Procesando nuevo like: {url}")
                    
                    # 1. Descargar
                    # Ejecutamos descarga síncrona en executor para no bloquear
                    media_list = await loop.run_in_executor(None, downloader_service.download_video, url)
                    
                    if media_list:
                        # 2. Procesar
                        processed_list = video_service.process_video(media_list)
                        
                        # 3. Publicar
                        await publish_service.publish_video(context.bot, processed_list, caption=None)
                        
                        # 4. Limpiar
                        for media in processed_list:
                            if os.path.exists(media['path']):
                                os.remove(media['path'])
                            
                        # 5. Marcar como procesado
                        history_service.mark_processed(url)
                        
                        # 6. Espera de seguridad (Rate Limiting)
                        logger.info("Esperando 20 segundos para evitar Rate Limit...")
                        await asyncio.sleep(20) 
                    else:
                        logger.warning(f"No se pudo descargar {url}, se reintentará en el próximo ciclo.")
                        
                except Exception as e:
                    logger.error(f"Error procesando like {url}: {e}")

twitter_monitor = TwitterMonitorService()
