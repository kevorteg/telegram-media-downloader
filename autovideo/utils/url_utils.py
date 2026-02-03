import re
from urllib.parse import urlparse

def extract_urls(text: str) -> list[str]:
    """Extrae URLs de un texto."""
    # Simple regex para encontrar http/https links
    regex = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*"
    return re.findall(regex, text)

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
