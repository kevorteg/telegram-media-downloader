# 🤖 Telegram Media Downloader Bot

Un bot de Telegram avanzado y "Cloud-Ready" diseñado para descargar, procesar y reenviar videos desde múltiples plataformas (Twitter/X, Instagram, TikTok, y más) automáticamente.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Enabled-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## ✨ Características

*   **Multi-Plataforma**: Descarga de Twitter (X), Instagram, TikTok, Facebook, YouTube (Shorts), y +1000 sitios soportados por `yt-dlp`.
*   **Gestión Inteligente de Video**:
    *   **Fix de Aspect Ratio**: Usa FFmpeg para detectar dimensiones reales y evitar videos "estirados" en Telegram.
    *   **Compresión Automática**: Si un video supera los 50MB, lo comprime automáticamente para poder enviarlo.
*   **Monitor de Likes**: (Opcional) Revisa automáticamente los "Likes" de una cuenta de Twitter cada X minutos y descarga los videos nuevos.
*   **Cookies Vía Entorno**: Soporte para cargar cookies desde una Variable de Entorno (`COOKIES_CONTENT`), ideal para despliegues en la nube (Koyeb, Render) sin exponer archivos sensibles.
*   **Auto-Limpieza**: Borra los archivos descargados inmediatamente después de enviarlos para ahorrar espacio.

## 🚀 Despliegue Rápido (Cloud)

Este proyecto está optimizado para **Koyeb** o **Render**.

### Pasos en Koyeb:
1.  Haz Fork de este repositorio.
2.  Crea un nuevo **Web Service** en Koyeb seleccionando tu repo.
3.  **Builder**: Selecciona **Dockerfile** (se detectará automáticamente).
4.  **Variables de Entorno (Environment Variables)**: Añade las siguientes:

| Variable | Descripción |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Token de tu bot (de @BotFather). |
| `TARGET_CHANNEL_ID` | ID del canal/grupo donde se enviarán los videos. |
| `TWITTER_USERNAME` | (Opcional) Usuario de Twitter para monitorear likes. |
| `COOKIES_CONTENT` | Contenido completo de tu archivo `cookies.txt` (copiar y pegar texto). |
| `ADMIN_USER_IDS` | (Opcional) IDs de usuarios admin separados por comas. |

5.  Dale a **Deploy**.

## 💻 Ejecución Local

### Requisitos
*   Python 3.10+
*   **FFmpeg** instalado y en el PATH del sistema.

### Instalación
1.  Clonar el repositorio:
    ```bash
    git clone https://github.com/kevorteg/telegram-media-downloader.git
    cd telegram-media-downloader
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Crear archivo `.env` basado en el ejemplo y configurar tus tokens.
4.  (Opcional) Colocar tu archivo `cookies.txt` en la carpeta `autovideo/` para acceso a sitios restringidos.
5.  Ejecutar:
    ```bash
    python autovideo/bot.py
    ```

## 🔒 Privacidad y Cookies
El bot soporta el uso de cookies exportadas (formato Netscape) para acceder a contenido +18 o restringido (Twitter, sitios para adultos, etc.).
*   **Local**: Pon el archivo `cookies.txt` en la carpeta raíz.
*   **Nube**: Copia el contenido del archivo en la variable `COOKIES_CONTENT`.

## 📄 Licencia
Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
