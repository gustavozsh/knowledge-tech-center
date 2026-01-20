"""
Cliente principal para interagir com a Google Analytics 4 Data API
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest as GARunReportRequest,
    RunRealtimeReportRequest,
    BatchRunReportsRequest,
    DateRange as GADateRange,
    Dimension as GADimension,
    Metric as GAMetric,
)
from google.oauth2 import service_account

from .models import DateRange, Dimension, Metric, RunReportRequest


class GoogleAnalytics4:
    """
    Cliente para interagir com o Google Analytics 4 Data API.

    Este cliente fornece métodos para executar relatórios e consultas
    no Google Analytics 4, incluindo suporte para relatórios em tempo real,
    relatórios em lote e consultas personalizadas.

    Attributes:
        property_id: ID da propriedade GA4
        credentials_path: Caminho para o arquivo de credenciais JSON
        client: Cliente da API do Google Analytics Data

    Examples:
        >>> # Inicializar com credenciais
        >>> client = GA4Client(
        ...     property_id='123456789',
        ...     credentials_path='path/to/credentials.json'
        ... )

        >>> # Criar uma requisição simples
        >>> request = RunReportRequest(
        ...     property_id='123456789',
        ...     date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
        ...     dimensions=[Dimension(name='country')],
        ...     metrics=[Metric(name='activeUsers')]
        ... )

        >>> # Executar o relatório
        >>> response = client.run_report(request)
        >>> print(response)
    """

    def __init__(
        self,
        property_id: str,
        credentials: Optional[service_account.Credentials] = None,
        credentials_path: Optional[str] = None,
        credentials_dict: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa o cliente GA4.

        Args:
            property_id: ID da propriedade GA4 (com ou sem o prefixo 'properties/')
            credentials: Objeto Credentials já criado (preferencial para Cloud Run)
            credentials_path: Caminho para o arquivo JSON de credenciais da conta de serviço
            credentials_dict: Dicionário com as credenciais (alternativa ao credentials_path)

        Raises:
            ValueError: Se nenhuma credencial for fornecida
            FileNotFoundError: Se o arquivo de credenciais não for encontrado

        Examples:
            >>> # Opção 1: Com objeto Credentials (Cloud Run)
            >>> from google.oauth2.service_account import Credentials
            >>> creds = Credentials.from_service_account_info(json_data)
            >>> client = GA4Client(property_id='123456789', credentials=creds)
            >>>
            >>> # Opção 2: Com arquivo
            >>> client = GA4Client(property_id='123456789', credentials_path='creds.json')
            >>>
            >>> # Opção 3: Com dicionário
            >>> client = GA4Client(property_id='123456789', credentials_dict=json_data)
        """
        if not property_id.startswith('properties/'):
            self.property_id = f'properties/{property_id}'
        else:
            self.property_id = property_id

        # Carregar credenciais
        if credentials:
            # Usar credenciais já fornecidas (caso do Cloud Run)
            creds = credentials
        elif credentials_path:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")

            creds = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
        elif credentials_dict:
            creds = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
        else:
            # Tentar usar Application Default Credentials
            creds = None  # O client tentará usar ADC

        # Inicializar o cliente
        if creds:
            self.client = BetaAnalyticsDataClient(credentials=creds)
        else:
            self.client = BetaAnalyticsDataClient()

    def run_report(self, request: RunReportRequest) -> Dict[str, Any]:
        """
        Executa um relatório no GA4.

        Args:
            request: Objeto RunReportRequest com os parâmetros da consulta

        Returns:
            Dicionário com os resultados do relatório processados

        Examples:
            >>> request = RunReportRequest(
            ...     property_id='123456789',
            ...     date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
            ...     dimensions=[Dimension(name='country')],
            ...     metrics=[Metric(name='activeUsers')]
            ... )
            >>> response = client.run_report(request)
        """
        # Converter nosso request para o formato da API do Google
        ga_request = self._convert_to_ga_request(request)

        # Executar o relatório
        response = self.client.run_report(ga_request)

        # Processar e retornar a resposta
        return self._process_response(response)

    def run_report_raw(self, request: RunReportRequest):
        """
        Executa um relatório e retorna a resposta raw da API do Google.

        Args:
            request: Objeto RunReportRequest com os parâmetros da consulta

        Returns:
            Resposta raw da API do Google Analytics
        """
        ga_request = self._convert_to_ga_request(request)
        return self.client.run_report(ga_request)

    def run_realtime_report(self, dimensions: List[Dimension],
                           metrics: List[Metric],
                           dimension_filter: Optional[Dict[str, Any]] = None,
                           metric_filter: Optional[Dict[str, Any]] = None,
                           limit: int = 10000) -> Dict[str, Any]:
        """
        Executa um relatório em tempo real no GA4.

        Args:
            dimensions: Lista de dimensões
            metrics: Lista de métricas
            dimension_filter: Filtro opcional para dimensões
            metric_filter: Filtro opcional para métricas
            limit: Limite de resultados

        Returns:
            Dicionário com os resultados do relatório processados
        """
        request = RunRealtimeReportRequest(
            property=self.property_id,
            dimensions=[GADimension(name=d.name) for d in dimensions],
            metrics=[GAMetric(name=m.name) for m in metrics],
            limit=limit
        )

        if dimension_filter:
            request.dimension_filter = dimension_filter

        if metric_filter:
            request.metric_filter = metric_filter

        response = self.client.run_realtime_report(request)
        return self._process_response(response)

    def batch_run_reports(self, requests: List[RunReportRequest]) -> List[Dict[str, Any]]:
        """
        Executa múltiplos relatórios em uma única chamada de API.

        Args:
            requests: Lista de objetos RunReportRequest

        Returns:
            Lista de dicionários com os resultados de cada relatório
        """
        ga_requests = [self._convert_to_ga_request(req) for req in requests]

        batch_request = BatchRunReportsRequest(
            property=self.property_id,
            requests=ga_requests
        )

        response = self.client.batch_run_reports(batch_request)

        return [self._process_response(report) for report in response.reports]

    def get_metadata(self) -> Dict[str, Any]:
        """
        Obtém os metadados da propriedade (dimensões e métricas disponíveis).

        Returns:
            Dicionário com as dimensões e métricas disponíveis
        """
        from google.analytics.data_v1beta.types import GetMetadataRequest

        request = GetMetadataRequest(name=f"{self.property_id}/metadata")
        response = self.client.get_metadata(request)

        return {
            'dimensions': [
                {
                    'api_name': dim.api_name,
                    'ui_name': dim.ui_name,
                    'description': dim.description,
                    'category': dim.category
                }
                for dim in response.dimensions
            ],
            'metrics': [
                {
                    'api_name': met.api_name,
                    'ui_name': met.ui_name,
                    'description': met.description,
                    'category': met.category,
                    'type': met.type_.name
                }
                for met in response.metrics
            ]
        }

    def _convert_to_ga_request(self, request: RunReportRequest) -> GARunReportRequest:
        """
        Converte nosso RunReportRequest para o formato da API do Google.

        Args:
            request: Nosso objeto RunReportRequest

        Returns:
            GARunReportRequest do Google
        """
        ga_request = GARunReportRequest(
            property=self.property_id,
            date_ranges=[
                GADateRange(
                    start_date=dr.start_date,
                    end_date=dr.end_date,
                    name=dr.name
                )
                for dr in request.date_ranges
            ],
            dimensions=[GADimension(name=d.name) for d in request.dimensions],
            metrics=[GAMetric(name=m.name) for m in request.metrics],
            offset=request.offset,
            limit=request.limit,
            keep_empty_rows=request.keep_empty_rows,
            return_property_quota=request.return_property_quota
        )

        if request.dimension_filter:
            ga_request.dimension_filter = request.dimension_filter

        if request.metric_filter:
            ga_request.metric_filter = request.metric_filter

        if request.order_bys:
            from google.analytics.data_v1beta.types import OrderBy
            order_bys = []
            for order_by in request.order_bys:
                ob_dict = order_by.to_dict()
                order_bys.append(ob_dict)
            ga_request.order_bys = order_bys

        return ga_request

    def _process_response(self, response) -> Dict[str, Any]:
        """
        Processa a resposta da API do Google em um formato mais amigável.

        Args:
            response: Resposta raw da API

        Returns:
            Dicionário processado com os dados
        """
        result = {
            'dimension_headers': [],
            'metric_headers': [],
            'rows': [],
            'row_count': response.row_count,
            'metadata': {}
        }

        # Processar headers de dimensões
        if hasattr(response, 'dimension_headers'):
            result['dimension_headers'] = [
                header.name for header in response.dimension_headers
            ]

        # Processar headers de métricas
        if hasattr(response, 'metric_headers'):
            result['metric_headers'] = [
                {
                    'name': header.name,
                    'type': header.type_.name
                }
                for header in response.metric_headers
            ]

        # Processar linhas de dados
        for row in response.rows:
            row_data = {
                'dimensions': {},
                'metrics': {}
            }

            # Dimensões
            for i, dimension_value in enumerate(row.dimension_values):
                dim_name = result['dimension_headers'][i]
                row_data['dimensions'][dim_name] = dimension_value.value

            # Métricas
            for i, metric_value in enumerate(row.metric_values):
                met_name = result['metric_headers'][i]['name']
                row_data['metrics'][met_name] = metric_value.value

            result['rows'].append(row_data)

        # Adicionar metadados se disponíveis
        if hasattr(response, 'metadata'):
            result['metadata'] = {
                'currency_code': response.metadata.currency_code if hasattr(response.metadata, 'currency_code') else None,
                'time_zone': response.metadata.time_zone if hasattr(response.metadata, 'time_zone') else None,
            }

        # Adicionar informações de quota se solicitado
        if hasattr(response, 'property_quota'):
            result['property_quota'] = {
                'tokens_per_day': {
                    'consumed': response.property_quota.tokens_per_day.consumed if hasattr(response.property_quota.tokens_per_day, 'consumed') else 0,
                    'remaining': response.property_quota.tokens_per_day.remaining if hasattr(response.property_quota.tokens_per_day, 'remaining') else 0
                },
                'tokens_per_hour': {
                    'consumed': response.property_quota.tokens_per_hour.consumed if hasattr(response.property_quota.tokens_per_hour, 'consumed') else 0,
                    'remaining': response.property_quota.tokens_per_hour.remaining if hasattr(response.property_quota.tokens_per_hour, 'remaining') else 0
                }
            }

        return result

    def export_to_json(self, response: Dict[str, Any], file_path: str):
        """
        Exporta a resposta para um arquivo JSON.

        Args:
            response: Resposta processada do relatório
            file_path: Caminho para salvar o arquivo JSON
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=2)

    def export_to_csv(self, response: Dict[str, Any], file_path: str):
        """
        Exporta a resposta para um arquivo CSV.

        Args:
            response: Resposta processada do relatório
            file_path: Caminho para salvar o arquivo CSV
        """
        import csv

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if not response['rows']:
                return

            # Criar headers
            fieldnames = []
            fieldnames.extend(response['dimension_headers'])
            fieldnames.extend([m['name'] for m in response['metric_headers']])

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Escrever dados
            for row in response['rows']:
                row_dict = {}
                row_dict.update(row['dimensions'])
                row_dict.update(row['metrics'])
                writer.writerow(row_dict)

    def __repr__(self) -> str:
        return f"GoogleAnalytics4(property_id='{self.property_id}')"


# Alias para compatibilidade
GA4Client = GoogleAnalytics4
