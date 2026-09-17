# 1. Imagen oficial y ligera de Python
FROM python:3.12-slim

# Metadatos del proyecto
LABEL maintainer="Cristian Eslava"
LABEL description="Compilador GeoQuery API con FastAPI y Docker"

# 2. Directorio de trabajo dentro del contenedor
WORKDIR /app

# Variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# 3. Copiar e instalar dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código del compilador (módulos, reglas.json y servidor.py)
COPY src/ /app/src/

# 5. Exponer el puerto 8000
EXPOSE 8000

# 6. Ejecutar Uvicorn al iniciar el contenedor
CMD ["uvicorn", "src.servidor:app", "--host", "0.0.0.0", "--port", "8000"]
