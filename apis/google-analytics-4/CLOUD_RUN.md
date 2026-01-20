# 🌐 Google Analytics 4 API - Cloud Run

API REST para executar relatórios do Google Analytics 4 e salvar automaticamente no BigQuery.

## 📋 Visão Geral

Esta API foi desenvolvida para ser executada no **Google Cloud Run** e fornece endpoints HTTP para:
- Executar relatórios do GA4
- Salvar dados automaticamente no BigQuery (dataset RAW)
- Buscar credenciais do Secret Manager automaticamente
- Processar relatórios em lote
- Obter dados em tempo real

## 🏗️ Arquitetura

```
Cliente HTTP
    ↓
Cloud Run (main.py)
    ↓
Secret Manager → Credenciais GA4
    ↓
Google Analytics 4 API
    ↓
BigQuery (dataset RAW)
```

## 🔧 Especificações Técnicas

- **Python Version**: 3.11
- **Web Framework**: Flask
- **Server**: Gunicorn
- **Entry Point**: `main.py`
- **Port**: 8080 (configurável via ENV)

## 📦 Componentes Principais

### 1. SecretManager (`src/secret_manager.py`)
Busca credenciais do Google Cloud Secret Manager.

```python
from src.secret_manager import SecretManager

secret_manager = SecretManager()
secret_value = secret_manager.access_secret_version(
    secret_id="ga4-credentials",
    project_id="your-project-id"
)
```

### 2. GoogleAnalytics4 (`src/ga4_client.py`)
Cliente para executar relatórios do GA4.

```python
from google.oauth2.service_account import Credentials
from src.ga4_client import GoogleAnalytics4

# Criar credentials
credentials = Credentials.from_service_account_info(json_data)

# Instanciar cliente
ga4 = GoogleAnalytics4(credentials)

# Executar relatório
response = ga4.run_report(request)
```

### 3. BigQueryWriter (`src/bigquery_writer.py`)
Escreve dados do GA4 no BigQuery.

```python
from src.bigquery_writer import BigQueryWriter

writer = BigQueryWriter(
    project_id="your-project-id",
    dataset_id="RAW",
    credentials=credentials
)

writer.write_ga4_data(
    table_id="ga4_daily_report",
    data=response
)
```

### 4. Models (`src/models.py`)
Classes para estruturar requisições.

```python
from src.models import DateRange, Dimension, Metric, RunReportRequest

request = RunReportRequest(
    property_id="123456789",
    date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
    dimensions=[Dimension(name='country')],
    metrics=[Metric(name='activeUsers')]
)
```

## 🌐 Endpoints da API

### `GET /`
Health check

**Response:**
```json
{
    "status": "healthy",
    "service": "Google Analytics 4 API",
    "version": "1.0.0"
}
```

### `POST /run-report`
Executa relatório do GA4 e salva no BigQuery

**Request Body:**
```json
{
    "project_id": "your-project-id",
    "secret_id": "ga4-credentials",
    "property_id": "123456789",
    "bigquery_table": "ga4_daily_report",
    "bigquery_dataset": "RAW",
    "date_ranges": [
        {
            "start_date": "7daysAgo",
            "end_date": "today"
        }
    ],
    "dimensions": [
        {"name": "country"},
        {"name": "city"}
    ],
    "metrics": [
        {"name": "activeUsers"},
        {"name": "sessions"}
    ],
    "limit": 10000
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Relatório processado e salvo no BigQuery",
    "details": {
        "property_id": "properties/123456789",
        "rows_processed": 150,
        "bigquery_table": "your-project-id.RAW.ga4_daily_report",
        "dimensions": ["country", "city"],
        "metrics": ["activeUsers", "sessions"]
    }
}
```

### `POST /batch-reports`
Executa múltiplos relatórios em lote

**Request Body:**
```json
{
    "project_id": "your-project-id",
    "secret_id": "ga4-credentials",
    "property_id": "123456789",
    "bigquery_table": "ga4_batch_reports",
    "bigquery_dataset": "RAW",
    "requests": [
        {
            "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}],
            "dimensions": [{"name": "country"}],
            "metrics": [{"name": "activeUsers"}]
        },
        {
            "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}],
            "dimensions": [{"name": "deviceCategory"}],
            "metrics": [{"name": "sessions"}]
        }
    ]
}
```

### `POST /realtime-report`
Executa relatório em tempo real

**Request Body:**
```json
{
    "project_id": "your-project-id",
    "secret_id": "ga4-credentials",
    "property_id": "123456789",
    "bigquery_table": "ga4_realtime",
    "bigquery_dataset": "RAW",
    "dimensions": [
        {"name": "country"}
    ],
    "metrics": [
        {"name": "activeUsers"}
    ],
    "limit": 10
}
```

## 🗄️ Estrutura no BigQuery

### Dataset: RAW

