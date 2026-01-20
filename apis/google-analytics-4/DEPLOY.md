# 🚀 Guia de Deploy no Google Cloud Run

Este guia mostra como fazer o deploy da API do Google Analytics 4 no Google Cloud Run.

## 📋 Pré-requisitos

1. **Google Cloud Project** criado
2. **gcloud CLI** instalado e configurado
3. **Docker** instalado (opcional, Cloud Build fará o build)
4. **APIs habilitadas** no GCP:
   - Cloud Run API
   - Cloud Build API
   - Secret Manager API
   - BigQuery API
   - Google Analytics Data API

## 🔧 Configuração Inicial

### 1. Configurar gcloud CLI

```bash
# Fazer login
gcloud auth login

# Configurar projeto
gcloud config set project YOUR-PROJECT-ID

# Habilitar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable analyticsdata.googleapis.com
```

### 2. Criar Secret no Secret Manager

#### Opção A: Via Console

1. Acesse https://console.cloud.google.com/security/secret-manager
2. Clique em **Criar Secret**
3. Nome: `ga4-credentials`
4. Valor: Cole o conteúdo completo do arquivo JSON de credenciais da conta de serviço
5. Clique em **Criar Secret**

#### Opção B: Via CLI

```bash
# Criar secret a partir de arquivo
gcloud secrets create ga4-credentials \
    --data-file=./path/to/service-account-key.json

# Ou criar secret a partir de string
cat service-account-key.json | gcloud secrets create ga4-credentials \
    --data-file=-
```

### 3. Criar Dataset no BigQuery

```bash
# Criar dataset RAW
bq mk --dataset --location=US YOUR-PROJECT-ID:RAW

# Verificar
bq ls
```

## 🏗️ Build e Deploy

### Opção 1: Deploy Direto (Recomendado)

```bash
# Navegar para o diretório da API
cd apis/google-analytics-4

# Deploy no Cloud Run (build automático)
gcloud run deploy ga4-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars PROJECT_ID=YOUR-PROJECT-ID
```

### Opção 2: Build Manual com Docker

```bash
# Build da imagem
docker build -t gcr.io/YOUR-PROJECT-ID/ga4-api:latest .

# Push para Google Container Registry
docker push gcr.io/YOUR-PROJECT-ID/ga4-api:latest

# Deploy no Cloud Run
gcloud run deploy ga4-api \
    --image gcr.io/YOUR-PROJECT-ID/ga4-api:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300
```

### Opção 3: Build com Cloud Build

```bash
# Submit build para Cloud Build
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/ga4-api

# Deploy
gcloud run deploy ga4-api \
    --image gcr.io/YOUR-PROJECT-ID/ga4-api:latest \
    --platform managed \
    --region us-central1
```

## 🔐 Permissões

### Dar permissões à Service Account do Cloud Run

```bash
# Obter email da service account
SERVICE_ACCOUNT=$(gcloud run services describe ga4-api \
    --platform managed \
    --region us-central1 \
    --format 'value(spec.template.spec.serviceAccountName)')

# Permissão para Secret Manager
gcloud secrets add-iam-policy-binding ga4-credentials \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"

# Permissão para BigQuery
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/bigquery.jobUser"
```

## ✅ Testar o Deployment

### 1. Health Check

```bash
# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe ga4-api \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)')

# Testar health check
curl $SERVICE_URL/
```

### 2. Executar Relatório de Teste

```bash
curl -X POST $SERVICE_URL/run-report \
    -H "Content-Type: application/json" \
    -d '{
        "project_id": "YOUR-PROJECT-ID",
        "secret_id": "ga4-credentials",
        "property_id": "YOUR-GA4-PROPERTY-ID",
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
        "limit": 10
    }'
```

## 📊 Verificar Dados no BigQuery

```bash
# Ver dados inseridos
bq query --use_legacy_sql=false \
    'SELECT * FROM `YOUR-PROJECT-ID.RAW.ga4_daily_report` LIMIT 10'

# Contar registros
bq query --use_legacy_sql=false \
    'SELECT COUNT(*) as total FROM `YOUR-PROJECT-ID.RAW.ga4_daily_report`'
```

