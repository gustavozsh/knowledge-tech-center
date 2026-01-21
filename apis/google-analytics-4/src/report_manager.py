"""
Gerenciador de Relatórios do Google Analytics 4

Este módulo é responsável por gerenciar a execução de relatórios
organizados por categoria (dimensões e métricas) e salvá-los no BigQuery.

Versão Python: 3.11+
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from google.oauth2.service_account import Credentials
from google.cloud import bigquery

from .ga4_client import GoogleAnalytics4
from .models import DateRange, Dimension, Metric, RunReportRequest
from .bigquery_writer import BigQueryWriter

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuração de um relatório"""
    table_name: str
    description: str
    dimensions: List[str]
    metrics: List[str]
    date_dimension: bool = True  # Se deve incluir a dimensão 'date'


class ReportManager:
    """
    Gerenciador de relatórios do Google Analytics 4.
    
    Esta classe coordena a execução de múltiplos relatórios organizados
    por categoria e salva os resultados no BigQuery.
    
    Attributes:
        ga4_client: Cliente do Google Analytics 4
        bq_writer: Writer do BigQuery
        property_id: ID da propriedade GA4
        
    Examples:
        >>> manager = ReportManager(
        ...     credentials=creds,
        ...     property_id="123456789",
        ...     project_id="my-project"
        ... )
        >>> manager.run_dimension_report("TB_001_GA4_DIM_USUARIO")
    """
    
    # Configurações de relatórios de dimensões
    DIMENSION_REPORTS = {
        "TB_001_GA4_DIM_USUARIO": ReportConfig(
            table_name="TB_001_GA4_DIM_USUARIO",
            description="Dimensões de usuário",
            dimensions=["newVsReturning", "userAgeBracket", "userGender"],
            metrics=["activeUsers", "newUsers", "totalUsers", "sessions"]
        ),
        "TB_002_GA4_DIM_GEOGRAFICA": ReportConfig(
            table_name="TB_002_GA4_DIM_GEOGRAFICA",
            description="Dimensões geográficas",
            dimensions=["city", "cityId", "country", "countryId", "region", "continent", "continentId"],
            metrics=["activeUsers", "sessions", "screenPageViews", "newUsers"]
        ),
        "TB_003_GA4_DIM_DISPOSITIVO": ReportConfig(
            table_name="TB_003_GA4_DIM_DISPOSITIVO",
            description="Dimensões de dispositivo/tecnologia",
            dimensions=["browser", "deviceCategory", "operatingSystem", "operatingSystemVersion", "platform", "screenResolution"],
            metrics=["activeUsers", "sessions", "screenPageViews", "bounceRate"]
        ),
        "TB_004_GA4_DIM_AQUISICAO": ReportConfig(
            table_name="TB_004_GA4_DIM_AQUISICAO",
            description="Dimensões de aquisição/campanha",
            dimensions=["source", "medium", "sourceMedium", "campaignId", "campaignName", "defaultChannelGroup"],
            metrics=["activeUsers", "sessions", "newUsers", "conversions", "totalRevenue"]
        ),
        "TB_005_GA4_DIM_PAGINA": ReportConfig(
            table_name="TB_005_GA4_DIM_PAGINA",
            description="Dimensões de página/conteúdo",
            dimensions=["pagePath", "pageTitle", "landingPage", "hostName"],
            metrics=["activeUsers", "sessions", "screenPageViews", "averageSessionDuration", "bounceRate"]
        ),
        "TB_006_GA4_DIM_EVENTO": ReportConfig(
            table_name="TB_006_GA4_DIM_EVENTO",
            description="Dimensões de evento",
            dimensions=["eventName", "isConversionEvent"],
            metrics=["eventCount", "eventCountPerUser", "conversions", "eventValue", "activeUsers"]
        ),
        "TB_007_GA4_DIM_PUBLICO": ReportConfig(
            table_name="TB_007_GA4_DIM_PUBLICO",
            description="Dimensões de público-alvo",
            dimensions=["audienceId", "audienceName"],
            metrics=["activeUsers", "totalUsers", "newUsers", "sessions"]
        )
    }
    
    # Configurações de relatórios de métricas
    METRIC_REPORTS = {
        "TB_008_GA4_MET_USUARIOS": ReportConfig(
            table_name="TB_008_GA4_MET_USUARIOS",
            description="Métricas de usuários",
            dimensions=[],  # Apenas date será adicionado
            metrics=["activeUsers", "newUsers", "totalUsers", "active1DayUsers", "active7DayUsers", "active28DayUsers", "dauPerMau", "dauPerWau", "wauPerMau"]
        ),
        "TB_009_GA4_MET_SESSAO": ReportConfig(
            table_name="TB_009_GA4_MET_SESSAO",
            description="Métricas de sessão",
            dimensions=[],
            metrics=["sessions", "sessionsPerUser", "averageSessionDuration", "bounceRate", "engagedSessions", "engagementRate", "userEngagementDuration"]
        ),
        "TB_010_GA4_MET_EVENTOS": ReportConfig(
            table_name="TB_010_GA4_MET_EVENTOS",
            description="Métricas de eventos",
            dimensions=[],
            metrics=["eventCount", "eventCountPerUser", "eventsPerSession", "conversions", "eventValue"]
        ),
        "TB_011_GA4_MET_VISUALIZACAO": ReportConfig(
            table_name="TB_011_GA4_MET_VISUALIZACAO",
            description="Métricas de visualização",
            dimensions=[],
            metrics=["screenPageViews", "screenPageViewsPerSession", "screenPageViewsPerUser"]
        ),
        "TB_012_GA4_MET_ECOMMERCE": ReportConfig(
            table_name="TB_012_GA4_MET_ECOMMERCE",
            description="Métricas de e-commerce",
            dimensions=[],
            metrics=["totalRevenue", "purchaseRevenue", "transactions", "ecommercePurchases", "averagePurchaseRevenue", "averageRevenuePerUser", "addToCarts", "checkouts", "cartToViewRate", "purchaseToViewRate"]
        )
    }
    
    def __init__(
        self,
        credentials: Credentials,
        property_id: str,
        project_id: str,
        dataset_id: str = "RAW"
    ):
        """
        Inicializa o gerenciador de relatórios.
        
        Args:
            credentials: Credenciais de autenticação
            property_id: ID da propriedade GA4
            project_id: ID do projeto GCP
            dataset_id: ID do dataset no BigQuery
        """
        self.credentials = credentials
        self.property_id = property_id
        self.project_id = project_id
        self.dataset_id = dataset_id
        
        # Inicializar clientes
        self.ga4_client = GoogleAnalytics4(
            property_id=property_id,
            credentials=credentials
        )
        
        self.bq_writer = BigQueryWriter(
            project_id=project_id,
            dataset_id=dataset_id,
            credentials=credentials
        )
        
        logger.info(f"ReportManager inicializado para property {property_id}")
    
    def _get_yesterday_date(self) -> str:
        """Retorna a data de ontem no formato YYYY-MM-DD"""
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")
    
    def _create_report_request(
        self,
        config: ReportConfig,
        start_date: str = "yesterday",
        end_date: str = "yesterday",
        limit: int = 100000
    ) -> RunReportRequest:
        """
        Cria uma requisição de relatório baseada na configuração.
        
        Args:
            config: Configuração do relatório
            start_date: Data inicial
            end_date: Data final
            limit: Limite de linhas
            
        Returns:
            RunReportRequest configurado
        """
        # Preparar dimensões (sempre incluir date para rastreabilidade)
        dimensions = [Dimension(name="date")]
        
        for dim_name in config.dimensions:
            dimensions.append(Dimension(name=dim_name))
        
        # Preparar métricas
        metrics = [Metric(name=met_name) for met_name in config.metrics]
        
        # Criar date range
        date_ranges = [DateRange(start_date=start_date, end_date=end_date)]
        
        return RunReportRequest(
            property_id=self.property_id,
            date_ranges=date_ranges,
            dimensions=dimensions,
            metrics=metrics,
            limit=limit
        )
    
    def _get_schema_for_report(self, config: ReportConfig) -> List[bigquery.SchemaField]:
        """
        Gera o schema do BigQuery para um relatório específico.
        
        Args:
            config: Configuração do relatório
            
        Returns:
            Lista de SchemaFields
        """
        schema = [
            bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("property_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("report_date", "DATE", mode="REQUIRED"),
        ]
        
        # Adicionar campos de dimensões
        for dim in config.dimensions:
            # Campos de ID são INTEGER, outros são STRING
            if dim.endswith("Id") and dim not in ["campaignId", "sessionCampaignId", "firstUserCampaignId"]:
                schema.append(bigquery.SchemaField(dim, "STRING", mode="NULLABLE"))
            else:
                schema.append(bigquery.SchemaField(dim, "STRING", mode="NULLABLE"))
        
        # Adicionar campos de métricas
        for met in config.metrics:
            # Métricas de taxa são FLOAT, contagens são INTEGER
            if any(keyword in met.lower() for keyword in ["rate", "per", "average", "duration"]):
                schema.append(bigquery.SchemaField(met, "FLOAT64", mode="NULLABLE"))
            elif any(keyword in met.lower() for keyword in ["revenue", "amount", "value"]):
                schema.append(bigquery.SchemaField(met, "FLOAT64", mode="NULLABLE"))
            else:
                schema.append(bigquery.SchemaField(met, "INT64", mode="NULLABLE"))
        
        return schema
    
    def _prepare_rows_for_bigquery(
        self,
        response: Dict[str, Any],
        config: ReportConfig
    ) -> List[Dict[str, Any]]:
        """
        Prepara as linhas do relatório para inserção no BigQuery.
        
        Args:
            response: Resposta processada do GA4
            config: Configuração do relatório
            
        Returns:
            Lista de dicionários prontos para inserção
        """
        rows = []
        ingestion_timestamp = datetime.utcnow().isoformat()
        
        for row_data in response.get('rows', []):
            row = {
                "ingestion_timestamp": ingestion_timestamp,
                "property_id": self.property_id.replace("properties/", "")
            }
            
            # Extrair data do relatório
            dimensions = row_data.get('dimensions', {})
            if 'date' in dimensions:
                date_str = dimensions['date']
                try:
                    row['report_date'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                except Exception:
                    row['report_date'] = None
            else:
                row['report_date'] = self._get_yesterday_date()
            
            # Adicionar dimensões
            for dim in config.dimensions:
                row[dim] = dimensions.get(dim)
            
            # Adicionar métricas
            metrics = row_data.get('metrics', {})
            for met in config.metrics:
                value = metrics.get(met)
                if value is not None:
                    try:
                        # Tentar converter para número
                        if '.' in str(value):
                            row[met] = float(value)
                        else:
                            row[met] = int(value)
                    except (ValueError, TypeError):
                        row[met] = value
                else:
                    row[met] = None
            
            rows.append(row)
        
        return rows
    
    def run_dimension_report(
        self,
        table_name: str,
        start_date: str = "yesterday",
        end_date: str = "yesterday",
        auto_create_table: bool = True
    ) -> Dict[str, Any]:
        """
        Executa um relatório de dimensão específico e salva no BigQuery.
        
        Args:
            table_name: Nome da tabela (ex: TB_001_GA4_DIM_USUARIO)
            start_date: Data inicial
            end_date: Data final
            auto_create_table: Se deve criar a tabela automaticamente
            
        Returns:
            Dicionário com status e informações do processamento
        """
        if table_name not in self.DIMENSION_REPORTS:
            raise ValueError(f"Tabela de dimensão não encontrada: {table_name}")
        
        config = self.DIMENSION_REPORTS[table_name]
        logger.info(f"Executando relatório de dimensão: {table_name}")
        
        try:
            # Criar requisição
            request = self._create_report_request(config, start_date, end_date)
            
            # Executar relatório
            response = self.ga4_client.run_report(request)
            logger.info(f"Relatório executado: {response['row_count']} linhas")
            
            # Preparar dados para BigQuery
            rows = self._prepare_rows_for_bigquery(response, config)
            
            if not rows:
                logger.warning(f"Nenhum dado retornado para {table_name}")
                return {
                    "status": "success",
                    "message": "Nenhum dado retornado",
                    "rows_processed": 0,
                    "table": table_name
                }
            
            # Criar tabela se necessário
            if auto_create_table:
                self.bq_writer.ensure_dataset_exists()
                schema = self._get_schema_for_report(config)
                self._create_table_with_schema(table_name, schema)
            
            # Inserir dados
            table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
            errors = self.bq_writer.client.insert_rows_json(table_ref, rows)
            
            if errors:
                logger.error(f"Erros ao inserir dados: {errors}")
                raise Exception(f"Falha ao inserir dados: {errors}")
            
            logger.info(f"✓ {len(rows)} linhas inseridas em {table_name}")
            
            return {
                "status": "success",
                "message": f"Relatório processado e salvo",
                "rows_processed": len(rows),
                "table": f"{self.project_id}.{self.dataset_id}.{table_name}",
                "dimensions": config.dimensions,
                "metrics": config.metrics
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar relatório {table_name}: {str(e)}")
            raise
    
    def run_metric_report(
        self,
        table_name: str,
        start_date: str = "yesterday",
        end_date: str = "yesterday",
        auto_create_table: bool = True
    ) -> Dict[str, Any]:
        """
        Executa um relatório de métrica específico e salva no BigQuery.
        
        Args:
            table_name: Nome da tabela (ex: TB_008_GA4_MET_USUARIOS)
            start_date: Data inicial
            end_date: Data final
            auto_create_table: Se deve criar a tabela automaticamente
            
        Returns:
            Dicionário com status e informações do processamento
        """
        if table_name not in self.METRIC_REPORTS:
            raise ValueError(f"Tabela de métrica não encontrada: {table_name}")
        
        config = self.METRIC_REPORTS[table_name]
        logger.info(f"Executando relatório de métrica: {table_name}")
        
        try:
            # Criar requisição
            request = self._create_report_request(config, start_date, end_date)
            
            # Executar relatório
            response = self.ga4_client.run_report(request)
            logger.info(f"Relatório executado: {response['row_count']} linhas")
            
            # Preparar dados para BigQuery
            rows = self._prepare_rows_for_bigquery(response, config)
            
            if not rows:
                logger.warning(f"Nenhum dado retornado para {table_name}")
                return {
                    "status": "success",
                    "message": "Nenhum dado retornado",
                    "rows_processed": 0,
                    "table": table_name
                }
            
            # Criar tabela se necessário
            if auto_create_table:
                self.bq_writer.ensure_dataset_exists()
                schema = self._get_schema_for_report(config)
                self._create_table_with_schema(table_name, schema)
            
            # Inserir dados
            table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
            errors = self.bq_writer.client.insert_rows_json(table_ref, rows)
            
            if errors:
                logger.error(f"Erros ao inserir dados: {errors}")
                raise Exception(f"Falha ao inserir dados: {errors}")
            
            logger.info(f"✓ {len(rows)} linhas inseridas em {table_name}")
            
            return {
                "status": "success",
                "message": f"Relatório processado e salvo",
                "rows_processed": len(rows),
                "table": f"{self.project_id}.{self.dataset_id}.{table_name}",
                "metrics": config.metrics
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar relatório {table_name}: {str(e)}")
            raise
    
    def _create_table_with_schema(
        self,
        table_name: str,
        schema: List[bigquery.SchemaField]
    ) -> None:
        """
        Cria uma tabela com schema específico se não existir.
        
        Args:
            table_name: Nome da tabela
            schema: Schema da tabela
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            self.bq_writer.client.get_table(table_ref)
            logger.info(f"Tabela {table_ref} já existe")
        except Exception:
            # Tabela não existe, criar
            table = bigquery.Table(table_ref, schema=schema)
            
            # Configurar particionamento por data
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="report_date"
            )
            
            table = self.bq_writer.client.create_table(table)
            logger.info(f"Tabela {table_ref} criada com sucesso")
    
    def run_all_dimension_reports(
        self,
        start_date: str = "yesterday",
        end_date: str = "yesterday"
    ) -> Dict[str, Any]:
        """
        Executa todos os relatórios de dimensão.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dicionário com resultados de todos os relatórios
        """
        results = {}
        
        for table_name in self.DIMENSION_REPORTS.keys():
            try:
                result = self.run_dimension_report(table_name, start_date, end_date)
                results[table_name] = result
            except Exception as e:
                results[table_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def run_all_metric_reports(
        self,
        start_date: str = "yesterday",
        end_date: str = "yesterday"
    ) -> Dict[str, Any]:
        """
        Executa todos os relatórios de métrica.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dicionário com resultados de todos os relatórios
        """
        results = {}
        
        for table_name in self.METRIC_REPORTS.keys():
            try:
                result = self.run_metric_report(table_name, start_date, end_date)
                results[table_name] = result
            except Exception as e:
                results[table_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def run_all_reports(
        self,
        start_date: str = "yesterday",
        end_date: str = "yesterday"
    ) -> Dict[str, Any]:
        """
        Executa todos os relatórios (dimensões e métricas).
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dicionário com resultados de todos os relatórios
        """
        logger.info(f"Iniciando execução de todos os relatórios para {start_date} a {end_date}")
        
        results = {
            "dimensions": self.run_all_dimension_reports(start_date, end_date),
            "metrics": self.run_all_metric_reports(start_date, end_date)
        }
        
        # Calcular estatísticas
        total_success = 0
        total_error = 0
        total_rows = 0
        
        for category in ["dimensions", "metrics"]:
            for table_name, result in results[category].items():
                if result.get("status") == "success":
                    total_success += 1
                    total_rows += result.get("rows_processed", 0)
                else:
                    total_error += 1
        
        results["summary"] = {
            "total_reports": total_success + total_error,
            "successful": total_success,
            "failed": total_error,
            "total_rows_processed": total_rows,
            "execution_date": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Execução concluída: {total_success} sucesso, {total_error} falhas, {total_rows} linhas")
        
        return results
    
    @classmethod
    def get_available_reports(cls) -> Dict[str, List[str]]:
        """
        Retorna lista de relatórios disponíveis.
        
        Returns:
            Dicionário com listas de relatórios por categoria
        """
        return {
            "dimension_reports": list(cls.DIMENSION_REPORTS.keys()),
            "metric_reports": list(cls.METRIC_REPORTS.keys())
        }
