# Google Analytics 4 API Wrapper

Uma API wrapper completa em Python para interagir com o Google Analytics 4 Data API, permitindo extrair e analisar dados de forma simples e eficiente.

## 🎯 Funcionalidades

- ✅ **DateRange**: Definição de intervalos de datas para análises
- ✅ **Dimension**: Configuração de dimensões (país, cidade, dispositivo, etc.)
- ✅ **Metric**: Configuração de métricas (usuários ativos, sessões, conversões, etc.)
- ✅ **RunReportRequest**: Execução de relatórios personalizados
- ✅ **Filtros avançados**: Filtros de dimensões e métricas com operadores AND/OR/NOT
- ✅ **Ordenação**: Ordenação de resultados por dimensões ou métricas
- ✅ **Relatórios em tempo real**: Dados de usuários ativos agora
- ✅ **Relatórios em lote**: Executar múltiplos relatórios em uma única chamada
- ✅ **Metadados**: Listar todas as dimensões e métricas disponíveis
- ✅ **Exportação**: Exportar dados para JSON e CSV
- ✅ **Execução local**: Pode ser executado completamente local

## 📋 Requisitos

- Python 3.8 ou superior
- Conta do Google Analytics 4
- Credenciais de conta de serviço do Google Cloud

## 🚀 Instalação

1. Clone ou baixe este repositório

2. Instale as dependências:

```bash
cd apis/google-analytics-4
pip install -r requirements.txt
```

## 🔑 Configuração de Credenciais

### 1. Criar uma Conta de Serviço

1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Selecione ou crie um projeto
3. Vá para **IAM e administrador** > **Contas de serviço**
4. Clique em **Criar conta de serviço**
5. Preencha os detalhes e clique em **Criar**
6. Na etapa de permissões, adicione o papel necessário
7. Clique em **Concluir**

### 2. Gerar Chave JSON

1. Na lista de contas de serviço, clique na conta criada
2. Vá para a aba **Chaves**
3. Clique em **Adicionar chave** > **Criar nova chave**
4. Selecione **JSON** e clique em **Criar**
5. O arquivo JSON será baixado automaticamente

### 3. Dar Permissões no GA4

