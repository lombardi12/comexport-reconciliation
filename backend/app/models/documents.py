from typing import List, Optional
from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    sku: str = Field(..., description="Código do produto pelo fornecedor")
    description: str = Field(..., description="Descrição comercial do item (ex: em inglês)")
    ncm: str = Field(..., description="NCM sugerida pelo exportador (8 dígitos)")
    quantity: float = Field(..., gt=0, description="Quantidade faturada")
    unit_price: float = Field(..., gt=0, description="Preço unitário na moeda de origem")
    total_price: float = Field(..., gt=0, description="Total faturado do item")
    country_of_origin: str = Field(default="CN", description="País de origem ISO-2")


class CommercialInvoice(BaseModel):
    invoice_number: str = Field(..., description="Número da Commercial Invoice")
    issue_date: str = Field(..., description="Data de emissão (YYYY-MM-DD)")
    supplier_name: str = Field(..., description="Razão social do fornecedor internacional")
    buyer_name: str = Field(..., description="Comprador / Importador (ex: Comexport)")
    currency: str = Field(default="USD", description="Moeda da transação (USD, EUR, CNY)")
    incoterm: str = Field(default="CIF", description="Termo Internacional de Comércio (CIF, FOB, CFR, FCA, etc.)")
    freight_amount: float = Field(default=0.0, ge=0, description="Valor do frete internacional destacado")
    insurance_amount: float = Field(default=0.0, ge=0, description="Valor do seguro internacional destacado")
    items: List[InvoiceItem] = Field(..., min_length=1, description="Lista de itens faturados")
    total_amount: float = Field(..., gt=0, description="Valor total da fatura")


class PackingListItem(BaseModel):
    sku: str = Field(..., description="Código do produto correspondente")
    package_type: str = Field(default="Pallet", description="Tipo de embalagem (Pallet, Caixa, Container)")
    package_count: int = Field(default=1, gt=0, description="Quantidade de volumes")
    net_weight_kg: float = Field(..., gt=0, description="Peso líquido total do item em kg")
    gross_weight_kg: float = Field(..., gt=0, description="Peso bruto total do item em kg")


class PackingList(BaseModel):
    packing_list_number: str = Field(..., description="Número do Romaneio de Carga")
    issue_date: str = Field(..., description="Data de emissão (YYYY-MM-DD)")
    total_packages: int = Field(..., gt=0, description="Total geral de volumes/embalagens")
    total_net_weight_kg: float = Field(..., gt=0, description="Peso líquido total manifestado em kg")
    total_gross_weight_kg: float = Field(..., gt=0, description="Peso bruto total manifestado em kg")
    container_numbers: List[str] = Field(default_factory=list, description="Identificadores dos contêineres")
    items: List[PackingListItem] = Field(..., min_length=1, description="Detalhamento de pesos por item")


class DUIMPItem(BaseModel):
    item_number: int = Field(..., description="Número sequencial do item na DUIMP")
    ncm: str = Field(..., description="NCM declarada na Receita Federal (8 dígitos)")
    product_catalog_code: Optional[str] = Field(default=None, description="Código do Catálogo de Produtos RFB")
    description: str = Field(..., description="Descrição padronizada em Português conforme catálogo")
    quantity: float = Field(..., gt=0, description="Quantidade na unidade estatística")
    customs_value_usd: float = Field(..., gt=0, description="Valor aduaneiro do item em USD")
    customs_value_brl: float = Field(..., gt=0, description="Valor aduaneiro do item em BRL")
    ii_rate: float = Field(default=0.0, ge=0, description="Alíquota do Imposto de Importação (%)")
    ipi_rate: float = Field(default=0.0, ge=0, description="Alíquota do IPI (%)")
    pis_rate: float = Field(default=2.1, ge=0, description="Alíquota do PIS Importação (%)")
    cofins_rate: float = Field(default=9.65, ge=0, description="Alíquota da COFINS Importação (%)")


class DUIMPDeclaration(BaseModel):
    duimp_number: str = Field(..., description="Número de rascunho ou protocolo da DUIMP")
    importador_cnpj: str = Field(..., description="CNPJ da Comexport ou cliente contratante")
    importador_nome: str = Field(..., description="Razão Social do Importador")
    urog_desembaraco: str = Field(default="0717700", description="Unidade da Receita Federal (ex: Porto de Vitória)")
    modal: str = Field(default="MARITIMO", description="Modal de transporte (MARITIMO, AEREO, RODOVIARIO)")
    ptax_rate: float = Field(..., gt=0, description="Taxa de câmbio fiscal PTAX utilizada para conversão")
    total_customs_value_usd: float = Field(..., gt=0, description="Valor aduaneiro total em USD")
    total_customs_value_brl: float = Field(..., gt=0, description="Valor aduaneiro total em BRL")
    total_net_weight_kg: float = Field(..., gt=0, description="Peso líquido total declarado na DUIMP em kg")
    total_gross_weight_kg: float = Field(..., gt=0, description="Peso bruto total declarado na DUIMP em kg")
    items: List[DUIMPItem] = Field(..., min_length=1, description="Itens declarados na DUIMP")


class ReconciliationInput(BaseModel):
    scenario_id: Optional[str] = Field(default=None, description="Identificador de cenário pré-definido")
    invoice: CommercialInvoice
    packing_list: PackingList
    duimp: DUIMPDeclaration
    reference_ptax: float = Field(default=5.4500, gt=0, description="Taxa PTAX oficial de referência para conferência")
    weight_tolerance_pct: float = Field(default=1.0, ge=0, le=10.0, description="Tolerância aceitável de variação de peso (%)")
