"""
Models for Google Analytics 4 API
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class DateRange:
    """
    Representa um intervalo de datas para consulta no GA4.

    Attributes:
        start_date: Data inicial no formato 'YYYY-MM-DD' ou valores especiais
                   como 'today', 'yesterday', 'NdaysAgo' (ex: '7daysAgo')
        end_date: Data final no formato 'YYYY-MM-DD' ou valores especiais
        name: Nome opcional para identificar o intervalo de datas

    Examples:
        >>> date_range = DateRange(start_date='7daysAgo', end_date='today')
        >>> date_range = DateRange(start_date='2024-01-01', end_date='2024-01-31', name='Janeiro')
    """
    start_date: str
    end_date: str
    name: Optional[str] = None

    def __post_init__(self):
        """Valida as datas fornecidas"""
        if not self.start_date or not self.end_date:
            raise ValueError("start_date e end_date são obrigatórios")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário no formato esperado pela API"""
        result = {
            "startDate": self.start_date,
            "endDate": self.end_date
        }
        if self.name:
            result["name"] = self.name
        return result

    def __str__(self) -> str:
        return f"DateRange({self.start_date} to {self.end_date})"


@dataclass
class Dimension:
    """
    Representa uma dimensão no GA4.

    Attributes:
        name: Nome da dimensão (ex: 'country', 'city', 'date', 'pagePath', etc.)
        dimension_expression: Expressão opcional para dimensões calculadas

    Examples:
        >>> dimension = Dimension(name='country')
        >>> dimension = Dimension(name='city')
        >>> dimension = Dimension(name='date')

    Dimensões comuns:
        - country: País
        - city: Cidade
        - date: Data
        - pagePath: Caminho da página
        - pageTitle: Título da página
        - sessionSource: Fonte da sessão
        - sessionMedium: Meio da sessão
        - deviceCategory: Categoria do dispositivo (desktop, mobile, tablet)
        - browser: Navegador
        - operatingSystem: Sistema operacional
        - eventName: Nome do evento
    """
    name: str
    dimension_expression: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Valida a dimensão"""
        if not self.name:
            raise ValueError("name é obrigatório para Dimension")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário no formato esperado pela API"""
        result = {"name": self.name}
        if self.dimension_expression:
            result["dimensionExpression"] = self.dimension_expression
        return result

    def __str__(self) -> str:
        return f"Dimension({self.name})"


@dataclass
class Metric:
    """
    Representa uma métrica no GA4.

    Attributes:
        name: Nome da métrica (ex: 'activeUsers', 'sessions', 'screenPageViews', etc.)
        expression: Expressão opcional para métricas calculadas
        invisible: Se True, a métrica não será retornada na resposta

    Examples:
        >>> metric = Metric(name='activeUsers')
        >>> metric = Metric(name='sessions')
        >>> metric = Metric(name='screenPageViews')

    Métricas comuns:
        - activeUsers: Usuários ativos
        - newUsers: Novos usuários
        - sessions: Sessões
        - screenPageViews: Visualizações de página/tela
        - eventCount: Contagem de eventos
        - conversions: Conversões
        - totalRevenue: Receita total
        - averageSessionDuration: Duração média da sessão
        - bounceRate: Taxa de rejeição
        - engagementRate: Taxa de engajamento
        - sessionsPerUser: Sessões por usuário
    """
    name: str
    expression: Optional[str] = None
    invisible: bool = False

    def __post_init__(self):
        """Valida a métrica"""
        if not self.name:
            raise ValueError("name é obrigatório para Metric")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário no formato esperado pela API"""
        result = {"name": self.name}
        if self.expression:
            result["expression"] = self.expression
        if self.invisible:
            result["invisible"] = self.invisible
        return result

    def __str__(self) -> str:
        return f"Metric({self.name})"


@dataclass
class OrderBy:
    """
    Define a ordenação dos resultados.

    Attributes:
        desc: Se True, ordena em ordem decrescente
        dimension_name: Nome da dimensão para ordenar
        metric_name: Nome da métrica para ordenar
    """
    desc: bool = False
    dimension_name: Optional[str] = None
    metric_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário no formato esperado pela API"""
        result = {"desc": self.desc}

        if self.dimension_name:
            result["dimension"] = {"dimensionName": self.dimension_name}
        elif self.metric_name:
            result["metric"] = {"metricName": self.metric_name}
        else:
            raise ValueError("Deve especificar dimension_name ou metric_name")

        return result


