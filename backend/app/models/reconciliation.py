from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RiskChannel(str, Enum):
    VERDE = "VERDE"       # Liberado automaticamente / Conforme
    AMARELO = "AMARELO"   # Conferência documental / Atenção (tolerâncias ou pequenas divergências)
    VERMELHO = "VERMELHO" # Bloqueio / Conferência física e documental / Inconsistência grave


class DiscrepancySeverity(str, Enum):
    CRITICAL = "CRITICAL"   # Gera Canal Vermelho, multa ou retenção
    WARNING = "WARNING"     # Gera Canal Amarelo, requer conferência
    INFO = "INFO"           # Meramente informativo ou recomendação


class DiscrepancyCategory(str, Enum):
    NCM = "NCM"                           # Classificação fiscal divergente
    WEIGHT = "WEIGHT"                     # Inconsistência de peso líquido ou bruto
    VALUATION = "VALUATION"               # Soma de itens ou valor aduaneiro
    EXCHANGE_RATE = "EXCHANGE_RATE"       # Taxa PTAX defasada ou conversão errada
    INCOTERM = "INCOTERM"                 # Falta de frete/seguro ou destaque indevido
    DOCUMENTATION = "DOCUMENTATION"       # Falta de CNPJ, catálogo ou divergência de volumes


class DiscrepancyItem(BaseModel):
    id: str = Field(..., description="Identificador único da inconsistência")
    category: DiscrepancyCategory
    severity: DiscrepancySeverity
    title: str = Field(..., description="Título resumido do alerta")
    description: str = Field(..., description="Explicação detalhada da divergência")
    expected_value: str = Field(..., description="Valor esperado / Documento de origem")
    actual_value: str = Field(..., description="Valor encontrado no rascunho DUIMP")
    difference: Optional[str] = Field(default=None, description="Diferença absoluta ou percentual")
    suggested_action: str = Field(..., description="Recomendação de correção para o analista")


class SemanticNCMAnalysis(BaseModel):
    item_sku: str
    international_description: str
    declared_ncm: str
    declared_description: str
    confidence_score_pct: float = Field(..., ge=0, le=100, description="Nível de confiança da IA (Gemini 3.8 Flash)")
    semantic_match: bool = Field(..., description="Indica se a descrição comercial corresponde à NCM declarada")
    ai_evaluation: str = Field(..., description="Avaliação técnica gerada pelo Gemini 3.8 Flash")
    recommended_ncm: Optional[str] = Field(default=None, description="NCM sugerida caso haja divergência")


class ReconciliationSummary(BaseModel):
    total_checks: int = Field(..., description="Total de validações realizadas")
    critical_issues: int = Field(default=0, description="Divergências críticas")
    warning_issues: int = Field(default=0, description="Divergências de atenção")
    info_issues: int = Field(default=0, description="Notas informativas")
    risk_channel: RiskChannel = Field(..., description="Canal aduaneiro resultante")
    risk_score: float = Field(..., ge=0, le=100, description="Score de conformidade de 0 a 100")
    ai_executive_summary: str = Field(..., description="Parecer executivo gerado por IA")
    total_declared_brl: float = Field(..., description="Valor aduaneiro total em Reais")
    potential_penalty_risk_brl: float = Field(default=0.0, description="Estimativa de risco financeiro / multas potenciais")


class ReconciliationResult(BaseModel):
    execution_id: str
    timestamp: str
    scenario_name: str
    duimp_approved: bool = Field(..., description="Se a DUIMP pode ser transmitida automaticamente")
    summary: ReconciliationSummary
    discrepancies: List[DiscrepancyItem] = Field(default_factory=list)
    semantic_analysis: List[SemanticNCMAnalysis] = Field(default_factory=list)
