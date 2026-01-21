# API de Extração de Dados do Google Analytics 4

**Autor:** Manus AI (a pedido de Gustavo)
**Data:** Janeiro de 2026
**Versão:** 2.0.0

---

## 1. Visão Geral

Esta API foi desenvolvida para automatizar a extração de dados do **Google Analytics 4 Data API v1beta** e realizar a carga em tabelas no **Google BigQuery**. O principal objetivo é permitir a coleta diária de dados de múltiplas propriedades GA4, organizando-os em tabelas específicas por categoria de dimensão e métrica.

A solução é implementada como uma API REST em **Python 3.12+ com Flask**, projetada para ser implantada no **Google Cloud Run**.

### 1.1. Estrutura Simplificada

A API foi refatorada para ter apenas **4 arquivos Python principais**:

```
/google-analytics-4
├── auth.py         # Autenticação GCP (PRIMEIRO a ser chamado)
├── ga4.py          # Extração de dados do GA4
├── bigquery.py     # Escrita no BigQuery
├── main.py         # API Flask (entrypoint)
├── Dockerfile      # Container para Cloud Run
├── requirements.txt
└── dags/           # DAGs Airflow
```

### 1.2. Fluxo de Execução

```
1. auth.py      → Autentica no GCP, Secret Manager, BigQuery e GA4
2. ga4.py       → Extrai dados do Google Analytics 4
3. bigquery.py  → Carrega dados no BigQuery
4. main.py      → Orquestra tudo via endpoints REST
```

---

## 2. Arquivos Principais

### 2.1. `auth.py` - Autenticação (PRIMEIRO)

Este módulo **deve ser importado primeiro** antes de qualquer outro. Ele fornece:

- `authenticate_gcp()` - Autentica no GCP usando várias fontes de credenciais
- `get_bigquery_client()` - Obtém cliente do BigQuery
- `get_ga4_client()` - Obtém cliente do GA4 Data API
- `get_secret()` - Recupera secrets do Secret Manager
- `initialize_all_clients()` - Inicializa todos os clientes de uma vez
- `test_authentication()` - Testa se a autenticação está funcionando

**Exemplo de uso:**
```python
from auth import initialize_all_clients

# Inicializa todos os clientes
clients = initialize_all_clients()

# Usar os clientes
bq_client = clients["bigquery"]
ga4_client = clients["ga4"]
```

### 2.2. `ga4.py` - Extração de Dados

Contém todas as funções para extrair dados do GA4:

- `run_ga4_report()` - Executa um relatório no GA4
- `extract_dimension_report()` - Extrai relatório de dimensão específico
- `extract_metric_report()` - Extrai relatório de métrica específico
- `extract_all_reports()` - Extrai todos os relatórios configurados
- `list_available_reports()` - Lista relatórios disponíveis

### 2.3. `bigquery.py` - Escrita no BigQuery

Contém todas as funções para interagir com o BigQuery:

- `create_table()` - Cria uma tabela
- `insert_rows()` - Insere linhas em uma tabela
- `load_report_to_bigquery()` - Carrega um relatório extraído
- `load_all_reports_to_bigquery()` - Carrega todos os relatórios

### 2.4. `main.py` - API Flask

O entrypoint da aplicação com endpoints REST:

- `GET /` - Health check
- `GET /test-auth` - Testa autenticação
- `GET /reports` - Lista relatórios disponíveis
- `POST /extract` - Extrai todos os dados de uma propriedade
- `POST /extract/dimension/<key>` - Extrai dimensão específica
- `POST /extract/metric/<key>` - Extrai métrica específica

---

## 3. Tabelas no BigQuery

### Tabelas de Dimensões

| Tabela | Descrição |
|--------|-----------|
| `RAW.TB_001_GA4_DIM_USUARIO` | Dimensões de usuário |
| `RAW.TB_002_GA4_DIM_GEOGRAFICA` | Dimensões geográficas |
| `RAW.TB_003_GA4_DIM_DISPOSITIVO` | Dimensões de dispositivo |
| `RAW.TB_004_GA4_DIM_AQUISICAO` | Dimensões de aquisição |
| `RAW.TB_005_GA4_DIM_PAGINA` | Dimensões de página |
| `RAW.TB_006_GA4_DIM_EVENTO` | Dimensões de evento |
| `RAW.TB_007_GA4_DIM_PUBLICO` | Dimensões de público |

### Tabelas de Métricas

| Tabela | Descrição |
|--------|-----------|
| `RAW.TB_008_GA4_MET_USUARIOS` | Métricas de usuários |
| `RAW.TB_009_GA4_MET_SESSAO` | Métricas de sessão |
| `RAW.TB_010_GA4_MET_EVENTOS` | Métricas de eventos |
| `RAW.TB_011_GA4_MET_VISUALIZACAO` | Métricas de visualização |
| `RAW.TB_012_GA4_MET_ECOMMERCE` | Métricas de e-commerce |

---

## 4. Como Usar

### 4.1. Testar Autenticação

```bash
# Via CLI
python main.py --test

# Via API
curl http://localhost:8080/test-auth
```

### 4.2. Extrair Dados via CLI

```bash
# Extrair dados de uma propriedade (D-1)
python main.py --extract 123456789

# Extrair dados com período específico
python main.py --extract 123456789 2024-01-01 2024-01-07
```

### 4.3. Extrair Dados via API

```bash
# Extrair todos os relatórios
curl -X POST http://localhost:8080/extract \
  -H "Content-Type: application/json" \
  -d '{"property_id": "123456789"}'

# Extrair dimensão específica
curl -X POST http://localhost:8080/extract/dimension/usuario \
  -H "Content-Type: application/json" \
  -d '{"property_id": "123456789"}'
```

---

## 5. Deploy no Cloud Run

### 5.1. Build e Push da Imagem

```bash
# Build
docker build -t gcr.io/cadastra-yduqs-uat/ga4-api:latest .

# Push
docker push gcr.io/cadastra-yduqs-uat/ga4-api:latest
```

### 5.2. Deploy

```bash
gcloud run deploy ga4-api \
  --image gcr.io/cadastra-yduqs-uat/ga4-api:latest \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated
```

---

## 6. Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `GCP_PROJECT_ID` | ID do projeto GCP | `cadastra-yduqs-uat` |
| `BQ_DATASET_ID` | ID do dataset BigQuery | `RAW` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Caminho para credenciais | - |
| `USE_SECRET_MANAGER` | Usar Secret Manager | `true` |
| `PORT` | Porta do servidor | `8080` |
| `DEBUG` | Modo debug | `false` |

---

## 7. Referências

- [Google Analytics Data API v1](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Google BigQuery](https://cloud.google.com/bigquery/docs)