## 🔄 Atualizar o Serviço

```bash
# Após fazer mudanças no código
cd apis/google-analytics-4

# Redeploy
gcloud run deploy ga4-api \
    --source . \
    --platform managed \
    --region us-central1
```

## 🎛️ Configurações Avançadas

### Configurar Autenticação (Recomendado para Produção)

```bash
# Deploy com autenticação obrigatória
gcloud run deploy ga4-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --no-allow-unauthenticated

# Dar permissão para invocar o serviço
gcloud run services add-iam-policy-binding ga4-api \
    --platform managed \
    --region us-central1 \
    --member="user:YOUR-EMAIL@example.com" \
    --role="roles/run.invoker"
```

### Configurar VPC Connector (para acesso privado)

```bash
gcloud run deploy ga4-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --vpc-connector YOUR-VPC-CONNECTOR \
    --vpc-egress all-traffic
```

### Configurar Variáveis de Ambiente

```bash
gcloud run deploy ga4-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --set-env-vars "PROJECT_ID=YOUR-PROJECT-ID,DATASET_ID=RAW"
```

### Configurar Limites de Recursos

```bash
gcloud run deploy ga4-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900 \
    --concurrency 80 \
    --min-instances 1 \
    --max-instances 100
```

## 📝 Monitoramento

### Ver Logs

```bash
# Logs em tempo real
gcloud run services logs tail ga4-api \
    --platform managed \
    --region us-central1

# Logs recentes
gcloud run services logs read ga4-api \
    --platform managed \
    --region us-central1 \
    --limit 50
```

### Métricas no Console

1. Acesse https://console.cloud.google.com/run
2. Clique no serviço `ga4-api`
3. Veja métricas de:
   - Requisições por segundo
   - Latência
   - Utilização de CPU/Memória
   - Erros

## 🔒 Segurança

### Boas Práticas

1. **Sempre use autenticação** em produção
2. **Use Secret Manager** para credenciais (nunca hardcode)
3. **Configure CORS** se necessário:
   ```python
   from flask_cors import CORS
   CORS(app, resources={r"/*": {"origins": "https://yourdomain.com"}})
   ```
4. **Use HTTPS** (Cloud Run fornece automaticamente)
5. **Configure alertas** de erro e latência
6. **Limite o número de instâncias** para controlar custos

## 💰 Custos

Custos do Cloud Run são baseados em:
- CPU e memória utilizados (por 100ms)
- Número de requisições
- Tráfego de rede

**Nível Gratuito:**
- 2 milhões de requisições/mês
- 360,000 GB-segundos de memória/mês
- 180,000 vCPU-segundos/mês

Para reduzir custos:
- Use `--min-instances 0` (padrão)
- Configure timeout adequado
- Otimize código para execução rápida

## 🆘 Troubleshooting

### Erro: "Permission denied"

```bash
# Verificar permissões do Secret Manager
gcloud secrets get-iam-policy ga4-credentials

# Adicionar permissão
gcloud secrets add-iam-policy-binding ga4-credentials \
    --member="serviceAccount:YOUR-SERVICE-ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

### Erro: "Deadline exceeded"

```bash
# Aumentar timeout
gcloud run deploy ga4-api \
    --source . \
    --timeout 900
```

### Erro: "Out of memory"

```bash
# Aumentar memória
gcloud run deploy ga4-api \
    --source . \
    --memory 2Gi
```

### Ver detalhes do serviço

```bash
gcloud run services describe ga4-api \
    --platform managed \
    --region us-central1
```

## 📚 Recursos Adicionais

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)
- [BigQuery](https://cloud.google.com/bigquery/docs)

## ✨ Próximos Passos

Após o deploy bem-sucedido:

1. Configure agendamento com **Cloud Scheduler**
2. Adicione alertas com **Cloud Monitoring**
3. Configure CI/CD com **Cloud Build triggers**
4. Implemente rate limiting se necessário
5. Configure backup dos dados no BigQuery
