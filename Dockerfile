FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del servidor (sin pywebview, que solo usa la app de escritorio)
COPY src/requirements-servidor.txt .
RUN pip install --no-cache-dir -r requirements-servidor.txt

# Copiar el código fuente, las reglas (persistencia) y la interfaz (ui)
COPY src/ .

EXPOSE 8000

# Render y otras plataformas indican el puerto en la variable PORT; en local se usa 8000
CMD ["sh", "-c", "uvicorn servidor:app --host 0.0.0.0 --port ${PORT:-8000}"]
