"""
Arquivo de configuração de exemplo

Copie este arquivo para config.py e preencha com suas informações
"""

import os

# ID da propriedade do Google Analytics 4
# Você pode encontrar este ID em: Admin > Propriedade > Detalhes da propriedade
GA4_PROPERTY_ID = os.getenv('GA4_PROPERTY_ID', 'SEU-PROPERTY-ID-AQUI')

# Caminho para o arquivo de credenciais JSON
# Para obter este arquivo:
# 1. Acesse https://console.cloud.google.com
# 2. Selecione seu projeto
# 3. Vá para "IAM e administrador" > "Contas de serviço"
# 4. Crie uma nova conta de serviço ou use uma existente
# 5. Baixe a chave JSON
# 6. Certifique-se de que a conta de serviço tem permissão "Visualizador" na propriedade GA4
GA4_CREDENTIALS_PATH = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

# Ou use um dicionário de credenciais diretamente
GA4_CREDENTIALS_DICT = {
    # "type": "service_account",
    # "project_id": "seu-project-id",
    # "private_key_id": "...",
    # "private_key": "...",
    # "client_email": "...",
    # "client_id": "...",
    # "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    # "token_uri": "https://oauth2.googleapis.com/token",
    # "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    # "client_x509_cert_url": "..."
}

# Configurações opcionais
DEFAULT_DATE_RANGE_START = '7daysAgo'
DEFAULT_DATE_RANGE_END = 'today'
DEFAULT_LIMIT = 10000
DEFAULT_OFFSET = 0

# Dimensões mais comuns para usar nos relatórios
COMMON_DIMENSIONS = [
    'country',           # País
    'city',              # Cidade
    'date',              # Data
    'pagePath',          # Caminho da página
    'pageTitle',         # Título da página
    'deviceCategory',    # Categoria do dispositivo
    'browser',           # Navegador
    'operatingSystem',   # Sistema operacional
    'sessionSource',     # Fonte da sessão
    'sessionMedium',     # Meio da sessão
    'eventName',         # Nome do evento
]

# Métricas mais comuns para usar nos relatórios
COMMON_METRICS = [
    'activeUsers',              # Usuários ativos
    'newUsers',                 # Novos usuários
    'sessions',                 # Sessões
    'screenPageViews',          # Visualizações de página
    'eventCount',               # Contagem de eventos
    'conversions',              # Conversões
    'totalRevenue',             # Receita total
    'averageSessionDuration',   # Duração média da sessão
    'bounceRate',               # Taxa de rejeição
    'engagementRate',           # Taxa de engajamento
]
