import pytest
from app.services.samples import SampleScenariosRepository
from app.services.reconciliation import CustomsReconciliationEngine
from app.services.tax_calculator import TaxCalculator
from app.models.reconciliation import RiskChannel, DiscrepancySeverity


@pytest.mark.anyio
async def test_byd_scenario_approves_green_channel():
    """Valida se o lote da BYD é 100% conciliado e classificado como Canal Verde."""
    input_data = SampleScenariosRepository.get_scenario("byd_ev_shipment")
    engine = CustomsReconciliationEngine()
    result = await engine.reconcile(input_data)

    assert result.duimp_approved is True
    assert result.summary.risk_channel == RiskChannel.VERDE
    assert result.summary.critical_issues == 0
    assert result.summary.risk_score >= 95.0
    assert len(result.discrepancies) == 0
    assert len(result.semantic_analysis) == 2
    assert all(a.semantic_match for a in result.semantic_analysis)


@pytest.mark.anyio
async def test_chemical_scenario_blocks_red_channel():
    """Valida se o cenário de fertilizantes químicos acusa Canal Vermelho por divergência de NCM e peso."""
    input_data = SampleScenariosRepository.get_scenario("chemical_fertilizer_alert")
    engine = CustomsReconciliationEngine()
    result = await engine.reconcile(input_data)

    assert result.duimp_approved is False
    assert result.summary.risk_channel == RiskChannel.VERMELHO
    assert result.summary.critical_issues >= 2
    assert result.summary.potential_penalty_risk_brl > 0

    # Verifica se detectou a inconsistência de peso (> 9%)
    weight_disc = next((d for d in result.discrepancies if d.category == "WEIGHT"), None)
    assert weight_disc is not None
    assert weight_disc.severity == DiscrepancySeverity.CRITICAL

    # Verifica se detectou o alerta de NCM
    ncm_disc = next((d for d in result.discrepancies if d.category == "NCM"), None)
    assert ncm_disc is not None


@pytest.mark.anyio
async def test_pace_scenario_flags_yellow_channel():
    """Valida se o cenário PACE Ceará detecta variação cambial e Incoterm como Canal Amarelo."""
    input_data = SampleScenariosRepository.get_scenario("pace_automotive_parts")
    engine = CustomsReconciliationEngine()
    result = await engine.reconcile(input_data)

    assert result.duimp_approved is False
    assert result.summary.risk_channel == RiskChannel.AMARELO
    assert result.summary.warning_issues >= 1
    assert result.summary.critical_issues == 0

    # Verifica se identificou a taxa PTAX defasada
    ptax_disc = next((d for d in result.discrepancies if d.category == "EXCHANGE_RATE"), None)
    assert ptax_disc is not None


@pytest.mark.anyio
async def test_aviation_turbine_scenario_approves_green():
    """Valida se a importação da turbina CFM56 (Aviação Executiva) é aprovada no Canal Verde."""
    input_data = SampleScenariosRepository.get_scenario("aviation_turbine_gulfstream")
    engine = CustomsReconciliationEngine()
    result = await engine.reconcile(input_data)

    assert result.duimp_approved is True
    assert result.summary.risk_channel == RiskChannel.VERDE
    assert result.summary.critical_issues == 0
    assert result.summary.risk_score >= 95.0
    assert any("aeronáutico" in a.ai_evaluation.lower() for a in result.semantic_analysis)


@pytest.mark.anyio
async def test_aviation_landing_gear_blocks_red():
    """Valida se o trem de pouso aeronáutico declarado com NCM indevida é bloqueado no Canal Vermelho."""
    input_data = SampleScenariosRepository.get_scenario("aviation_landing_gear_alert")
    engine = CustomsReconciliationEngine()
    result = await engine.reconcile(input_data)

    assert result.duimp_approved is False
    assert result.summary.risk_channel == RiskChannel.VERMELHO
    assert result.summary.critical_issues >= 1
    assert result.summary.potential_penalty_risk_brl > 0


@pytest.mark.anyio
async def test_fertilizer_kcl_approves_green():
    """Valida se o lote de 20.000 t de Cloreto de Potássio é aprovado no Canal Verde."""
    input_data = SampleScenariosRepository.get_scenario("fertilizer_kcl_potassium")
    engine = CustomsReconciliationEngine()
    result = await engine.reconcile(input_data)

    assert result.duimp_approved is True
    assert result.summary.risk_channel == RiskChannel.VERDE
    assert result.summary.critical_issues == 0


@pytest.mark.anyio
async def test_steel_coils_blocks_red():
    """Valida se as bobinas de inox com espessura adulterada na NCM caem no Canal Vermelho."""
    input_data = SampleScenariosRepository.get_scenario("steel_coils_stainless")
    engine = CustomsReconciliationEngine()
    result = await engine.reconcile(input_data)

    assert result.duimp_approved is False
    assert result.summary.risk_channel == RiskChannel.VERMELHO
    assert result.summary.critical_issues >= 1
    assert any("7219" in d.actual_value for d in result.discrepancies)


def test_tax_calculator_customs_value():
    """Testa regra de cálculo do Valor Aduaneiro conforme Incoterm."""
    val_fob = TaxCalculator.calculate_customs_value(100.0, "FOB", freight=20.0, insurance=5.0)
    assert val_fob == 125.0

    val_cif = TaxCalculator.calculate_customs_value(100.0, "CIF", freight=20.0, insurance=5.0)
    assert val_cif == 100.0


def test_tax_calculator_penalty_estimation():
    """Testa estimativa de risco de penalidades da Receita Federal."""
    penalty_ncm = TaxCalculator.calculate_potential_penalty("NCM", 1_000_000.0)
    assert penalty_ncm == 10_000.0 # 1% do valor aduaneiro
