from typing import Dict, List
from ..models.documents import (
    ReconciliationInput,
    CommercialInvoice,
    InvoiceItem,
    PackingList,
    PackingListItem,
    DUIMPDeclaration,
    DUIMPItem,
)


class SampleScenariosRepository:
    """
    Cenários pré-configurados de operações reais da Comexport para demonstração:
    1. BYD Eletromobilidade (Veículos Elétricos - Sucesso / Canal Verde)
    2. Fertilizantes & Químicos (Ureia vs Fosfatados + Excesso de Peso - Canal Vermelho)
    3. Polo Automotivo do Ceará (PACE) - Autopeças e Arredondamento Cambial (Canal Amarelo)
    """

    @staticmethod
    def get_all_scenarios() -> List[Dict[str, str]]:
        return [
            {
                "id": "byd_ev_shipment",
                "title": "1. Lote BYD - Veículos Elétricos & Módulos (Canal Verde)",
                "category": "Automotivo & Eletromobilidade",
                "client": "BYD Auto do Brasil / Comexport",
                "expected_channel": "VERDE",
                "description": "Importação marítima via Porto de Vitória de 120 veículos elétricos e baterias LFP sob Incoterm CIF. 100% conciliado."
            },
            {
                "id": "chemical_fertilizer_alert",
                "title": "2. Insumos Agrícolas - Fertilizantes Químicos (Canal Vermelho)",
                "category": "Química & Fertilizantes",
                "client": "Kalium Chemical / Comexport Agro",
                "expected_channel": "VERMELHO",
                "description": "Carga a granel com divergência conceitual grave de NCM (Ureia x Fosfatados) e estouro de peso no terminal portuário."
            },
            {
                "id": "pace_automotive_parts",
                "title": "3. Polo Automotivo Ceará (PACE) - Autopeças (Canal Amarelo)",
                "category": "Indústria Automotiva & PDI",
                "client": "PACE Ceará / Comexport",
                "expected_channel": "AMARELO",
                "description": "Componentes de chassis e freios com pequena variação cambial de PTAX e ausência de destaque de seguro no Incoterm FOB."
            }
        ]

    @staticmethod
    def get_scenario(scenario_id: str) -> ReconciliationInput:
        if scenario_id == "byd_ev_shipment":
            return SampleScenariosRepository._build_byd_scenario()
        elif scenario_id == "chemical_fertilizer_alert":
            return SampleScenariosRepository._build_chemical_scenario()
        elif scenario_id == "pace_automotive_parts":
            return SampleScenariosRepository._build_pace_scenario()
        else:
            return SampleScenariosRepository._build_byd_scenario()

    @staticmethod
    def _build_byd_scenario() -> ReconciliationInput:
        """Cenário 1: Sucesso total (Canal Verde)"""
        invoice = CommercialInvoice(
            invoice_number="BYD-EXP-2026-9921",
            issue_date="2026-09-28",
            supplier_name="BYD AUTO INDUSTRY COMPANY LIMITED (Shenzhen, China)",
            buyer_name="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            currency="USD",
            incoterm="CIF",
            freight_amount=180000.0,
            insurance_amount=15000.0,
            items=[
                InvoiceItem(
                    sku="BYD-DOLPHIN-EV",
                    description="Electric Passenger Vehicle Model Dolphin Pure EV 44.9kWh",
                    ncm="8703.80.00",
                    quantity=80.0,
                    unit_price=18500.0,
                    total_price=1480000.0,
                    country_of_origin="CN"
                ),
                InvoiceItem(
                    sku="BYD-SEAL-EV",
                    description="Electric Passenger Sedan Model Seal AWD Long Range 82.5kWh",
                    ncm="8703.80.00",
                    quantity=40.0,
                    unit_price=24250.0,
                    total_price=970000.0,
                    country_of_origin="CN"
                )
            ],
            total_amount=2450000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-BYD-2026-9921",
            issue_date="2026-09-28",
            total_packages=120,
            total_net_weight_kg=186400.0,
            total_gross_weight_kg=214200.0,
            container_numbers=["RO-RO EXPLORER 1 - DECK A/B"],
            items=[
                PackingListItem(sku="BYD-DOLPHIN-EV", package_type="Unit", package_count=80, net_weight_kg=112400.0, gross_weight_kg=129600.0),
                PackingListItem(sku="BYD-SEAL-EV", package_type="Unit", package_count=40, net_weight_kg=74000.0, gross_weight_kg=84600.0)
            ]
        )

        ptax = 5.4215
        total_usd = 2450000.0
        total_brl = round(total_usd * ptax, 2)

        duimp = DUIMPDeclaration(
            duimp_number="26BR00018942-0",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0717700 - ALFANDEGA DO PORTO DE VITORIA",
            modal="MARITIMO",
            ptax_rate=ptax,
            total_customs_value_usd=total_usd,
            total_customs_value_brl=total_brl,
            total_net_weight_kg=186400.0,
            total_gross_weight_kg=214200.0,
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="8703.80.00",
                    product_catalog_code="CAT-BYD-DOLPHIN",
                    description="Automóvel de passageiros com propulsão exclusiva por motor elétrico - BYD Dolphin",
                    quantity=80.0,
                    customs_value_usd=1480000.0,
                    customs_value_brl=round(1480000.0 * ptax, 2),
                    ii_rate=18.0,
                    ipi_rate=5.0,
                    pis_rate=2.1,
                    cofins_rate=9.65
                ),
                DUIMPItem(
                    item_number=2,
                    ncm="8703.80.00",
                    product_catalog_code="CAT-BYD-SEAL",
                    description="Automóvel de passageiros com propulsão exclusiva por motor elétrico - BYD Seal AWD",
                    quantity=40.0,
                    customs_value_usd=970000.0,
                    customs_value_brl=round(970000.0 * ptax, 2),
                    ii_rate=18.0,
                    ipi_rate=5.0,
                    pis_rate=2.1,
                    cofins_rate=9.65
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="byd_ev_shipment",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=ptax,
            weight_tolerance_pct=1.0
        )

    @staticmethod
    def _build_chemical_scenario() -> ReconciliationInput:
        """Cenário 2: Erros críticos de NCM e peso (Canal Vermelho)"""
        invoice = CommercialInvoice(
            invoice_number="KALIUM-AGRO-2026-771",
            issue_date="2026-10-02",
            supplier_name="SINOCHEM FERTILIZER CORP (Tianjin, China)",
            buyer_name="COMEXPORT / KALIUM CHEMICAL",
            currency="USD",
            incoterm="CIF",
            freight_amount=45000.0,
            insurance_amount=4000.0,
            items=[
                InvoiceItem(
                    sku="AGRO-UREA-46",
                    description="Prilled Urea 46% Nitrogen Technical Agricultural Grade",
                    ncm="3102.10.10", # NCM Correta de Ureia
                    quantity=5000.0, # 5.000 toneladas
                    unit_price=310.0,
                    total_price=1550000.0,
                    country_of_origin="CN"
                )
            ],
            total_amount=1550000.0
        )

        # Packing list declara 5.000 toneladas (5.000.000 kg)
        packing_list = PackingList(
            packing_list_number="PK-KALIUM-771",
            issue_date="2026-10-02",
            total_packages=1,
            total_net_weight_kg=5000000.0,
            total_gross_weight_kg=5020000.0, # 5.020.000 kg
            container_numbers=["BULK CARRIER M/V PACIFIC LEADER"],
            items=[
                PackingListItem(sku="AGRO-UREA-46", package_type="Granel", package_count=1, net_weight_kg=5000000.0, gross_weight_kg=5020000.0)
            ]
        )

        ptax = 5.4500
        # DUIMP preenchida errada pelo despachante/parceiro:
        # Erro 1: NCM colocada como superfosfatos (3103.19.00) em vez de Ureia (3102.10.10)
        # Erro 2: Peso bruto preenchido como 5.480.000 kg (estouro de 9.1%!)
        duimp = DUIMPDeclaration(
            duimp_number="26BR00029141-9",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0717700 - ALFANDEGA DO PORTO DE VITORIA",
            modal="MARITIMO",
            ptax_rate=ptax,
            total_customs_value_usd=1550000.0,
            total_customs_value_brl=round(1550000.0 * ptax, 2),
            total_net_weight_kg=5000000.0,
            total_gross_weight_kg=5480000.0, # Divergência de 460.000 kg (>9%)
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="3103.19.00", # ERRO DE NCM (Superfosfatos)
                    product_catalog_code="CAT-AGRO-PHOSPHATE",
                    description="Superfosfatos concentrados para adubação - NCM Fosfatados",
                    quantity=5000.0,
                    customs_value_usd=1550000.0,
                    customs_value_brl=round(1550000.0 * ptax, 2),
                    ii_rate=0.0,
                    ipi_rate=0.0,
                    pis_rate=2.1,
                    cofins_rate=9.65
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="chemical_fertilizer_alert",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=ptax,
            weight_tolerance_pct=1.0
        )

    @staticmethod
    def _build_pace_scenario() -> ReconciliationInput:
        """Cenário 3: Atenção / Alerta de PTAX e Incoterm (Canal Amarelo)"""
        invoice = CommercialInvoice(
            invoice_number="PACE-AUTO-2026-302",
            issue_date="2026-10-05",
            supplier_name="BOSCH MOBILITY GMBH (Stuttgart, Germany)",
            buyer_name="COMEXPORT / POLO AUTOMOTIVO DO CEARA (PACE)",
            currency="USD",
            incoterm="FOB", # FOB exige adição de frete e seguro
            freight_amount=12500.0,
            insurance_amount=1200.0,
            items=[
                InvoiceItem(
                    sku="PACE-BRAKE-SYS-01",
                    description="Electronic Braking System ABS/ESP Control Unit for Hybrid EV Chassis",
                    ncm="8708.30.90",
                    quantity=500.0,
                    unit_price=480.0,
                    total_price=240000.0,
                    country_of_origin="DE"
                )
            ],
            total_amount=240000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-PACE-302",
            issue_date="2026-10-05",
            total_packages=25,
            total_net_weight_kg=1250.0,
            total_gross_weight_kg=1420.0,
            container_numbers=["TEMU8923011"],
            items=[
                PackingListItem(sku="PACE-BRAKE-SYS-01", package_type="Pallet", package_count=25, net_weight_kg=1250.0, gross_weight_kg=1420.0)
            ]
        )

        official_ptax = 5.4320
        # DUIMP preenchida com PTAX desatualizada (5.4050 - variação de 2.7 centavos)
        # E com Valor Aduaneiro que esqueceu de somar o seguro de US$ 1.200
        duimp = DUIMPDeclaration(
            duimp_number="26BR00031005-2",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0317900 - ALFANDEGA DO PORTO DO PECEM (CE)",
            modal="MARITIMO",
            ptax_rate=5.4050, # Divergência de taxa cambial
            total_customs_value_usd=252500.0, # FOB (240k) + Frete (12.5k), faltou o Seguro ($1.2k)
            total_customs_value_brl=round(252500.0 * 5.4050, 2),
            total_net_weight_kg=1250.0,
            total_gross_weight_kg=1420.0,
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="8708.30.90",
                    product_catalog_code="CAT-PACE-BRAKE-01",
                    description="Unidade hidráulica e de comando eletrônico de freios ABS/ESP para montagem de veículos híbridos",
                    quantity=500.0,
                    customs_value_usd=252500.0,
                    customs_value_brl=round(252500.0 * 5.4050, 2),
                    ii_rate=14.0,
                    ipi_rate=6.5,
                    pis_rate=2.1,
                    cofins_rate=9.65
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="pace_automotive_parts",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=official_ptax,
            weight_tolerance_pct=1.0
        )
