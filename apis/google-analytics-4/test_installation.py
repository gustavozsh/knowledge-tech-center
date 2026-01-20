"""
Script para testar a instalação da API do Google Analytics 4

Execute este script para verificar se tudo está configurado corretamente.
"""

import sys
import os


def check_python_version():
    """Verifica a versão do Python"""
    print("="*80)
    print("1. Verificando versão do Python...")
    print("="*80)

    version = sys.version_info
    print(f"Versão: Python {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("✓ Versão do Python OK (>= 3.8)")
        return True
    else:
        print("✗ Python 3.8 ou superior é necessário")
        return False


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("\n" + "="*80)
    print("2. Verificando dependências...")
    print("="*80)

    dependencies = [
        'google.analytics.data_v1beta',
        'google.auth',
        'google.oauth2',
    ]

    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} instalado")
        except ImportError:
            print(f"✗ {dep} NÃO instalado")
            all_ok = False

    if not all_ok:
        print("\nInstale as dependências com:")
        print("  pip install -r requirements.txt")

    return all_ok


def check_modules():
    """Verifica se os módulos locais estão acessíveis"""
    print("\n" + "="*80)
    print("3. Verificando módulos locais...")
    print("="*80)

    # Adicionar src ao path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    modules = ['models', 'ga4_client']
    all_ok = True

    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py encontrado")
        except ImportError as e:
            print(f"✗ {module}.py NÃO encontrado: {e}")
            all_ok = False

    return all_ok


def check_environment():
    """Verifica as variáveis de ambiente"""
    print("\n" + "="*80)
    print("4. Verificando variáveis de ambiente...")
    print("="*80)

    property_id = os.getenv('GA4_PROPERTY_ID')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH')

    if property_id:
        print(f"✓ GA4_PROPERTY_ID configurado: {property_id}")
    else:
        print("✗ GA4_PROPERTY_ID não configurado")

    if credentials_path:
        print(f"✓ GA4_CREDENTIALS_PATH configurado: {credentials_path}")

        # Verificar se o arquivo existe
        if os.path.exists(credentials_path):
            print(f"✓ Arquivo de credenciais encontrado")
        else:
            print(f"✗ Arquivo de credenciais NÃO encontrado: {credentials_path}")
            return False
    else:
        print("⚠ GA4_CREDENTIALS_PATH não configurado")
        print("  Tentando usar 'credentials.json' no diretório atual...")

        if os.path.exists('credentials.json'):
            print("✓ credentials.json encontrado")
        else:
            print("✗ credentials.json NÃO encontrado")
            return False

    return bool(property_id)


def test_import_models():
    """Testa importação dos modelos"""
    print("\n" + "="*80)
    print("5. Testando importação dos modelos...")
    print("="*80)

    try:
        from models import DateRange, Dimension, Metric, RunReportRequest

        # Testar criação de objetos
        date_range = DateRange(start_date='7daysAgo', end_date='today')
        print(f"✓ DateRange criado: {date_range}")

        dimension = Dimension(name='country')
        print(f"✓ Dimension criado: {dimension}")

        metric = Metric(name='activeUsers')
        print(f"✓ Metric criado: {metric}")

        request = RunReportRequest(
            property_id='123456789',
            date_ranges=[date_range],
            dimensions=[dimension],
            metrics=[metric]
        )
        print(f"✓ RunReportRequest criado: {request}")

        return True

    except Exception as e:
        print(f"✗ Erro ao importar/criar modelos: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_client_init():
    """Testa inicialização do cliente"""
    print("\n" + "="*80)
    print("6. Testando inicialização do cliente...")
    print("="*80)

    try:
        from ga4_client import GA4Client

        property_id = os.getenv('GA4_PROPERTY_ID', '123456789')
        credentials_path = os.getenv('GA4_CREDENTIALS_PATH', 'credentials.json')

        if not os.path.exists(credentials_path):
            print("⚠ Pulando teste - credenciais não encontradas")
            return True

        client = GA4Client(
            property_id=property_id,
            credentials_path=credentials_path
        )

        print(f"✓ Cliente criado: {client}")
        return True

    except FileNotFoundError:
        print("⚠ Arquivo de credenciais não encontrado (esperado para este teste)")
        return True
    except Exception as e:
        print(f"✗ Erro ao criar cliente: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "🔍 TESTE DE INSTALAÇÃO - Google Analytics 4 API Wrapper\n")

    tests = [
        check_python_version,
        check_dependencies,
        check_modules,
        check_environment,
        test_import_models,
        test_client_init,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Resumo
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)

    passed = sum(results)
    total = len(results)

    print(f"\nTestes passados: {passed}/{total}")

    if all(results):
        print("\n🎉 Tudo OK! Você está pronto para usar a API.")
        print("\nPróximos passos:")
        print("  1. Configure as variáveis de ambiente (se ainda não fez)")
        print("  2. Execute: cd examples && python basic_example.py")
    else:
        print("\n⚠ Alguns testes falharam. Revise as mensagens acima.")
        print("\nDicas:")
        print("  1. Instale as dependências: pip install -r requirements.txt")
        print("  2. Configure as variáveis de ambiente")
        print("  3. Verifique o arquivo de credenciais")
        print("  4. Consulte o QUICKSTART.md para ajuda")

    return all(results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