@dataclass
class RunReportRequest:
    """
    Representa uma requisição completa para executar um relatório no GA4.

    Attributes:
        property_id: ID da propriedade GA4 (formato: 'properties/123456789')
        date_ranges: Lista de intervalos de datas
        dimensions: Lista de dimensões
        metrics: Lista de métricas
        dimension_filter: Filtro opcional para dimensões
        metric_filter: Filtro opcional para métricas
        offset: Offset para paginação (padrão: 0)
        limit: Limite de resultados (padrão: 10000, máximo: 100000)
        order_bys: Lista de ordenações
        keep_empty_rows: Se True, mantém linhas vazias
        return_property_quota: Se True, retorna informações de quota

    Examples:
        >>> request = RunReportRequest(
        ...     property_id='properties/123456789',
        ...     date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
        ...     dimensions=[Dimension(name='country'), Dimension(name='city')],
        ...     metrics=[Metric(name='activeUsers'), Metric(name='sessions')]
        ... )
    """
    property_id: str
    date_ranges: List[DateRange]
    dimensions: List[Dimension] = field(default_factory=list)
    metrics: List[Metric] = field(default_factory=list)
    dimension_filter: Optional[Dict[str, Any]] = None
    metric_filter: Optional[Dict[str, Any]] = None
    offset: int = 0
    limit: int = 10000
    order_bys: List[OrderBy] = field(default_factory=list)
    keep_empty_rows: bool = False
    return_property_quota: bool = False

    def __post_init__(self):
        """Valida a requisição"""
        if not self.property_id:
            raise ValueError("property_id é obrigatório")

        if not self.property_id.startswith('properties/'):
            self.property_id = f'properties/{self.property_id}'

        if not self.date_ranges:
            raise ValueError("date_ranges é obrigatório e deve conter ao menos um intervalo")

        if not self.dimensions and not self.metrics:
            raise ValueError("Deve especificar ao menos uma dimension ou metric")

        if self.limit > 100000:
            raise ValueError("limit não pode ser maior que 100000")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário no formato esperado pela API"""
        result = {
            "dateRanges": [dr.to_dict() for dr in self.date_ranges],
            "offset": str(self.offset),
            "limit": str(self.limit),
            "keepEmptyRows": self.keep_empty_rows,
            "returnPropertyQuota": self.return_property_quota
        }

        if self.dimensions:
            result["dimensions"] = [d.to_dict() for d in self.dimensions]

        if self.metrics:
            result["metrics"] = [m.to_dict() for m in self.metrics]

        if self.dimension_filter:
            result["dimensionFilter"] = self.dimension_filter

        if self.metric_filter:
            result["metricFilter"] = self.metric_filter

        if self.order_bys:
            result["orderBys"] = [o.to_dict() for o in self.order_bys]

        return result

    def __str__(self) -> str:
        return (f"RunReportRequest(property={self.property_id}, "
                f"dimensions={len(self.dimensions)}, "
                f"metrics={len(self.metrics)})")


@dataclass
class FilterExpression:
    """
    Classe auxiliar para criar expressões de filtro.

    Examples:
        >>> # Filtro simples
        >>> filter_exp = FilterExpression.string_filter(
        ...     dimension_name='country',
        ...     value='Brazil',
        ...     match_type='EXACT'
        ... )

        >>> # Filtro numérico
        >>> filter_exp = FilterExpression.numeric_filter(
        ...     metric_name='sessions',
        ...     value=100,
        ...     operation='GREATER_THAN'
        ... )
    """

    @staticmethod
    def string_filter(dimension_name: str, value: str, match_type: str = 'EXACT',
                     case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Cria um filtro de string para dimensões.

        Args:
            dimension_name: Nome da dimensão
            value: Valor para filtrar
            match_type: Tipo de correspondência ('EXACT', 'BEGINS_WITH', 'ENDS_WITH',
                       'CONTAINS', 'FULL_REGEXP', 'PARTIAL_REGEXP')
            case_sensitive: Se o filtro deve ser case-sensitive
        """
        return {
            "filter": {
                "fieldName": dimension_name,
                "stringFilter": {
                    "matchType": match_type,
                    "value": value,
                    "caseSensitive": case_sensitive
                }
            }
        }

    @staticmethod
    def numeric_filter(metric_name: str, value: float,
                      operation: str = 'EQUAL') -> Dict[str, Any]:
        """
        Cria um filtro numérico para métricas.

        Args:
            metric_name: Nome da métrica
            value: Valor para filtrar
            operation: Operação ('EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL',
                      'GREATER_THAN', 'GREATER_THAN_OR_EQUAL')
        """
        return {
            "filter": {
                "fieldName": metric_name,
                "numericFilter": {
                    "operation": operation,
                    "value": {"doubleValue": value}
                }
            }
        }

    @staticmethod
    def in_list_filter(dimension_name: str, values: List[str],
                      case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Cria um filtro para verificar se o valor está em uma lista.

        Args:
            dimension_name: Nome da dimensão
            values: Lista de valores
            case_sensitive: Se o filtro deve ser case-sensitive
        """
        return {
            "filter": {
                "fieldName": dimension_name,
                "inListFilter": {
                    "values": values,
                    "caseSensitive": case_sensitive
                }
            }
        }

    @staticmethod
    def and_group(expressions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combina múltiplas expressões com operador AND"""
        return {
            "andGroup": {
                "expressions": expressions
            }
        }

    @staticmethod
    def or_group(expressions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combina múltiplas expressões com operador OR"""
        return {
            "orGroup": {
                "expressions": expressions
            }
        }

    @staticmethod
    def not_expression(expression: Dict[str, Any]) -> Dict[str, Any]:
        """Nega uma expressão"""
        return {
            "notExpression": expression
        }
