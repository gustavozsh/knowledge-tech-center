# Dockerfile para GA4 Campaign Extractor API
# Otimizado para Google Cloud Run

FROM python:3.12-slim

# Definir diretorio de trabalho
WORKDIR /app

# Variaveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Instalar dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo da aplicacao
COPY . .

# Expor porta
EXPOSE 8080

# Comando para iniciar a aplicacao com Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
