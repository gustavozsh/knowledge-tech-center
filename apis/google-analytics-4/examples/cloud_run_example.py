"""
Exemplo de uso da API conforme padrão Cloud Run

Este exemplo mostra como usar a API exatamente como será usado no Cloud Run,
com Secret Manager, BigQuery e GoogleAnalytics4.
"""

import json
import os
import sys

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from secret_manager import SecretManager
from ga4_client import GoogleAnalytics4
from bigquery_writer import BigQueryWriter
from models import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2.service_account import Credentials


def main():
    """
    Exemplo completo usando o padrão Cloud Run
    """
    # Configurações (normalmente viriam de variáveis de ambiente ou request)
    project_id = os.getenv('PROJECT_ID', 'your-project-id')
    secret_id = os.getenv('SECRET_ID', 'ga4-credentials')
    property_id = os.getenv('GA4_PROPERTY_ID', 'your-property-id')
    bigquery_table = 'ga4_daily_report'
    bigquery_dataset = 'RAW'

    print("="*80)
    print("EXEMPLO: Uso da API no padrão Cloud Run")
    print("="*80)

    # 1. Buscar credenciais do Secret Manager
    print("\n1. Buscando credenciais do Secret Manager...")
    try:
        secret_manager = SecretManager()
        secret_value = secret_manager.access_secret_version(
            secret_id=secret_id,
            project_id=project_id
        )
        print(f"✓ Secret '{secret_id}' obtido com sucesso")
    except Exception as e:
        print(f"✗ Erro ao buscar secret: {e}")
        print("\nCertifique-se de:")
        print("1. Criar o secret no Secret Manager")
        print("2. Configurar as variáveis de ambiente")
        print("3. Dar permissões adequadas")
        return

    # 2. Carregar JSON e criar objeto Credentials
    print("\n2. Criando objeto Credentials...")
    try:
        service_account_json = json.loads(secret_value)
        credentials_service_account_json = Credentials.from_service_account_info(
            service_account_json
        )
        print("✓ Credentials criado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao criar credentials: {e}")
        return

    # 3. Instanciar GoogleAnalytics4
    print("\n3. Instanciando GoogleAnalytics4...")
    try:
        ga4 = GoogleAnalytics4(credentials_service_account_json)
        print(f"✓ GoogleAnalytics4 instanciado: {ga4}")
    except Exception as e:
        print(f"✗ Erro ao instanciar GoogleAnalytics4: {e}")
        return

    # 4. Criar requisição
    print("\n4. Criando requisição de relatório...")
    try:
        request = RunReportRequest(
            property_id=property_id,
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
        print(f"✓ Requisição criada: {request}")
    except Exception as e:
        print(f"✗ Erro ao criar requisição: {e}")
        return

    # 5. Executar relatório
    print("\n5. Executando relatório do GA4...")
    try:
        response = ga4.run_report(request)
        print(f"✓ Relatório executado com sucesso!")
        print(f"  Total de linhas: {response['row_count']}")
        print(f"  Dimensões: {response['dimension_headers']}")
        print(f"  Métricas: {[m['name'] for m in response['metric_headers']]}")
    except Exception as e:
        print(f"✗ Erro ao executar relatório: {e}")
        return

    # 6. Mostrar primeiros resultados
    print("\n6. Primeiros resultados:")
    print("-"*80)
    for i, row in enumerate(response['rows'][:5], 1):
        country = row['dimensions']['country']
        city = row['dimensions']['city']
        users = row['metrics']['activeUsers']
        sessions = row['metrics']['sessions']
        print(f"{i}. {country} - {city}")
        print(f"   Usuários ativos: {users}, Sessões: {sessions}")

    # 7. Salvar no BigQuery
    print("\n7. Salvando dados no BigQuery...")
    try:
        bq_writer = BigQueryWriter(
            project_id=project_id,
            dataset_id=bigquery_dataset,
            credentials=credentials_service_account_json
        )
        print(f"✓ BigQueryWriter criado: {bq_writer}")

        bq_writer.write_ga4_data(
            table_id=bigquery_table,
            data=response,
            auto_create=True
        )
        print(f"✓ Dados salvos em {project_id}.{bigquery_dataset}.{bigquery_table}")

    except Exception as e:
        print(f"✗ Erro ao salvar no BigQuery: {e}")
        print("Nota: Isso pode falhar se você não tiver permissões no BigQuery")

    # 8. Resumo
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    print(f"✓ Credenciais obtidas do Secret Manager")
    print(f"✓ Relatório executado no GA4")
    print(f"✓ {response['row_count']} linhas processadas")
    print(f"✓ Dados salvos no BigQuery (se permissões OK)")
    print("\n🎉 Processo completo executado com sucesso!")


if __name__ == '__main__':
    print("""
    Para executar este exemplo, configure:

    export PROJECT_ID='your-project-id'
    export SECRET_ID='ga4-credentials'
    export GA4_PROPERTY_ID='your-property-id'

    E certifique-se de que:
    1. O secret existe no Secret Manager
    2. Você tem permissões para acessar o secret
    3. Você tem permissões no BigQuery
    """)

    main()
