# GA4 Campaign Extractor API

API de extracao de dados de campanhas do Google Analytics 4 para BigQuery, otimizada para execucao no Google Cloud Run.

## Caracteristicas

- Extracao de **11 dimensoes diferentes** com suas metricas associadas
- Tabelas separadas no BigQuery para cada dimensao
- Particionamento diario (tabelas incrementais)
- ID unico como chave primaria em cada registro
- Chave estrangeira (`ga4_session_key`) para relacionar tabelas
- Campo `last_update` com timestamp da execucao
- Schemas pre-definidos com criacao automatica de tabelas

## Dimensoes Disponiveis

| Dimensao | Tabela | Descricao |
|----------|--------|-----------|
| CAMPAIGN | GA4_DIM_CAMPAIGN | Campanhas de marketing |
| SOURCE_MEDIUM | GA4_DIM_SOURCE_MEDIUM | Origem e midia de trafego |
| CHANNEL | GA4_DIM_CHANNEL | Canais de aquisicao |
| GEOGRAPHIC | GA4_DIM_GEOGRAPHIC | Dados geograficos |
| DEVICE | GA4_DIM_DEVICE | Dispositivos e tecnologia |
| PAGE | GA4_DIM_PAGE | Paginas e conteudo |
| EVENT | GA4_DIM_EVENT | Eventos e conversoes |
| USER | GA4_DIM_USER | Usuarios e demograficos |
| ECOMMERCE | GA4_DIM_ECOMMERCE | E-commerce e transacoes |
| SESSION | GA4_DIM_SESSION | Sessoes |
| GOOGLE_ADS | GA4_DIM_GOOGLE_ADS | Campanhas Google Ads |

## Estrutura das Tabelas

Todas as tabelas possuem os seguintes campos base (em UPPERCASE):

```sql
PK_{NOME_TABELA}  STRING    REQUIRED  -- Chave primaria (UUID) - Ex: PK_GA4_DIM_CAMPAIGN
GA4_SESSION_KEY   STRING    REQUIRED  -- Chave estrangeira (PROPERTY_ID + DATE)
PROPERTY_ID       STRING    REQUIRED  -- ID da propriedade GA4
DATE              DATE      REQUIRED  -- Data do registro (particionamento)
LAST_UPDATE       TIMESTAMP REQUIRED  -- Timestamp do carregamento
```

## Instalacao

### Requisitos

- Python 3.12+
- Conta GCP com acesso ao BigQuery e GA4

### Instalacao Local

```bash
cd apis/ga4-campaign
pip install -r requirements.txt
```

### Variaveis de Ambiente

```bash
# Obrigatorias
export GCP_PROJECT_ID="seu-projeto-gcp"
export GA4_PROPERTY_ID="123456789"

# Opcionais
export BQ_DATASET_ID="GA4_CAMPAIGN"           # default: GA4_CAMPAIGN
export BQ_LOCATION="US"                        # default: US
export GA4_TIMEZONE="America/Sao_Paulo"        # default: America/Sao_Paulo
export PORT="8080"                             # default: 8080
export DEBUG="false"                           # default: false
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

## Uso

### Executar Localmente

```bash
# Iniciar servidor
python main.py

# Inicializar tabelas via CLI
python main.py --init-tables

# Extrair dados via CLI
python main.py --extract <property_id> [start_date] [end_date]

# Ajuda
python main.py --help
```

### Endpoints da API

#### Health Check
```bash
GET /
```

#### Listar Dimensoes Disponiveis
```bash
GET /dimensions
```

#### Obter Metadados da Propriedade GA4
```bash
GET /metadata?property_id=123456789
# ou
POST /metadata
{"property_id": "123456789"}
```

#### Inicializar Tabelas no BigQuery
```bash
POST /init-tables
{
    "dataset_id": "CUSTOM_DATASET"  // opcional
}
```

#### Extrair Todas as Dimensoes
```bash
POST /extract
{
    "property_id": "123456789",        // obrigatorio
    "start_date": "2024-01-01",        // opcional (default: D-1)
    "end_date": "2024-01-01",          // opcional (default: D-1)
    "dimensions": ["CAMPAIGN", "USER"], // opcional (default: todas)
    "dataset_id": "CUSTOM_DATASET",    // opcional
    "table_prefix": "PREFIX",          // opcional
    "init_tables": true                // opcional (default: true)
}
```

#### Extrair Dimensao Especifica
```bash
POST /extract/CAMPAIGN
{
    "property_id": "123456789",
    "start_date": "2024-01-01",
    "end_date": "2024-01-01"
}
```

## Deploy no Cloud Run

### Build da Imagem Docker

```bash
# Build local
docker build -t ga4-campaign-api .

# Build para Artifact Registry
gcloud builds submit --tag gcr.io/SEU_PROJETO/ga4-campaign-api
```

### Deploy

```bash
gcloud run deploy ga4-campaign-api \
    --image gcr.io/SEU_PROJETO/ga4-campaign-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=seu-projeto,GA4_PROPERTY_ID=123456789,BQ_DATASET_ID=GA4_CAMPAIGN"
```

## Exemplo de Uso com Cloud Composer (Airflow)

```python
from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ga4_campaign_extraction',
    default_args=default_args,
    schedule_interval='0 6 * * *',  # Diariamente as 6h
    catchup=False
)

extract_task = SimpleHttpOperator(
    task_id='extract_ga4_data',
    http_conn_id='ga4_api',
    endpoint='/extract',
    method='POST',
    data='{"property_id": "123456789"}',
    headers={'Content-Type': 'application/json'},
    dag=dag
)
```

## Estrutura do Projeto

```
ga4-campaign/
├── main.py              # API Flask principal
├── config.py            # Configuracoes
├── gcp_connection.py    # Conexao com GCP
├── schemas.py           # Schemas das tabelas BigQuery
├── bigquery_client.py   # Cliente BigQuery
├── ga4_extractor.py     # Extracao de dados GA4
├── requirements.txt     # Dependencias Python
├── Dockerfile           # Imagem Docker
└── README.md            # Documentacao
```

## Joins entre Tabelas

As tabelas podem ser relacionadas usando a chave `GA4_SESSION_KEY`:

```sql
SELECT
    c.CAMPAIGN_NAME,
    c.SESSIONS,
    g.COUNTRY,
    g.CITY
FROM `projeto.dataset.GA4_DIM_CAMPAIGN` c
JOIN `projeto.dataset.GA4_DIM_GEOGRAPHIC` g
    ON c.GA4_SESSION_KEY = g.GA4_SESSION_KEY
    AND c.DATE = g.DATE
WHERE c.DATE = '2024-01-01'
```

## Referencia

Baseado nos exemplos oficiais do Google Analytics Data API:
- [python-docs-samples/google-analytics-data](https://github.com/googleanalytics/python-docs-samples/tree/main/google-analytics-data)

## Licenca

MIT License
