import os
import logging
import subprocess
import json
import shutil
from autovideo.utils.file_utils import get_file_size_mb

logger = logging.getLogger(__name__)

class VideoService:
    def get_video_metadata(self, file_path: str) -> dict:
        """Obtiene metadatos reales del video usando ffprobe."""
        try:
            cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                '-show_streams', 
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            data = json.loads(result.stdout)
            
            video_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), None)
            if not video_stream:
                return {}

            return {
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'duration': float(data['format'].get('duration', 0))
            }
        except Exception as e:
            logger.error(f"Error obteniendo metadatos con ffprobe: {e}")
            return {}

    def compress_video(self, input_path: str, target_size_mb: int = 49) -> str:
        """Comprime el video si supera el tamaño objetivo."""
        try:
            output_path = f"{os.path.splitext(input_path)[0]}_compressed.mp4"
            logger.info(f"Comprimiendo video: {input_path} -> {output_path}")
            
            # Usamos CRF 28 para una compresión decente y rápida
            # -movflags faststart mueve los metadatos al inicio para streaming
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-vcodec', 'libx264',
                '-crf', '28',
                '-preset', 'fast',
                '-acodec', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                output_path
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(output_path):
                new_size = get_file_size_mb(output_path)
                logger.info(f"Compresión completada. Nuevo tamaño: {new_size:.2f} MB")
                return output_path
            
            return input_path
        except Exception as e:
            logger.error(f"Error comprimiendo video: {e}")
            return input_path

    def process_video(self, media_list: list[dict]) -> list[dict]:
        """
        Procesa la lista de videos:
        1. Obtiene dimensiones reales (arregla videos estirados).
        2. Comprime si > 50MB.
        """
        processed_list = []
        
        for media in media_list:
            file_path = media['path']
            
            if not os.path.exists(file_path):
                logger.error(f"Archivo no encontrado: {file_path}")
                continue

            # 1. Verificar tamaño y comprimir si es necesario
            size_mb = get_file_size_mb(file_path)
            if size_mb > 50:
                logger.warning(f"Video {size_mb:.2f}MB > 50MB. Iniciando compresión...")
                compressed_path = self.compress_video(file_path)
                
                # Si se comprimió (el nombre cambió), actualizamos path y borramos el original
                if compressed_path != file_path:
                    try:
                        os.remove(file_path)  # Borrar el original pesado
                    except:
                        pass
                    media['path'] = compressed_path
                    file_path = compressed_path
                    size_mb = get_file_size_mb(file_path) # Actualizar tamaño

            # 2. Obtener metadatos reales (Dimensiones)
            # Esto es CRUCIAL para que Telegram no estire el video
            metadata = self.get_video_metadata(file_path)
            if metadata.get('width') and metadata.get('height'):
                media['width'] = metadata['width']
                media['height'] = metadata['height']
                media['duration'] = metadata.get('duration')
                logger.info(f"Metadatos corregidos: {metadata['width']}x{metadata['height']}")
            
            media['size_mb'] = size_mb
            processed_list.append(media)

        return processed_list

video_service = VideoService()
