import uuid
from datetime import datetime
from typing import List, Tuple
from ..models.documents import ReconciliationInput, CommercialInvoice, PackingList, DUIMPDeclaration
from ..models.reconciliation import (
    RiskChannel,
    DiscrepancySeverity,
    DiscrepancyCategory,
    DiscrepancyItem,
    SemanticNCMAnalysis,
    ReconciliationSummary,
    ReconciliationResult,
)
from .tax_calculator import TaxCalculator
from .ai_analyzer import GeminiComexAnalyzer


class CustomsReconciliationEngine:
    """
    Motor Central de Conciliação Aduaneira com validações tributárias brasileiras
    e integração com inteligência artificial Gemini 3.8 Flash.
    """

    def __init__(self, ai_analyzer: GeminiComexAnalyzer = None):
        self.ai_analyzer = ai_analyzer or GeminiComexAnalyzer()

    async def reconcile(self, input_data: ReconciliationInput) -> ReconciliationResult:
        execution_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scenario_name = input_data.scenario_id or "Operação Customizada Comexport"

        discrepancies: List[DiscrepancyItem] = []
        semantic_analyses: List[SemanticNCMAnalysis] = []
        total_checks = 0

        invoice = input_data.invoice
        packing = input_data.packing_list
        duimp = input_data.duimp
        ref_ptax = input_data.reference_ptax
        weight_tol_pct = input_data.weight_tolerance_pct

        # ---------------------------------------------------------
        # 1. Validação Matemática da Commercial Invoice
        # ---------------------------------------------------------
        total_checks += 1
        items_sum = round(sum(item.total_price for item in invoice.items), 2)
        if abs(items_sum - invoice.total_amount) > 0.05:
            discrepancies.append(
                DiscrepancyItem(
                    id=f"DISC-{len(discrepancies)+1:03d}",
                    category=DiscrepancyCategory.VALUATION,
                    severity=DiscrepancySeverity.CRITICAL,
                    title="Inconsistência na Soma dos Itens da Invoice",
                    description=(
                        f"A soma aritmética dos itens faturados (US$ {items_sum:,.2f}) "
                        f"diverge do total declarado no cabeçalho da fatura (US$ {invoice.total_amount:,.2f})."
                    ),
                    expected_value=f"US$ {invoice.total_amount:,.2f}",
                    actual_value=f"US$ {items_sum:,.2f}",
                    difference=f"US$ {abs(items_sum - invoice.total_amount):,.2f}",
                    suggested_action="Solicitar retificação imediata da Commercial Invoice ao exportador para evitar rejeição no Siscomex."
                )
            )

        # ---------------------------------------------------------
        # 2. Validação do Valor Aduaneiro Conforme Incoterm
        # ---------------------------------------------------------
        total_checks += 1
        expected_customs_usd = TaxCalculator.calculate_customs_value(
            items_total=invoice.total_amount,
            incoterm=invoice.incoterm,
            freight=invoice.freight_amount,
            insurance=invoice.insurance_amount
        )
        diff_val = abs(expected_customs_usd - duimp.total_customs_value_usd)
        if diff_val > 0.10:
            diff_pct = (diff_val / expected_customs_usd * 100.0) if expected_customs_usd > 0 else 0
            severity = DiscrepancySeverity.CRITICAL if (diff_pct > 3.0 or diff_val > 25000.0) else DiscrepancySeverity.WARNING
            discrepancies.append(
                DiscrepancyItem(
                    id=f"DISC-{len(discrepancies)+1:03d}",
                    category=DiscrepancyCategory.INCOTERM,
                    severity=severity,
                    title=f"Divergência de Composição do Valor Aduaneiro ({invoice.incoterm})",
                    description=(
                        f"Sob o Incoterm {invoice.incoterm}, o Valor Aduaneiro esperado é US$ {expected_customs_usd:,.2f}, "
                        f"mas a DUIMP foi preenchida com US$ {duimp.total_customs_value_usd:,.2f}."
                    ),
                    expected_value=f"US$ {expected_customs_usd:,.2f}",
                    actual_value=f"US$ {duimp.total_customs_value_usd:,.2f}",
                    difference=f"US$ {abs(expected_customs_usd - duimp.total_customs_value_usd):,.2f}",
                    suggested_action=f"Ajustar a base de cálculo da DUIMP para considerar corretamente frete (US$ {invoice.freight_amount:,.2f}) e seguro (US$ {invoice.insurance_amount:,.2f})."
                )
            )

        # ---------------------------------------------------------
        # 3. Validação de Pesos e Romaneio (Packing List vs DUIMP)
        # ---------------------------------------------------------
        total_checks += 1
        # Variação percentual do peso bruto
        gross_diff_kg = duimp.total_gross_weight_kg - packing.total_gross_weight_kg
        gross_diff_pct = abs(gross_diff_kg / packing.total_gross_weight_kg) * 100.0 if packing.total_gross_weight_kg > 0 else 0

        if gross_diff_pct > weight_tol_pct:
            is_critical = gross_diff_pct > 3.0
            discrepancies.append(
                DiscrepancyItem(
                    id=f"DISC-{len(discrepancies)+1:03d}",
                    category=DiscrepancyCategory.WEIGHT,
                    severity=DiscrepancySeverity.CRITICAL if is_critical else DiscrepancySeverity.WARNING,
                    title="Divergência de Peso Bruto acima da Tolerância",
                    description=(
                        f"O peso bruto declarado na DUIMP ({duimp.total_gross_weight_kg:,.2f} kg) varia {gross_diff_pct:.2f}% "
                        f"em relação ao Packing List ({packing.total_gross_weight_kg:,.2f} kg). Limite tolerado: {weight_tol_pct:.1f}%."
                    ),
                    expected_value=f"{packing.total_gross_weight_kg:,.2f} kg",
                    actual_value=f"{duimp.total_gross_weight_kg:,.2f} kg",
                    difference=f"{gross_diff_kg:+,.2f} kg ({gross_diff_pct:.2f}%)",
                    suggested_action="Conferir a pesagem oficial da balança portuária antes da parametrização para evitar retenção em Canal Vermelho."
                )
            )

        # ---------------------------------------------------------
        # 4. Validação da Taxa Cambial PTAX e Conversão BRL
        # ---------------------------------------------------------
        total_checks += 1
        ptax_diff = abs(duimp.ptax_rate - ref_ptax)
        if ptax_diff > 0.0050: # Tolerância de meio centavo
            discrepancies.append(
                DiscrepancyItem(
                    id=f"DISC-{len(discrepancies)+1:03d}",
                    category=DiscrepancyCategory.EXCHANGE_RATE,
                    severity=DiscrepancySeverity.WARNING,
                    title="Taxa PTAX Fiscal Divergente da Data Oficial",
                    description=(
                        f"A taxa cambial adotada na DUIMP (R$ {duimp.ptax_rate:.4f}) difere da taxa oficial PTAX "
                        f"do Banco Central / Siscomex para a data de registro (R$ {ref_ptax:.4f})."
                    ),
                    expected_value=f"R$ {ref_ptax:.4f}",
                    actual_value=f"R$ {duimp.ptax_rate:.4f}",
                    difference=f"R$ {ptax_diff:.4f}",
                    suggested_action="Atualizar a taxa cambial da declaração para a PTAX de fechamento do dia útil anterior."
                )
            )

        # ---------------------------------------------------------
        # 5. Conciliação Item a Item & Validação Semântica de NCM (Gemini 3.8 Flash)
        # ---------------------------------------------------------
        invoice_items_by_sku = {item.sku: item for item in invoice.items}
        
        for duimp_item in duimp.items:
            total_checks += 1
            inv_item = invoice_items_by_sku.get(duimp_item.product_catalog_code or duimp_item.description) or (
                invoice.items[duimp_item.item_number - 1] if duimp_item.item_number <= len(invoice.items) else None
            )

            if inv_item:
                # Checagem de NCM
                clean_inv_ncm = inv_item.ncm.replace(".", "").strip()
                clean_duimp_ncm = duimp_item.ncm.replace(".", "").strip()

                if clean_inv_ncm != clean_duimp_ncm:
                    discrepancies.append(
                        DiscrepancyItem(
                            id=f"DISC-{len(discrepancies)+1:03d}",
                            category=DiscrepancyCategory.NCM,
                            severity=DiscrepancySeverity.CRITICAL,
                            title=f"Inconsistência de NCM no Item {duimp_item.item_number} ({inv_item.sku})",
                            description=(
                                f"A NCM indicada na fatura do exportador ({inv_item.ncm}) não coincide "
                                f"com a NCM preenchida na DUIMP ({duimp_item.ncm})."
                            ),
                            expected_value=inv_item.ncm,
                            actual_value=duimp_item.ncm,
                            difference="Classificação conflitante",
                            suggested_action="Submeter ao departamento de classificação fiscal e retificar a declaração ou solicitar aditivo à fatura."
                        )
                    )

                # Chamada de Avaliação Semântica pelo Gemini 3.8 Flash
                analysis = await self.ai_analyzer.evaluate_ncm_semantics(
                    sku=inv_item.sku,
                    international_desc=inv_item.description,
                    declared_ncm=duimp_item.ncm,
                    declared_desc=duimp_item.description
                )
                semantic_analyses.append(analysis)

                if not analysis.semantic_match:
                    discrepancies.append(
                        DiscrepancyItem(
                            id=f"DISC-{len(discrepancies)+1:03d}",
                            category=DiscrepancyCategory.NCM,
                            severity=DiscrepancySeverity.CRITICAL,
                            title=f"Alerta IA (Gemini 3.8 Flash): Incoerência Técnica de NCM",
                            description=analysis.ai_evaluation,
                            expected_value=f"Compatível com '{inv_item.description}'",
                            actual_value=f"NCM {duimp_item.ncm}",
                            difference="Desvio conceitual de classificação",
                            suggested_action=f"Avaliar enquadramento na NCM sugerida pela IA: {analysis.recommended_ncm or 'Sob análise técnica'}."
                        )
                    )

        # ---------------------------------------------------------
        # 6. Apuração do Semáforo de Risco & Penalidades
        # ---------------------------------------------------------
        critical_count = sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.CRITICAL)
        warning_count = sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.WARNING)
        info_count = sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.INFO)

        if critical_count > 0:
            channel = RiskChannel.VERMELHO
            risk_score = max(10.0, round(100.0 - (critical_count * 30.0) - (warning_count * 10.0), 1))
            approved = False
        elif warning_count > 0:
            channel = RiskChannel.AMARELO
            risk_score = max(60.0, round(100.0 - (warning_count * 12.0), 1))
            approved = False
        else:
            channel = RiskChannel.VERDE
            risk_score = 99.4
            approved = True

        # Estimativa de exposição a penalidades
        potential_penalty = 0.0
        for d in discrepancies:
            potential_penalty += TaxCalculator.calculate_potential_penalty(
                d.category.value,
                duimp.total_customs_value_brl
            )

        # Parecer executivo da IA
        ai_summary = await self.ai_analyzer.generate_executive_diagnosis(
            scenario_name=scenario_name,
            channel=channel.value,
            discrepancies=discrepancies,
            total_value_usd=duimp.total_customs_value_usd
        )

        summary = ReconciliationSummary(
            total_checks=total_checks,
            critical_issues=critical_count,
            warning_issues=warning_count,
            info_issues=info_count,
            risk_channel=channel,
            risk_score=risk_score,
            ai_executive_summary=ai_summary,
            total_declared_brl=duimp.total_customs_value_brl,
            potential_penalty_risk_brl=round(potential_penalty, 2)
        )

        return ReconciliationResult(
            execution_id=execution_id,
            timestamp=timestamp,
            scenario_name=scenario_name,
            duimp_approved=approved,
            summary=summary,
            discrepancies=discrepancies,
            semantic_analysis=semantic_analyses
        )
