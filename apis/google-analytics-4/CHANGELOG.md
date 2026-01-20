# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-01-20

### Adicionado
- ✨ Implementação inicial da API wrapper do Google Analytics 4
- ✨ Classe `DateRange` para definir intervalos de datas
- ✨ Classe `Dimension` para configurar dimensões
- ✨ Classe `Metric` para configurar métricas
- ✨ Classe `RunReportRequest` para executar relatórios
- ✨ Classe `GA4Client` como cliente principal da API
- ✨ Classe `FilterExpression` para filtros avançados
- ✨ Classe `OrderBy` para ordenação de resultados
- ✨ Suporte a filtros de dimensões (string, numérico, in_list)
- ✨ Suporte a filtros de métricas
- ✨ Operadores lógicos para filtros (AND, OR, NOT)
- ✨ Relatórios em tempo real via `run_realtime_report()`
- ✨ Relatórios em lote via `batch_run_reports()`
- ✨ Obtenção de metadados via `get_metadata()`
- ✨ Exportação para JSON via `export_to_json()`
- ✨ Exportação para CSV via `export_to_csv()`
- 📚 Documentação completa em português
- 📚 README.md com exemplos e instruções
- 📚 QUICKSTART.md com guia de início rápido
- 🧪 Exemplo básico (`examples/basic_example.py`)
- 🧪 Exemplo avançado (`examples/advanced_example.py`)
- 🧪 Script de teste de instalação (`test_installation.py`)
- 📦 requirements.txt com todas as dependências
- 📦 setup.py para instalação via pip
- 🔧 .gitignore para proteção de credenciais
- 🔧 Configuração de exemplo (`examples/config.example.py`)

### Características
- 🚀 Execução totalmente local
- 🎯 API intuitiva e fácil de usar
- 📊 Suporte completo para DateRange, Dimension, Metric e RunReportRequest
- 🔍 Filtros e ordenação avançados
- ⏱️ Relatórios em tempo real
- 📦 Relatórios em lote
- 🔐 Suporte para autenticação via conta de serviço
- 📝 Type hints completos
- 🌍 Documentação em português

### Documentação
- Todos os métodos possuem docstrings detalhadas
- Exemplos de uso em cada classe
- Guia de início rápido
- Lista de dimensões e métricas comuns
- Instruções de configuração de credenciais

## [Unreleased]

### Planejado
- 🧪 Testes unitários completos
- 🧪 Testes de integração
- 📊 Suporte para visualizações com matplotlib/plotly
- 🔄 Cache de resultados
- 📈 Análises estatísticas avançadas
- 🔧 CLI para execução via linha de comando
- 🌐 Suporte para múltiplas propriedades
- 📱 Relatórios específicos para aplicativos mobile
- 🎨 Templates de relatórios pré-configurados

---

## Legendas

- ✨ Novos recursos
- 🐛 Correções de bugs
- 📚 Documentação
- 🧪 Testes
- 📦 Dependências
- 🔧 Configuração
- 🚀 Performance
- 🔐 Segurança
- 📊 Visualizações
- 🔄 Refatoração
