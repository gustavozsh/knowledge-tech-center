"""
Exemplo básico de uso da API do Google Analytics 4

Este exemplo demonstra como:
1. Inicializar o cliente
2. Criar uma requisição simples
3. Executar o relatório
4. Processar os resultados
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ga4_client import GA4Client
from models import DateRange, Dimension, Metric, RunReportRequest


def main():
    """Exemplo básico de uso"""

    # 1. Configurar credenciais
    # Opção 1: Usar arquivo de credenciais
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    # Opção 2: Ou usar variável de ambiente GOOGLE_APPLICATION_CREDENTIALS
    # export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

    # 2. Inicializar o cliente
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')

    print("Inicializando cliente GA4...")
    try:
        client = GA4Client(
            property_id=property_id,
            credentials_path=credentials_path
        )
        print(f"✓ Cliente inicializado: {client}")
    except Exception as e:
        print(f"✗ Erro ao inicializar cliente: {e}")
        print("\nCertifique-se de:")
        print("1. Definir GA4_PROPERTY_ID com seu ID de propriedade")
        print("2. Definir GA4_CREDENTIALS_PATH ou GOOGLE_APPLICATION_CREDENTIALS")
        return

    # 3. Criar uma requisição simples
    print("\nCriando requisição...")
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

    # 4. Executar o relatório
    print("\nExecutando relatório...")
    try:
        response = client.run_report(request)
        print(f"✓ Relatório executado com sucesso!")
        print(f"  Total de linhas: {response['row_count']}")

        # 5. Processar resultados
        print("\n" + "="*80)
        print("RESULTADOS")
        print("="*80)

        print("\nDimensões:", ", ".join(response['dimension_headers']))
        print("Métricas:", ", ".join([m['name'] for m in response['metric_headers']]))

        print("\nPrimeiras 10 linhas:")
        print("-"*80)

        for i, row in enumerate(response['rows'], 1):
            dims = " | ".join([f"{k}: {v}" for k, v in row['dimensions'].items()])
            mets = " | ".join([f"{k}: {v}" for k, v in row['metrics'].items()])
            print(f"{i}. {dims}")
            print(f"   {mets}")

        # 6. Metadados
        if response.get('metadata'):
            print("\n" + "="*80)
            print("METADADOS")
            print("="*80)
            print(f"Moeda: {response['metadata'].get('currency_code', 'N/A')}")
            print(f"Fuso horário: {response['metadata'].get('time_zone', 'N/A')}")

        # 7. Exportar para JSON
        print("\n" + "="*80)
        print("EXPORTANDO DADOS")
        print("="*80)

        json_path = 'output_basic.json'
        client.export_to_json(response, json_path)
        print(f"✓ Dados exportados para {json_path}")

        csv_path = 'output_basic.csv'
        client.export_to_csv(response, csv_path)
        print(f"✓ Dados exportados para {csv_path}")

    except Exception as e:
        print(f"✗ Erro ao executar relatório: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