Todas as tabelas são criadas automaticamente no dataset `RAW` com o schema:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ingestion_timestamp` | TIMESTAMP | Data/hora da ingestão |
| `report_date` | DATE | Data do relatório (extraída das dimensões) |
| `dimensions` | JSON | Dimensões do relatório |
| `metrics` | JSON | Métricas do relatório |
| `row_data` | JSON | Dados completos da linha |
| `metadata` | JSON | Metadados do relatório |

**Exemplo de consulta:**
```sql
SELECT
    report_date,
    JSON_VALUE(dimensions, '$.country') as country,
    JSON_VALUE(metrics, '$.activeUsers') as active_users
FROM `your-project-id.RAW.ga4_daily_report`
WHERE report_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
ORDER BY report_date DESC
```

## 🚀 Deploy Rápido

```bash
# 1. Configurar projeto
gcloud config set project YOUR-PROJECT-ID

# 2. Criar secret com credenciais GA4
gcloud secrets create ga4-credentials \
    --data-file=./service-account-key.json

# 3. Criar dataset no BigQuery
bq mk --dataset --location=US YOUR-PROJECT-ID:RAW

# 4. Deploy no Cloud Run
cd apis/google-analytics-4
gcloud run deploy ga4-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --timeout 300
```

## 🧪 Testar Localmente

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
export PROJECT_ID='your-project-id'
export SECRET_ID='ga4-credentials'
export GA4_PROPERTY_ID='your-property-id'
export PORT=8080
```

### 3. Executar servidor local

```bash
python main.py
```

### 4. Testar endpoint

```bash
curl -X POST http://localhost:8080/run-report \
    -H "Content-Type: application/json" \
    -d @test_request.json
```

## 📝 Exemplo de Uso Programático

```python
import json
from google.oauth2.service_account import Credentials
from src.secret_manager import SecretManager
from src.ga4_client import GoogleAnalytics4
from src.bigquery_writer import BigQueryWriter
from src.models import DateRange, Dimension, Metric, RunReportRequest

# 1. Buscar credenciais
secret_manager = SecretManager()
secret_value = secret_manager.access_secret_version(
    secret_id="ga4-credentials",
    project_id="your-project-id"
)

# 2. Criar credentials
service_account_json = json.loads(secret_value)
credentials = Credentials.from_service_account_info(service_account_json)

# 3. Instanciar GA4
ga4 = GoogleAnalytics4(credentials)

# 4. Criar requisição
request = RunReportRequest(
    property_id="123456789",
    date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
    dimensions=[Dimension(name='country')],
    metrics=[Metric(name='activeUsers')],
    limit=100
)

# 5. Executar relatório
response = ga4.run_report(request)

# 6. Salvar no BigQuery
writer = BigQueryWriter(
    project_id="your-project-id",
    dataset_id="RAW",
    credentials=credentials
)

writer.write_ga4_data(
    table_id="ga4_daily_report",
    data=response
)

print(f"✓ {response['row_count']} linhas salvas no BigQuery")
```

## 🔐 Permissões Necessárias

### Service Account do Cloud Run precisa:
- `roles/secretmanager.secretAccessor` - Acessar secrets
- `roles/bigquery.dataEditor` - Editar dados no BigQuery
- `roles/bigquery.jobUser` - Executar jobs no BigQuery

### Service Account do GA4 (no secret) precisa:
- Permissão de **Visualizador** na propriedade GA4

## 📊 Monitoramento

### Logs
```bash
gcloud run services logs tail ga4-api \
    --platform managed \
    --region us-central1
```

### Métricas
- Acesse: https://console.cloud.google.com/run
- Clique em `ga4-api`
- Veja métricas de requisições, latência, CPU, memória

## 🔧 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `PORT` | Porta do servidor | 8080 |
| `PROJECT_ID` | ID do projeto GCP | - |

## 📚 Documentação Completa

- [README.md](README.md) - Documentação geral da API
- [DEPLOY.md](DEPLOY.md) - Guia completo de deploy
- [QUICKSTART.md](QUICKSTART.md) - Guia de início rápido

## 🆘 Troubleshooting

### Erro: "Permission denied" ao acessar secret
```bash
# Dar permissão à service account
gcloud secrets add-iam-policy-binding ga4-credentials \
    --member="serviceAccount:YOUR-SERVICE-ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

### Erro: "Table not found" no BigQuery
- A API cria a tabela automaticamente
- Certifique-se de que a service account tem permissão `bigquery.dataEditor`

### Erro: "Out of memory"
```bash
# Aumentar memória
gcloud run deploy ga4-api \
    --source . \
    --memory 2Gi
```

## ✨ Próximos Passos

1. Configure **Cloud Scheduler** para executar relatórios diariamente
2. Adicione **alertas** no Cloud Monitoring
3. Configure **CI/CD** com Cloud Build
4. Implemente **cache** para otimizar performance
5. Adicione **autenticação** para produção
