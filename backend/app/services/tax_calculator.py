import math
from typing import Dict, Any


class TaxCalculator:
    """
    Motor de cálculo tributário e aduaneiro conforme legislação brasileira (IN RFB 2090/2022).
    """

    @staticmethod
    def calculate_customs_value(
        items_total: float,
        incoterm: str,
        freight: float = 0.0,
        insurance: float = 0.0
    ) -> float:
        """
        Calcula o Valor Aduaneiro na moeda de origem.
        Se FOB/FCA: Valor Aduaneiro = Mercadoria + Frete + Seguro
        Se CIF/CIP: Valor Aduaneiro = Total da Fatura (já inclui frete e seguro)
        Se CFR/CPT: Valor Aduaneiro = Fatura + Seguro
        """
        incoterm_upper = incoterm.upper().strip()
        
        if incoterm_upper in ["FOB", "FCA", "EXW", "FAS"]:
            return round(items_total + freight + insurance, 2)
        elif incoterm_upper in ["CFR", "CPT"]:
            return round(items_total + insurance, 2)
        elif incoterm_upper in ["CIF", "CIP"]:
            # No CIF, o total da fatura já deve contemplar frete e seguro
            return round(items_total, 2)
        else:
            return round(items_total + freight + insurance, 2)

    @staticmethod
    def convert_to_brl(value_usd: float, ptax: float) -> float:
        """Converte valor em moeda estrangeira para BRL com 2 casas decimais."""
        return round(value_usd * ptax, 2)

    @staticmethod
    def calculate_potential_penalty(discrepancy_category: str, base_value_brl: float) -> float:
        """
        Estima a exposição a penalidades fiscais da Receita Federal:
        - Erro de NCM / Classificação Fiscal Inexata: Multa de 1% do valor aduaneiro (mínimo R$ 500)
        - Subfaturamento / Subvaloração: Multa de 75% a 100% sobre a diferença de tributos
        - Diferença de Peso / Volume: Risco de armazenagem adicional e multa de 5% sobre frete/taxas
        """
        if discrepancy_category == "NCM":
            # Art. 711 do Regulamento Aduaneiro (Dec. 6.759/09)
            penalty = base_value_brl * 0.01
            return max(500.0, round(penalty, 2))
        elif discrepancy_category in ["VALUATION", "EXCHANGE_RATE"]:
            # Multa de ofício por diferença tributária
            return round(base_value_brl * 0.15, 2)
        elif discrepancy_category == "WEIGHT":
            # Custo médio estimado de retenção/demurrage (R$ 8.500)
            return 8500.0
        return 1000.0
