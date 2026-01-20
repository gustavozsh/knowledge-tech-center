"""
Exemplo avançado de uso da API do Google Analytics 4

Este exemplo demonstra funcionalidades avançadas:
1. Filtros de dimensões e métricas
2. Ordenação de resultados
3. Múltiplos intervalos de datas
4. Relatórios em tempo real
5. Relatórios em lote
6. Obtenção de metadados
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ga4_client import GA4Client
from models import (
    DateRange, Dimension, Metric, RunReportRequest,
    OrderBy, FilterExpression
)


def example_with_filters():
    """Exemplo usando filtros"""
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    client = GA4Client(property_id=property_id, credentials_path=credentials_path)

    print("\n" + "="*80)
    print("EXEMPLO 1: Filtros")
    print("="*80)

    # Filtrar apenas usuários do Brasil com mais de 100 sessões
    brazil_filter = FilterExpression.string_filter(
        dimension_name='country',
        value='Brazil',
        match_type='EXACT'
    )

    sessions_filter = FilterExpression.numeric_filter(
        metric_name='sessions',
        value=100,
        operation='GREATER_THAN'
    )

    request = RunReportRequest(
        property_id=property_id,
        date_ranges=[DateRange(start_date='30daysAgo', end_date='today')],
        dimensions=[
            Dimension(name='country'),
            Dimension(name='city')
        ],
        metrics=[
            Metric(name='activeUsers'),
            Metric(name='sessions'),
            Metric(name='screenPageViews')
        ],
        dimension_filter=brazil_filter,
        metric_filter=sessions_filter,
        limit=5
    )

    try:
        response = client.run_report(request)
        print(f"✓ Total de resultados: {response['row_count']}")
        for i, row in enumerate(response['rows'], 1):
            print(f"{i}. {row['dimensions']['city']}: "
                  f"{row['metrics']['sessions']} sessões")
    except Exception as e:
        print(f"✗ Erro: {e}")


def example_with_ordering():
    """Exemplo usando ordenação"""
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    client = GA4Client(property_id=property_id, credentials_path=credentials_path)

    print("\n" + "="*80)
    print("EXEMPLO 2: Ordenação")
    print("="*80)

    # Ordenar por número de usuários ativos (decrescente)
    request = RunReportRequest(
        property_id=property_id,
        date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
        dimensions=[Dimension(name='country')],
        metrics=[Metric(name='activeUsers')],
        order_bys=[
            OrderBy(metric_name='activeUsers', desc=True)
        ],
        limit=10
    )

    try:
        response = client.run_report(request)
        print(f"✓ Top 10 países por usuários ativos:")
        for i, row in enumerate(response['rows'], 1):
            print(f"{i}. {row['dimensions']['country']}: "
                  f"{row['metrics']['activeUsers']} usuários")
    except Exception as e:
        print(f"✗ Erro: {e}")


def example_multiple_date_ranges():
    """Exemplo com múltiplos intervalos de datas"""
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    client = GA4Client(property_id=property_id, credentials_path=credentials_path)

    print("\n" + "="*80)
    print("EXEMPLO 3: Múltiplos Intervalos de Datas")
    print("="*80)

    # Comparar última semana com semana anterior
    request = RunReportRequest(
        property_id=property_id,
        date_ranges=[
            DateRange(start_date='14daysAgo', end_date='8daysAgo', name='Semana Anterior'),
            DateRange(start_date='7daysAgo', end_date='today', name='Última Semana')
        ],
        dimensions=[Dimension(name='date')],
        metrics=[
            Metric(name='activeUsers'),
            Metric(name='sessions')
        ],
        limit=20
    )

    try:
        response = client.run_report(request)
        print(f"✓ Total de resultados: {response['row_count']}")
        print("Primeiras linhas:")
        for i, row in enumerate(response['rows'][:5], 1):
            print(f"{i}. Data: {row['dimensions']['date']}")
            print(f"   Usuários: {row['metrics']['activeUsers']}, "
                  f"Sessões: {row['metrics']['sessions']}")
    except Exception as e:
        print(f"✗ Erro: {e}")


def example_realtime_report():
    """Exemplo de relatório em tempo real"""
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    client = GA4Client(property_id=property_id, credentials_path=credentials_path)

    print("\n" + "="*80)
    print("EXEMPLO 4: Relatório em Tempo Real")
    print("="*80)

    try:
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

        print(f"✓ Usuários ativos agora: {response['row_count']} registros")
        for i, row in enumerate(response['rows'], 1):
            print(f"{i}. {row['dimensions']}: {row['metrics']}")
    except Exception as e:
        print(f"✗ Erro: {e}")


def example_batch_reports():
    """Exemplo de relatórios em lote"""
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    client = GA4Client(property_id=property_id, credentials_path=credentials_path)

    print("\n" + "="*80)
    print("EXEMPLO 5: Relatórios em Lote")
    print("="*80)

    # Criar múltiplas requisições
    requests = [
        # Relatório 1: Por país
        RunReportRequest(
            property_id=property_id,
            date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
            dimensions=[Dimension(name='country')],
            metrics=[Metric(name='activeUsers')],
            limit=5
        ),
        # Relatório 2: Por dispositivo
        RunReportRequest(
            property_id=property_id,
            date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
            dimensions=[Dimension(name='deviceCategory')],
            metrics=[Metric(name='sessions')],
            limit=5
        ),
        # Relatório 3: Por navegador
        RunReportRequest(
            property_id=property_id,
            date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
            dimensions=[Dimension(name='browser')],
            metrics=[Metric(name='screenPageViews')],
            limit=5
        )
    ]

    try:
        responses = client.batch_run_reports(requests)
        print(f"✓ {len(responses)} relatórios executados")

        for i, response in enumerate(responses, 1):
            print(f"\nRelatório {i}: {response['row_count']} linhas")
            print(f"Dimensões: {response['dimension_headers']}")
    except Exception as e:
        print(f"✗ Erro: {e}")


def example_get_metadata():
    """Exemplo de obtenção de metadados"""
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    client = GA4Client(property_id=property_id, credentials_path=credentials_path)

    print("\n" + "="*80)
    print("EXEMPLO 6: Metadados da Propriedade")
    print("="*80)

    try:
        metadata = client.get_metadata()

        print(f"\n✓ Dimensões disponíveis: {len(metadata['dimensions'])}")
        print("Primeiras 10 dimensões:")
        for i, dim in enumerate(metadata['dimensions'][:10], 1):
            print(f"{i}. {dim['api_name']}")
            print(f"   Nome: {dim['ui_name']}")
            print(f"   Categoria: {dim['category']}")

        print(f"\n✓ Métricas disponíveis: {len(metadata['metrics'])}")
        print("Primeiras 10 métricas:")
        for i, met in enumerate(metadata['metrics'][:10], 1):
            print(f"{i}. {met['api_name']}")
            print(f"   Nome: {met['ui_name']}")
            print(f"   Tipo: {met['type']}")
            print(f"   Categoria: {met['category']}")

        # Exportar metadados completos
        import json
        with open('metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Metadados completos exportados para metadata.json")

    except Exception as e:
        print(f"✗ Erro: {e}")


def example_advanced_filters():
    """Exemplo com filtros avançados (AND, OR, NOT)"""
    property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

    client = GA4Client(property_id=property_id, credentials_path=credentials_path)

    print("\n" + "="*80)
    print("EXEMPLO 7: Filtros Avançados (AND/OR/NOT)")
    print("="*80)

    # Filtrar países da América do Sul
    brazil = FilterExpression.string_filter('country', 'Brazil', 'EXACT')
    argentina = FilterExpression.string_filter('country', 'Argentina', 'EXACT')
    chile = FilterExpression.string_filter('country', 'Chile', 'EXACT')

    # Combinar com OR
    south_america_filter = FilterExpression.or_group([brazil, argentina, chile])

    request = RunReportRequest(
        property_id=property_id,
        date_ranges=[DateRange(start_date='30daysAgo', end_date='today')],
        dimensions=[Dimension(name='country'), Dimension(name='city')],
        metrics=[Metric(name='activeUsers'), Metric(name='sessions')],
        dimension_filter=south_america_filter,
        limit=10
    )

    try:
        response = client.run_report(request)
        print(f"✓ Resultados para América do Sul: {response['row_count']} linhas")
        for i, row in enumerate(response['rows'], 1):
            print(f"{i}. {row['dimensions']['country']} - {row['dimensions']['city']}: "
                  f"{row['metrics']['activeUsers']} usuários")
    except Exception as e:
        print(f"✗ Erro: {e}")


def main():
    """Executar todos os exemplos"""
    print("EXEMPLOS AVANÇADOS - Google Analytics 4 API")

    # Verificar se as credenciais estão configuradas
    if not os.getenv('GA4_PROPERTY_ID'):
        print("\n⚠ Configure as variáveis de ambiente:")
        print("  export GA4_PROPERTY_ID='seu-property-id'")
        print("  export GA4_CREDENTIALS_PATH='/path/to/credentials.json'")
        return

    try:
        example_with_filters()
        example_with_ordering()
        example_multiple_date_ranges()
        example_realtime_report()
        example_batch_reports()
        example_get_metadata()
        example_advanced_filters()

        print("\n" + "="*80)
        print("✓ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("="*80)

    except Exception as e:
        print(f"\n✗ Erro geral: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
