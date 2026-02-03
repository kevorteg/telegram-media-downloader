from autovideo.config.settings import settings

def is_admin(user_id: int) -> bool:
    """Verifica si un usuario es administrador."""
    return user_id in settings.ADMIN_USER_IDS
