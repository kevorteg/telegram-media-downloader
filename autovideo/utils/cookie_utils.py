import os
from autovideo.utils.logger import logger

def get_patched_cookie_file(cookies_path: str) -> str:
    """
    Lee el archivo de cookies y si encuentra dominios x.com sin su par twitter.com,
    crea un archivo temporal con los dominios duplicados para asegurar compatibilidad.
    Retorna la ruta al archivo de cookies a usar (original o temporal).
    """
    if not os.path.exists(cookies_path):
        logger.warning(f"No se encontró cookies.txt en {cookies_path}")
        return None

    try:
        file_size = os.path.getsize(cookies_path)
        if file_size == 0:
            logger.warning("El archivo cookies.txt está vacío.")
            return None

        with open(cookies_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # FIX: Incluso si existen cookies para .twitter.com, a veces faltan las de autenticación 
        # Si detectamos .x.com, forzamos la creación/actualización de cookies .twitter.com
        if '.x.com' in content or 'x.com' in content:
            logger.debug("Analizando cookies de x.com para asegurar compatibilidad con twitter.com...")
            
            new_lines = []
            existing_lines = content.splitlines()
            new_lines.extend(existing_lines)
            
            changes_made = False
            
            for line in existing_lines:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                parts = line.split()
                if len(parts) >= 7:
                    domain = parts[0]
                    if 'x.com' in domain:
                        # Crear versión twitter.com
                        new_domain = domain.replace('x.com', 'twitter.com')
                        # Reconstruir línea con nuevo dominio
                        new_line = line.replace(domain, new_domain, 1)
                        # Solo agregamos si no parece ser un duplicado exacto (aunque yt-dlp maneja duplicados bien)
                        new_lines.append(new_line)
                        changes_made = True
            
            if changes_made:
                temp_cookies = cookies_path + ".temp"
                with open(temp_cookies, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                logger.info(f"Cookies parcheadas guardadas en: {temp_cookies}")
                return temp_cookies
        
        return cookies_path

    except Exception as e:
        logger.error(f"Error procesando cookies: {e}")
        return cookies_path
