FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y persistencia
COPY src/ .

EXPOSE 8000

CMD ["uvicorn", "servidor:app", "--host", "0.0.0.0", "--port", "8000"]
