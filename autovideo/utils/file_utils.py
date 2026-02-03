import os
import shutil
from autovideo.utils.logger import logger

def ensure_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Directorio creado: {path}")

def clean_directory(path: str):
    """Elimina todos los archivos en un directorio."""
    if os.path.exists(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f'Fallo al borrar {file_path}. Razón: {e}')

def get_file_size_mb(path: str) -> float:
    if os.path.exists(path):
        return os.path.getsize(path) / (1024 * 1024)
    return 0.0
