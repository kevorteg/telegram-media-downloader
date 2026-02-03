FROM python:3.10-slim

# Instalar dependencias del sistema (FFmpeg es CRÍTICO para este bot)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando de inicio
CMD ["python", "autovideo/bot.py"]
