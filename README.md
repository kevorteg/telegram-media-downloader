# AutoVideo Telegram Bot

Bot de Telegram para descargar videos (especialmente de Twitter/X) y reenviarlos automáticamente a grupos o canales.

## Estructura

- `autovideo/`: Código fuente del bot.
  - `handlers/`: Manejadores de comandos y mensajes de Telegram.
  - `services/`: Lógica de negocio (descarga, validación, video, publicación).
  - `storage/`: Almacenamieto temporal de descargas.

## Instalación

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar `.env`:
   - Copiar `.env` y rellenar `TELEGRAM_BOT_TOKEN` y `TARGET_CHANNEL_ID`.

3. Ejecutar:
   ```bash
   python autovideo/bot.py
   ```
