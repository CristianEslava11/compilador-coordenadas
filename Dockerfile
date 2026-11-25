FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Dependencias del servidor web (sin pywebview: no hay ventana nativa en un contenedor)
COPY src/requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Código fuente, reglas (persistencia/) e interfaz (ui/)
COPY src/ .

# Usuario sin privilegios
RUN useradd --create-home geo && chown -R geo /app
USER geo

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/info')" || exit 1

# La plataforma de despliegue (Render, Railway, Fly...) inyecta $PORT; en local es 8000
CMD ["sh", "-c", "uvicorn servidor:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
