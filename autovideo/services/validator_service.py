from autovideo.utils.url_utils import is_valid_url
from urllib.parse import urlparse

# Lista blanca de dominios soportados (aunque yt-dlp soporta muchos, podemos restringir si queremos)
# Dejar vacío o None para permitir todos los soportados por yt-dlp
# Lista blanca desactivada para permitir +1000 sitios (incluyendo adultos)
ALLOWED_DOMAINS = None

def is_supported_url(url: str) -> bool:
    if not is_valid_url(url):
        return False
    
    # Si ALLOWED_DOMAINS es None, permitimos todo lo que parezca una URL válida
    if ALLOWED_DOMAINS is None:
        return True

    domain = urlparse(url).netloc.lower()
    
    # Quitar 'www.' si existe
    if domain.startswith("www."):
        domain = domain[4:]
        
    for allowed in ALLOWED_DOMAINS:
        if allowed in domain:
            return True
            
    return False
