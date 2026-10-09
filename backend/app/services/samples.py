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
    2. GWM Brasil - Haval & Componentes Híbridos (Canal Amarelo)
    3. Polo Automotivo do Ceará (PACE) - Autopeças e Arredondamento Cambial (Canal Amarelo)
    4. Aviação Executiva - Turbina Gulfstream CFM56 (Canal Verde)
    5. Aviação Comercial - Trem de Pouso & NCM Indevida (Canal Vermelho)
    6. Insumos Agrícolas - Ureia vs Fosfato + Estouro de Peso (Canal Vermelho)
    7. Agronegócio - Cloreto de Potássio KCl Granulado (Canal Verde)
    8. Siderurgia & Metais - Bobinas de Aço Inox Laminadas (Canal Vermelho)
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
                "id": "gwm_haval_parts",
                "title": "2. GWM Brasil - Haval H6 & Módulos Híbridos (Canal Amarelo)",
                "category": "Automotivo & Eletromobilidade",
                "client": "Great Wall Motors / Comexport",
                "expected_channel": "AMARELO",
                "description": "Módulos de motor elétrico e baterias sob Incoterm FOB com pequena divergência em despesas portuárias de capatazia."
            },
            {
                "id": "pace_automotive_parts",
                "title": "3. Polo Automotivo Ceará (PACE) - Autopeças (Canal Amarelo)",
                "category": "Indústria Automotiva & PDI",
                "client": "PACE Ceará / Comexport",
                "expected_channel": "AMARELO",
                "description": "Componentes de chassis e freios com pequena variação cambial de PTAX e ausência de destaque de seguro no Incoterm FOB."
            },
            {
                "id": "aviation_turbine_gulfstream",
                "title": "4. Aviação Executiva - Turbina CFM56 Gulfstream (Canal Verde)",
                "category": "Aviação & Defesa",
                "client": "Comexport Aviation / Liderança Setorial",
                "expected_channel": "VERDE",
                "description": "Turbofan aeronáutico para jato executivo via Aeroporto de Viracopos (VCP). Regime especial aeronáutico e Certificado FAA 8130 100% em conformidade."
            },
            {
                "id": "aviation_landing_gear_alert",
                "title": "5. Aviação Comercial - Trem de Pouso & Freios (Canal Vermelho)",
                "category": "Aviação & Defesa",
                "client": "Comexport Aviation MRO",
                "expected_channel": "VERMELHO",
                "description": "Conjunto de atuadores e freios aeronáuticos cadastrado com NCM genérica sem benefício de alíquota zero. Risco tributário elevado."
            },
            {
                "id": "chemical_fertilizer_alert",
                "title": "6. Insumos Agrícolas - Fertilizantes Químicos (Canal Vermelho)",
                "category": "Química & Fertilizantes",
                "client": "Kalium Chemical / Comexport Agro",
                "expected_channel": "VERMELHO",
                "description": "Carga a granel de Ureia com divergência conceitual grave de NCM (Superfosfatos) e estouro de peso de 460 toneladas no terminal."
            },
            {
                "id": "fertilizer_kcl_potassium",
                "title": "7. Comexport Agro - Cloreto de Potássio KCl (Canal Verde)",
                "category": "Química & Fertilizantes",
                "client": "Canpotex / Comexport Agro",
                "expected_channel": "VERDE",
                "description": "Importação de 20.000 toneladas de KCl via Porto de Paranaguá. Modal marítimo a granel com documentação e laudo MAPA perfeitamente aderentes."
            },
            {
                "id": "steel_coils_stainless",
                "title": "8. Siderurgia - Bobinas de Aço Inox Laminadas (Canal Vermelho)",
                "category": "Siderurgia & Metais",
                "client": "Posco / Comexport Metais",
                "expected_channel": "VERMELHO",
                "description": "Bobinas de aço inoxidável AISI 304 via Porto de São Francisco do Sul com NCM manipulada na faixa de espessura para burlar alíquota antidumping."
            }
        ]

    @staticmethod
    def get_all_scenarios_full() -> Dict[str, ReconciliationInput]:
        return {
            "byd_ev_shipment": SampleScenariosRepository._build_byd_scenario(),
            "gwm_haval_parts": SampleScenariosRepository._build_gwm_scenario(),
            "pace_automotive_parts": SampleScenariosRepository._build_pace_scenario(),
            "aviation_turbine_gulfstream": SampleScenariosRepository._build_aviation_turbine_scenario(),
            "aviation_landing_gear_alert": SampleScenariosRepository._build_aviation_landing_gear_scenario(),
            "chemical_fertilizer_alert": SampleScenariosRepository._build_chemical_scenario(),
            "fertilizer_kcl_potassium": SampleScenariosRepository._build_fertilizer_kcl_scenario(),
            "steel_coils_stainless": SampleScenariosRepository._build_steel_coils_scenario(),
        }

    @staticmethod
    def get_scenario(scenario_id: str) -> ReconciliationInput:
        scenarios = {
            "byd_ev_shipment": SampleScenariosRepository._build_byd_scenario,
            "gwm_haval_parts": SampleScenariosRepository._build_gwm_scenario,
            "pace_automotive_parts": SampleScenariosRepository._build_pace_scenario,
            "aviation_turbine_gulfstream": SampleScenariosRepository._build_aviation_turbine_scenario,
            "aviation_landing_gear_alert": SampleScenariosRepository._build_aviation_landing_gear_scenario,
            "chemical_fertilizer_alert": SampleScenariosRepository._build_chemical_scenario,
            "fertilizer_kcl_potassium": SampleScenariosRepository._build_fertilizer_kcl_scenario,
            "steel_coils_stainless": SampleScenariosRepository._build_steel_coils_scenario,
        }
        builder = scenarios.get(scenario_id, SampleScenariosRepository._build_byd_scenario)
        return builder()

    # -------------------------------------------------------------
    # 1. BYD Auto (Verde)
    # -------------------------------------------------------------
    @staticmethod
    def _build_byd_scenario() -> ReconciliationInput:
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

    # -------------------------------------------------------------
    # 2. GWM Brasil - Haval & Peças (Amarelo)
    # -------------------------------------------------------------
    @staticmethod
    def _build_gwm_scenario() -> ReconciliationInput:
        invoice = CommercialInvoice(
            invoice_number="GWM-EXP-2026-3301",
            issue_date="2026-10-01",
            supplier_name="GREAT WALL MOTOR COMPANY LTD (Baoding, China)",
            buyer_name="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            currency="USD",
            incoterm="FOB",
            freight_amount=32000.0,
            insurance_amount=2400.0,
            items=[
                InvoiceItem(
                    sku="GWM-HYBRID-MOTOR-01",
                    description="Electric Traction Motor and Dual-Inverter Assembly for Haval H6 DHT",
                    ncm="8501.52.90",
                    quantity=200.0,
                    unit_price=1750.0,
                    total_price=350000.0,
                    country_of_origin="CN"
                )
            ],
            total_amount=350000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-GWM-2026-3301",
            issue_date="2026-10-01",
            total_packages=40,
            total_net_weight_kg=18400.0,
            total_gross_weight_kg=20800.0,
            container_numbers=["MSKU8841920", "MSKU8841931"],
            items=[
                PackingListItem(sku="GWM-HYBRID-MOTOR-01", package_type="Crate", package_count=40, net_weight_kg=18400.0, gross_weight_kg=20800.0)
            ]
        )

        ptax = 5.4380
        # DUIMP declarou Valor Aduaneiro com pequeno arredondamento de frete (diferença de $800)
        expected_customs_usd = 350000.0 + 32000.0 + 2400.0 # 384,400.0
        declared_customs_usd = 383600.0 # Variação de $800 (<0.3% -> Warning)
        duimp = DUIMPDeclaration(
            duimp_number="26BR00034419-1",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0817800 - ALFANDEGA DO PORTO DE SANTOS",
            modal="MARITIMO",
            ptax_rate=ptax,
            total_customs_value_usd=declared_customs_usd,
            total_customs_value_brl=round(declared_customs_usd * ptax, 2),
            total_net_weight_kg=18400.0,
            total_gross_weight_kg=20800.0,
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="8501.52.90",
                    product_catalog_code="CAT-GWM-MOTOR-DHT",
                    description="Motores de tração de corrente alternada polifásicos de potência superior a 75 kW - Haval H6",
                    quantity=200.0,
                    customs_value_usd=declared_customs_usd,
                    customs_value_brl=round(declared_customs_usd * ptax, 2),
                    ii_rate=14.0,
                    ipi_rate=5.0,
                    pis_rate=2.1,
                    cofins_rate=9.65
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="gwm_haval_parts",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=ptax,
            weight_tolerance_pct=1.0
        )

    # -------------------------------------------------------------
    # 3. PACE Ceará (Amarelo)
    # -------------------------------------------------------------
    @staticmethod
    def _build_pace_scenario() -> ReconciliationInput:
        invoice = CommercialInvoice(
            invoice_number="PACE-AUTO-2026-302",
            issue_date="2026-10-05",
            supplier_name="BOSCH MOBILITY GMBH (Stuttgart, Germany)",
            buyer_name="COMEXPORT / POLO AUTOMOTIVO DO CEARA (PACE)",
            currency="USD",
            incoterm="FOB",
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
        duimp = DUIMPDeclaration(
            duimp_number="26BR00031005-2",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0317900 - ALFANDEGA DO PORTO DO PECEM (CE)",
            modal="MARITIMO",
            ptax_rate=5.4050,
            total_customs_value_usd=252500.0,
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

    # -------------------------------------------------------------
    # 4. Aviação Executiva - Turbina Gulfstream CFM56 (Verde)
    # -------------------------------------------------------------
    @staticmethod
    def _build_aviation_turbine_scenario() -> ReconciliationInput:
        invoice = CommercialInvoice(
            invoice_number="GE-AERO-2026-8802",
            issue_date="2026-10-06",
            supplier_name="GE AEROSPACE / SAFRAN AIRCRAFT ENGINES (Cincinnati, USA)",
            buyer_name="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR (AVIATION DIV)",
            currency="USD",
            incoterm="CIP",
            freight_amount=45000.0,
            insurance_amount=12000.0,
            items=[
                InvoiceItem(
                    sku="CFM56-7B27-TURBINE",
                    description="Aviation Turbofan Aircraft Engine Model CFM56-7B27 complete with FAA 8130-3 Airworthiness Certificate",
                    ncm="8411.12.00",
                    quantity=1.0,
                    unit_price=4850000.0,
                    total_price=4850000.0,
                    country_of_origin="US"
                )
            ],
            total_amount=4850000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-GE-AERO-8802",
            issue_date="2026-10-06",
            total_packages=1,
            total_net_weight_kg=2480.0,
            total_gross_weight_kg=3850.0,
            container_numbers=["AIR-WAYBILL 001-99482012 / FLIGHT GTI8122"],
            items=[
                PackingListItem(sku="CFM56-7B27-TURBINE", package_type="Aero Stand", package_count=1, net_weight_kg=2480.0, gross_weight_kg=3850.0)
            ]
        )

        ptax = 5.4290
        total_usd = 4850000.0
        total_brl = round(total_usd * ptax, 2)

        duimp = DUIMPDeclaration(
            duimp_number="26BR00040112-8",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0817700 - ALFANDEGA DO AEROPORTO DE VIRACOPOS (VCP)",
            modal="AEREO",
            ptax_rate=ptax,
            total_customs_value_usd=total_usd,
            total_customs_value_brl=total_brl,
            total_net_weight_kg=2480.0,
            total_gross_weight_kg=3850.0,
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="8411.12.00",
                    product_catalog_code="CAT-AERO-TURBOFAN-CFM",
                    description="Turborreatores de empuxo superior a 25 kN para uso em aeronaves civis - Regime Aduaneiro Aeronáutico",
                    quantity=1.0,
                    customs_value_usd=total_usd,
                    customs_value_brl=total_brl,
                    ii_rate=0.0, # Alíquota Zero - Regime Aeronáutico
                    ipi_rate=0.0, # Alíquota Zero
                    pis_rate=1.65,
                    cofins_rate=7.60
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="aviation_turbine_gulfstream",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=ptax,
            weight_tolerance_pct=1.0
        )

    # -------------------------------------------------------------
    # 5. Aviação Comercial - Trem de Pouso (Vermelho)
    # -------------------------------------------------------------
    @staticmethod
    def _build_aviation_landing_gear_scenario() -> ReconciliationInput:
        invoice = CommercialInvoice(
            invoice_number="SAFRAN-LG-2026-441",
            issue_date="2026-10-04",
            supplier_name="SAFRAN LANDING SYSTEMS (Velizy, France)",
            buyer_name="COMEXPORT AVIATION LOGISTICS",
            currency="USD",
            incoterm="CIP",
            freight_amount=15000.0,
            insurance_amount=3500.0,
            items=[
                InvoiceItem(
                    sku="AERO-MAIN-LANDING-GEAR",
                    description="Main Landing Gear Actuator and Braking Assembly for Civil Jet Aircraft",
                    ncm="8803.20.00", # NCM Correta de Trem de Pouso
                    quantity=2.0,
                    unit_price=420000.0,
                    total_price=840000.0,
                    country_of_origin="FR"
                )
            ],
            total_amount=840000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-SAFRAN-LG-441",
            issue_date="2026-10-04",
            total_packages=2,
            total_net_weight_kg=1280.0,
            total_gross_weight_kg=1640.0,
            container_numbers=["AWB 057-78192341 / AF0454"],
            items=[
                PackingListItem(sku="AERO-MAIN-LANDING-GEAR", package_type="Wooden Box", package_count=2, net_weight_kg=1280.0, gross_weight_kg=1640.0)
            ]
        )

        ptax = 5.4350
        total_usd = 840000.0
        # DUIMP preenchida errada: NCM genérica de máquinas gerais (8479.89.99)
        # com alíquota de 14% de II e 9.75% de IPI em vez de alíquota zero aeronáutica!
        duimp = DUIMPDeclaration(
            duimp_number="26BR00041920-3",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0817600 - ALFANDEGA DO AEROPORTO DE GUARULHOS (GRU)",
            modal="AEREO",
            ptax_rate=ptax,
            total_customs_value_usd=total_usd,
            total_customs_value_brl=round(total_usd * ptax, 2),
            total_net_weight_kg=1280.0,
            total_gross_weight_kg=1640.0,
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="8479.89.99", # ERRO GRAVE DE NCM (Aparelhos mecânicos gerais)
                    product_catalog_code="CAT-MECH-GENERIC",
                    description="Outras máquinas e aparelhos mecânicos com função própria não especificados",
                    quantity=2.0,
                    customs_value_usd=total_usd,
                    customs_value_brl=round(total_usd * ptax, 2),
                    ii_rate=14.0, # Tributação indevida de centenas de milhares de reais
                    ipi_rate=9.75,
                    pis_rate=2.1,
                    cofins_rate=9.65
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="aviation_landing_gear_alert",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=ptax,
            weight_tolerance_pct=1.0
        )

    # -------------------------------------------------------------
    # 6. Insumos Agrícolas - Ureia vs Fosfatos (Vermelho)
    # -------------------------------------------------------------
    @staticmethod
    def _build_chemical_scenario() -> ReconciliationInput:
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
                    ncm="3102.10.10",
                    quantity=5000.0,
                    unit_price=310.0,
                    total_price=1550000.0,
                    country_of_origin="CN"
                )
            ],
            total_amount=1550000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-KALIUM-771",
            issue_date="2026-10-02",
            total_packages=1,
            total_net_weight_kg=5000000.0,
            total_gross_weight_kg=5020000.0,
            container_numbers=["BULK CARRIER M/V PACIFIC LEADER"],
            items=[
                PackingListItem(sku="AGRO-UREA-46", package_type="Granel", package_count=1, net_weight_kg=5000000.0, gross_weight_kg=5020000.0)
            ]
        )

        ptax = 5.4500
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
            total_gross_weight_kg=5480000.0, # Divergência de peso >9%
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

    # -------------------------------------------------------------
    # 7. Fertilizantes - Cloreto de Potássio KCl (Verde)
    # -------------------------------------------------------------
    @staticmethod
    def _build_fertilizer_kcl_scenario() -> ReconciliationInput:
        invoice = CommercialInvoice(
            invoice_number="CANPOTEX-KCL-2026-102",
            issue_date="2026-10-03",
            supplier_name="CANPOTEX LIMITED (Saskatoon, Canada)",
            buyer_name="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR (AGRO)",
            currency="USD",
            incoterm="CFR",
            freight_amount=380000.0,
            insurance_amount=15000.0,
            items=[
                InvoiceItem(
                    sku="AGRO-KCL-RED-GRANULAR",
                    description="Muriate of Potash (MOP) Potassium Chloride Granular 60% K2O Agricultural Grade",
                    ncm="3104.20.90",
                    quantity=20000.0,
                    unit_price=295.0,
                    total_price=5900000.0,
                    country_of_origin="CA"
                )
            ],
            total_amount=5900000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-CANPOTEX-102",
            issue_date="2026-10-03",
            total_packages=1,
            total_net_weight_kg=20000000.0,
            total_gross_weight_kg=20015000.0,
            container_numbers=["PANAMAX BULK CARRIER M/V SASKATCHEWAN STAR"],
            items=[
                PackingListItem(sku="AGRO-KCL-RED-GRANULAR", package_type="Granel", package_count=1, net_weight_kg=20000000.0, gross_weight_kg=20015000.0)
            ]
        )

        ptax = 5.4310
        total_usd = 5900000.0 + 15000.0 # CFR + Seguro = 5,915,000 USD
        total_brl = round(total_usd * ptax, 2)

        duimp = DUIMPDeclaration(
            duimp_number="26BR00045091-0",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0917800 - ALFANDEGA DO PORTO DE PARANAGUA",
            modal="MARITIMO",
            ptax_rate=ptax,
            total_customs_value_usd=total_usd,
            total_customs_value_brl=total_brl,
            total_net_weight_kg=20000000.0,
            total_gross_weight_kg=20015000.0,
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="3104.20.90",
                    product_catalog_code="CAT-AGRO-POTASSIUM-KCL",
                    description="Outros cloretos de potássio com teor de K2O superior a 60% em peso - Adubo / Fertilizante",
                    quantity=20000.0,
                    customs_value_usd=total_usd,
                    customs_value_brl=total_brl,
                    ii_rate=0.0,
                    ipi_rate=0.0,
                    pis_rate=1.65,
                    cofins_rate=7.60
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="fertilizer_kcl_potassium",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=ptax,
            weight_tolerance_pct=1.0
        )

    # -------------------------------------------------------------
    # 8. Siderurgia - Bobinas de Aço Inox (Vermelho)
    # -------------------------------------------------------------
    @staticmethod
    def _build_steel_coils_scenario() -> ReconciliationInput:
        invoice = CommercialInvoice(
            invoice_number="POSCO-ST-2026-904",
            issue_date="2026-10-05",
            supplier_name="POSCO STEEL CORPORATION (Pohang, South Korea)",
            buyer_name="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR (METALS)",
            currency="USD",
            incoterm="CIF",
            freight_amount=68000.0,
            insurance_amount=5500.0,
            items=[
                InvoiceItem(
                    sku="POSCO-SS-COIL-304",
                    description="Cold-Rolled Stainless Steel Coils Grade AISI 304 2B Thickness 1.50mm Width 1219mm",
                    ncm="7219.34.00", # NCM Correta de Bobinas Inox com espessura de 1mm a 3mm
                    quantity=1200.0,
                    unit_price=2200.0,
                    total_price=2640000.0,
                    country_of_origin="KR"
                )
            ],
            total_amount=2640000.0
        )

        packing_list = PackingList(
            packing_list_number="PK-POSCO-ST-904",
            issue_date="2026-10-05",
            total_packages=48,
            total_net_weight_kg=1200000.0,
            total_gross_weight_kg=1214000.0,
            container_numbers=["BREAKBULK M/V KOREAN EMERALD"],
            items=[
                PackingListItem(sku="POSCO-SS-COIL-304", package_type="Steel Coil", package_count=48, net_weight_kg=1200000.0, gross_weight_kg=1214000.0)
            ]
        )

        ptax = 5.4360
        total_usd = 2640000.0
        total_brl = round(total_usd * ptax, 2)

        # DUIMP preenchida errada: NCM classificada como espessura superior a 4.75mm (7219.12.00)
        # com objetivo indevido de evitar a tarifa de defesa comercial antidumping!
        duimp = DUIMPDeclaration(
            duimp_number="26BR00047812-7",
            importador_cnpj="42.441.527/0001-44",
            importador_nome="COMEXPORT COMPANHIA DE COMERCIO EXTERIOR",
            urog_desembaraco="0927800 - ALFANDEGA DE SAO FRANCISCO DO SUL",
            modal="MARITIMO",
            ptax_rate=ptax,
            total_customs_value_usd=total_usd,
            total_customs_value_brl=total_brl,
            total_net_weight_kg=1200000.0,
            total_gross_weight_kg=1214000.0,
            items=[
                DUIMPItem(
                    item_number=1,
                    ncm="7219.12.00", # ERRO DE NCM: Laminados a quente espessura > 4.75mm
                    product_catalog_code="CAT-STEEL-HOT-ROLLED",
                    description="Produtos laminados planos de aço inoxidável laminados a quente de espessura superior a 4.75mm",
                    quantity=1200.0,
                    customs_value_usd=total_usd,
                    customs_value_brl=total_brl,
                    ii_rate=12.0,
                    ipi_rate=5.0,
                    pis_rate=2.1,
                    cofins_rate=9.65
                )
            ]
        )

        return ReconciliationInput(
            scenario_id="steel_coils_stainless",
            invoice=invoice,
            packing_list=packing_list,
            duimp=duimp,
            reference_ptax=ptax,
            weight_tolerance_pct=1.0
        )
