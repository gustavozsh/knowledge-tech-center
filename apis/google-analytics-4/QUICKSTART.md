# 🚀 Guia de Início Rápido

Este guia irá ajudá-lo a começar a usar a API do Google Analytics 4 em poucos minutos.

## Passo 1: Instalar Dependências

```bash
cd apis/google-analytics-4
pip install -r requirements.txt
```

## Passo 2: Obter Credenciais

### 2.1. Criar Conta de Serviço

1. Acesse https://console.cloud.google.com
2. Selecione ou crie um projeto
3. No menu lateral, vá para **IAM e administrador** > **Contas de serviço**
4. Clique em **+ CRIAR CONTA DE SERVIÇO**
5. Preencha:
   - Nome: `ga4-api-reader`
   - Descrição: `Conta para ler dados do GA4`
6. Clique em **CRIAR E CONTINUAR**
7. Clique em **CONCLUIR** (não precisa adicionar papéis aqui)

### 2.2. Gerar Chave JSON

1. Clique na conta de serviço criada
2. Vá para a aba **CHAVES**
3. Clique em **ADICIONAR CHAVE** > **Criar nova chave**
4. Selecione **JSON**
5. Clique em **CRIAR**
6. Salve o arquivo baixado como `credentials.json` na pasta `apis/google-analytics-4/`

### 2.3. Ativar API

1. No menu lateral, vá para **APIs e serviços** > **Biblioteca**
2. Procure por "Google Analytics Data API"
3. Clique e depois em **ATIVAR**

### 2.4. Dar Permissão no GA4

1. Acesse https://analytics.google.com
2. Clique em **Admin** (engrenagem inferior esquerda)
3. Na coluna **Propriedade**, clique em **Acesso à propriedade**
4. Clique em **+** (Adicionar usuários)
5. Cole o email da conta de serviço (está no arquivo credentials.json no campo `client_email`)
6. Marque **Visualizador**
7. Clique em **Adicionar**

### 2.5. Obter Property ID

1. No Google Analytics, em **Admin**
2. Na coluna **Propriedade**, clique em **Detalhes da propriedade**
3. Copie o **ID da propriedade** (números apenas, ex: 123456789)

## Passo 3: Configurar Variáveis de Ambiente

### Linux/Mac:

```bash
export GA4_PROPERTY_ID='seu-property-id'
export GA4_CREDENTIALS_PATH='credentials.json'
```

### Windows (PowerShell):

```powershell
$env:GA4_PROPERTY_ID='seu-property-id'
$env:GA4_CREDENTIALS_PATH='credentials.json'
```

### Ou crie um arquivo `.env`:

```
GA4_PROPERTY_ID=123456789
GA4_CREDENTIALS_PATH=credentials.json
```

## Passo 4: Executar o Primeiro Exemplo

```bash
cd examples
python basic_example.py
```

Se tudo estiver configurado corretamente, você verá os dados do seu Google Analytics 4!

## Passo 5: Testar Código Próprio

Crie um arquivo `test.py`:

```python
import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ga4_client import GA4Client
from models import DateRange, Dimension, Metric, RunReportRequest

# Suas credenciais
property_id = os.getenv('GA4_PROPERTY_ID')
credentials_path = os.getenv('GA4_CREDENTIALS_PATH')

# Criar cliente
client = GA4Client(
    property_id=property_id,
    credentials_path=credentials_path
)

# Criar requisição
request = RunReportRequest(
    property_id=property_id,
    date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
    dimensions=[Dimension(name='country')],
    metrics=[Metric(name='activeUsers')],
    limit=10
)

# Executar
response = client.run_report(request)

# Mostrar resultados
print(f"Total de países: {response['row_count']}")
for row in response['rows']:
    print(f"{row['dimensions']['country']}: {row['metrics']['activeUsers']} usuários")
```

Execute:

```bash
python test.py
```

## 🎉 Pronto!

Agora você pode:

1. ✅ Executar relatórios do GA4
2. ✅ Filtrar dados
3. ✅ Ordenar resultados
4. ✅ Exportar para JSON/CSV
5. ✅ Usar relatórios em tempo real

## 📚 Próximos Passos

- Explore o arquivo `examples/advanced_example.py` para ver funcionalidades avançadas
- Leia o `README.md` para documentação completa
- Consulte `src/models.py` para ver todas as opções disponíveis

## ❓ Problemas Comuns

### Erro: "credentials.json not found"

- Certifique-se de que o arquivo `credentials.json` está no diretório correto
- Verifique o caminho nas variáveis de ambiente

### Erro: "Permission denied"

- Verifique se você adicionou a conta de serviço no GA4 com permissão de Visualizador
- Aguarde alguns minutos para as permissões propagarem

### Erro: "API has not been enabled"

- Ative a "Google Analytics Data API" no Google Cloud Console
- Aguarde alguns minutos para a API ser ativada

### Erro: "Property not found"

- Verifique se o Property ID está correto
- Certifique-se de usar apenas os números (ex: 123456789, não properties/123456789)

## 🆘 Ajuda

Se continuar com problemas:

1. Verifique se seguiu todos os passos
2. Confirme que as variáveis de ambiente estão configuradas
3. Teste o exemplo básico primeiro antes de criar código próprio
4. Consulte a documentação oficial do Google Analytics Data API