1. Acesse o [Google Analytics](https://analytics.google.com)
2. Vá para **Admin** (engrenagem no canto inferior esquerdo)
3. Na coluna **Propriedade**, clique em **Acesso à propriedade**
4. Clique em **Adicionar usuários**
5. Adicione o email da conta de serviço (encontrado no arquivo JSON)
6. Selecione o papel **Visualizador**
7. Clique em **Adicionar**

### 4. Obter o Property ID

1. No Google Analytics, vá para **Admin**
2. Na coluna **Propriedade**, clique em **Detalhes da propriedade**
3. Copie o **ID da propriedade** (formato: 123456789)

### 5. Configurar Variáveis de Ambiente

```bash
export GA4_PROPERTY_ID='seu-property-id'
export GA4_CREDENTIALS_PATH='/caminho/para/credentials.json'
```

Ou crie um arquivo `.env`:

```
GA4_PROPERTY_ID=123456789
GA4_CREDENTIALS_PATH=/caminho/para/credentials.json
```

## 💡 Uso Básico

### Exemplo Simples

```python
from src.ga4_client import GA4Client
from src.models import DateRange, Dimension, Metric, RunReportRequest

# Inicializar o cliente
client = GA4Client(
    property_id='123456789',
    credentials_path='credentials.json'
)

# Criar requisição
request = RunReportRequest(
    property_id='123456789',
    date_ranges=[
        DateRange(start_date='7daysAgo', end_date='today')
    ],
    dimensions=[
        Dimension(name='country'),
        Dimension(name='city')
    ],
    metrics=[
        Metric(name='activeUsers'),
        Metric(name='sessions')
    ],
    limit=10
)

# Executar relatório
response = client.run_report(request)

# Processar resultados
for row in response['rows']:
    print(f"País: {row['dimensions']['country']}")
    print(f"Cidade: {row['dimensions']['city']}")
    print(f"Usuários: {row['metrics']['activeUsers']}")
    print(f"Sessões: {row['metrics']['sessions']}")
    print("---")
```

### Executar Exemplos

```bash
# Exemplo básico
cd examples
python basic_example.py

# Exemplo avançado (filtros, ordenação, etc.)
python advanced_example.py
```

## 📊 Modelos

### DateRange

Define intervalos de datas para consultas:

```python
# Datas relativas
DateRange(start_date='7daysAgo', end_date='today')
DateRange(start_date='yesterday', end_date='yesterday')
DateRange(start_date='30daysAgo', end_date='today', name='Último Mês')

# Datas específicas
DateRange(start_date='2024-01-01', end_date='2024-01-31')

# Múltiplos intervalos (comparação)
date_ranges = [
    DateRange(start_date='14daysAgo', end_date='8daysAgo', name='Semana Passada'),
    DateRange(start_date='7daysAgo', end_date='today', name='Esta Semana')
]
```

### Dimension

Define as dimensões para análise:

```python
# Dimensões comuns
Dimension(name='country')           # País
Dimension(name='city')              # Cidade
Dimension(name='date')              # Data
Dimension(name='pagePath')          # Caminho da página
Dimension(name='deviceCategory')    # Categoria do dispositivo
Dimension(name='browser')           # Navegador
Dimension(name='sessionSource')     # Fonte da sessão
Dimension(name='eventName')         # Nome do evento
```

### Metric

Define as métricas para coletar:

```python
# Métricas comuns
Metric(name='activeUsers')              # Usuários ativos
Metric(name='newUsers')                 # Novos usuários
Metric(name='sessions')                 # Sessões
Metric(name='screenPageViews')          # Visualizações
Metric(name='eventCount')               # Contagem de eventos
Metric(name='conversions')              # Conversões
Metric(name='totalRevenue')             # Receita total
Metric(name='averageSessionDuration')   # Duração média
Metric(name='bounceRate')               # Taxa de rejeição
```

### RunReportRequest

Configura e executa relatórios:

```python
request = RunReportRequest(
    property_id='123456789',
    date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
    dimensions=[Dimension(name='country')],
    metrics=[Metric(name='activeUsers')],
    limit=100,
    offset=0,
    keep_empty_rows=False
)
```

## 🔍 Funcionalidades Avançadas

### Filtros

```python
from src.models import FilterExpression

# Filtro de string
brazil_filter = FilterExpression.string_filter(
    dimension_name='country',
    value='Brazil',
    match_type='EXACT'
)

# Filtro numérico
sessions_filter = FilterExpression.numeric_filter(
    metric_name='sessions',
    value=100,
    operation='GREATER_THAN'
)

# Filtro de lista
countries_filter = FilterExpression.in_list_filter(
    dimension_name='country',
    values=['Brazil', 'Argentina', 'Chile']
)

# Combinar filtros (AND)
combined_filter = FilterExpression.and_group([
    brazil_filter,
    sessions_filter
])

# Usar no request
request = RunReportRequest(
    property_id='123456789',
    date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
    dimensions=[Dimension(name='country')],
    metrics=[Metric(name='sessions')],
    dimension_filter=brazil_filter,
    metric_filter=sessions_filter
)
```

### Ordenação

```python
from src.models import OrderBy

# Ordenar por métrica (decrescente)
request = RunReportRequest(
    property_id='123456789',
    date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
    dimensions=[Dimension(name='country')],
    metrics=[Metric(name='activeUsers')],
    order_bys=[
        OrderBy(metric_name='activeUsers', desc=True)
    ]
)

# Ordenar por dimensão
request = RunReportRequest(
    property_id='123456789',
    date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
    dimensions=[Dimension(name='country')],
    metrics=[Metric(name='activeUsers')],
    order_bys=[
        OrderBy(dimension_name='country', desc=False)
    ]
)
```

### Relatórios em Tempo Real

```python
response = client.run_realtime_report(
    dimensions=[
        Dimension(name='country'),
        Dimension(name='unifiedScreenName')
    ],
    metrics=[
        Metric(name='activeUsers')
    ],
    limit=10
)
```

### Relatórios em Lote

```python
requests = [
    RunReportRequest(...),
    RunReportRequest(...),
    RunReportRequest(...)
]

responses = client.batch_run_reports(requests)
```

### Obter Metadados

```python
# Listar todas dimensões e métricas disponíveis
metadata = client.get_metadata()

print(f"Dimensões: {len(metadata['dimensions'])}")
print(f"Métricas: {len(metadata['metrics'])}")

for dim in metadata['dimensions']:
    print(f"- {dim['api_name']}: {dim['ui_name']}")
```

### Exportação

```python
# Exportar para JSON
client.export_to_json(response, 'output.json')

# Exportar para CSV
client.export_to_csv(response, 'output.csv')
```

## 📁 Estrutura do Projeto

```
google-analytics-4/
├── src/
│   ├── __init__.py
│   ├── ga4_client.py      # Cliente principal
│   └── models.py          # Modelos (DateRange, Dimension, Metric, etc.)
├── examples/
│   ├── __init__.py
│   ├── basic_example.py   # Exemplo básico
│   ├── advanced_example.py # Exemplos avançados
│   └── config.example.py  # Configuração de exemplo
├── tests/
│   └── (testes unitários)
├── requirements.txt       # Dependências
└── README.md             # Esta documentação
```

## 🧪 Testes

```bash
# Executar testes (quando disponíveis)
pytest tests/
```

## 📖 Recursos Úteis

- [Documentação oficial GA4 Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Referência de Dimensões e Métricas](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
- [Guia de filtros](https://developers.google.com/analytics/devguides/reporting/data/v1/basics#filtering)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📝 Licença

Este projeto está sob a licença especificada no arquivo LICENSE do repositório principal.

## ⚠️ Observações

- Esta API requer credenciais válidas do Google Cloud
- Certifique-se de que a conta de serviço tem as permissões adequadas
- A API tem limites de quota - consulte a documentação do Google para mais detalhes
- Para ambientes de produção, considere usar variáveis de ambiente para credenciais
- Nunca commite arquivos de credenciais no controle de versão

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique a documentação oficial do Google Analytics
2. Consulte os exemplos fornecidos
3. Abra uma issue no repositório

## ✨ Características

- **Totalmente tipado**: Usa type hints do Python
- **Bem documentado**: Docstrings completas em português
- **Exemplos práticos**: Vários exemplos de uso
- **Fácil de usar**: API intuitiva e simples
- **Exportação flexível**: Suporte para JSON e CSV
- **Execução local**: Não requer servidores externos
