# Dockerfile para API de Extração de Dados do Google Analytics 4
# Deploy no Google Cloud Run
# Python 3.12 (versão estável mais recente, compatível com 3.14)

# Usar imagem base do Python 3.12
FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação (apenas arquivos necessários)
COPY auth.py .
COPY ga4.py .
COPY bigquery.py .
COPY main.py .

# Expor porta
EXPOSE 8080

# Comando para iniciar a aplicação
# A função main() é o entrypoint
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
