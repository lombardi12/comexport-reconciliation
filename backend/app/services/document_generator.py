import os
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .samples import SampleScenariosRepository


class DocumentPDFGenerator:
    """
    Gerador de Documentos Comerciais e Aduaneiros em formato PDF.
    Gera Commercial Invoices e Packing Lists autênticos para testes de upload
    e demonstração do Google Cloud Document AI e Gemini 3.8 Flash.
    """

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            # Diretório raiz comexport/samples/documents/
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.output_dir = os.path.join(base_dir, "samples", "documents")
        else:
            self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )
        self.subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748b"),
        )
        self.cell_style = ParagraphStyle(
            "CellNormal",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b"),
        )
        self.cell_bold = ParagraphStyle(
            "CellBold",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=10,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0f172a"),
        )
        self.cell_right = ParagraphStyle(
            "CellRight",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=10,
            alignment=2,
            textColor=colors.HexColor("#1e293b"),
        )

    def generate_invoice_pdf(self, scenario_id: str, filename: str) -> str:
        """Gera o PDF de uma Commercial Invoice para o cenário especificado."""
        scenario = SampleScenariosRepository.get_scenario(scenario_id)
        inv = scenario.invoice
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        elements = []

        # Cabeçalho da Fatura
        header_data = [
            [
                Paragraph(f"<b>{inv.supplier_name}</b><br/>International Trade & Manufacturing Operations", self.cell_style),
                Paragraph("<b>COMMERCIAL INVOICE</b><br/><font color='#2563eb'>ORIGINAL FOR CUSTOMS</font>", self.title_style),
            ]
        ]
        header_table = Table(header_data, colWidths=[4.2 * inch, 3.3 * inch])
        header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elements.append(header_table)

        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10))

        # Metadados: Fatura, Data, Comprador (Comexport)
        meta_data = [
            [
                Paragraph("<b>CONSIGNEE / BUYER:</b>", self.cell_bold),
                Paragraph("<b>INVOICE DETAILS:</b>", self.cell_bold),
            ],
            [
                Paragraph(
                    f"<b>{inv.buyer_name}</b><br/>"
                    "Avenida Brigadeiro Faria Lima, 2277 - São Paulo, SP, Brazil<br/>"
                    "CNPJ: 42.441.527/0001-44 • RADAR / SISCOMEX HABILITADO",
                    self.cell_style,
                ),
                Paragraph(
                    f"<b>Invoice No:</b> {inv.invoice_number}<br/>"
                    f"<b>Issue Date:</b> {inv.issue_date}<br/>"
                    f"<b>Currency:</b> {inv.currency}<br/>"
                    f"<b>Incoterm:</b> <b>{inv.incoterm}</b><br/>"
                    f"<b>Payment:</b> Irrevocable Letter of Credit (L/C 90 Days)",
                    self.cell_style,
                ),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[4.2 * inch, 3.3 * inch])
        meta_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        elements.append(meta_table)

        elements.append(Spacer(1, 15))
        elements.append(Paragraph("<b>MERCHANDISE DESCRIPTION & HS/NCM TARIFF CLASSIFICATION</b>", self.cell_bold))
        elements.append(Spacer(1, 5))

        # Tabela de Itens da Fatura
        items_data = [
            [
                Paragraph("<b>Item / SKU</b>", self.cell_bold),
                Paragraph("<b>Product Description (Commercial Spec)</b>", self.cell_bold),
                Paragraph("<b>NCM/HS</b>", self.cell_bold),
                Paragraph("<b>Qty</b>", self.cell_bold),
                Paragraph("<b>Unit (USD)</b>", self.cell_bold),
                Paragraph("<b>Total (USD)</b>", self.cell_bold),
            ]
        ]

        subtotal = 0.0
        for it in inv.items:
            subtotal += it.total_price
            items_data.append([
                Paragraph(it.sku, self.cell_style),
                Paragraph(it.description, self.cell_style),
                Paragraph(f"<b>{it.ncm}</b>", self.cell_style),
                Paragraph(f"{it.quantity:,.0f}", self.cell_right),
                Paragraph(f"${it.unit_price:,.2f}", self.cell_right),
                Paragraph(f"${it.total_price:,.2f}", self.cell_right),
            ])

        items_table = Table(items_data, colWidths=[1.1 * inch, 3.1 * inch, 0.9 * inch, 0.6 * inch, 0.9 * inch, 0.9 * inch])
        items_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        # Ajusta cabeçalho do grid com texto branco
        for i in range(len(items_data[0])):
            items_table.setStyle(TableStyle([("TEXTCOLOR", (i, 0), (i, 0), colors.white)]))
        elements.append(items_table)

        elements.append(Spacer(1, 10))

        # Totais Fiscais
        totals_data = [
            [Paragraph("Subtotal Items Value:", self.cell_bold), Paragraph(f"USD ${subtotal:,.2f}", self.cell_right)],
            [Paragraph("International Freight:", self.cell_style), Paragraph(f"USD ${inv.freight_amount:,.2f}", self.cell_right)],
            [Paragraph("International Marine/Air Insurance:", self.cell_style), Paragraph(f"USD ${inv.insurance_amount:,.2f}", self.cell_right)],
            [Paragraph(f"<b>TOTAL {inv.incoterm} VALUE:</b>", self.cell_bold), Paragraph(f"<b>USD ${inv.total_amount:,.2f}</b>", self.cell_right)],
        ]
        totals_table = Table(totals_data, colWidths=[2.0 * inch, 1.5 * inch])
        totals_table.setStyle(
            TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )

        wrapper_data = [[Paragraph("<i>Certified true and correct in all particulars.<br/>Export clearance processed under international conventions.</i>", self.subtitle_style), totals_table]]
        wrapper_table = Table(wrapper_data, colWidths=[4.0 * inch, 3.5 * inch])
        wrapper_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elements.append(wrapper_table)

        elements.append(Spacer(1, 30))

        # Assinatura e Carimbo
        sig_data = [
            [
                Paragraph("__________________________________________<br/>Authorized Signatory - Shipper/Exporter", self.cell_style),
                Paragraph("<b>[DOCUMENT AI VERIFIED]</b><br/>Google Cloud Document AI Ready", self.cell_right),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[4.5 * inch, 3.0 * inch])
        elements.append(sig_table)

        doc.build(elements)
        return filepath

    def generate_packing_list_pdf(self, scenario_id: str, filename: str) -> str:
        """Gera o PDF do Packing List (Romaneio de Carga) para o cenário especificado."""
        scenario = SampleScenariosRepository.get_scenario(scenario_id)
        pkl = scenario.packing_list
        inv = scenario.invoice
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        elements = []

        # Cabeçalho do Packing List
        header_data = [
            [
                Paragraph(f"<b>{inv.supplier_name}</b><br/>Global Logistics & Packaging Division", self.cell_style),
                Paragraph("<b>PACKING LIST / ROMANEIO</b><br/><font color='#059669'>CUSTOMS WEIGHT CARGO SHEET</font>", self.title_style),
            ]
        ]
        header_table = Table(header_data, colWidths=[4.2 * inch, 3.3 * inch])
        header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elements.append(header_table)

        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#059669"), spaceAfter=10))

        # Metadados
        meta_data = [
            [
                Paragraph("<b>LOGISTICS OPERATOR / BUYER:</b>", self.cell_bold),
                Paragraph("<b>MANIFEST & SHIPMENT DETAILS:</b>", self.cell_bold),
            ],
            [
                Paragraph(
                    f"<b>{inv.buyer_name}</b><br/>"
                    "Port Operative Despacho Aduaneiro 5PL<br/>"
                    "Recinto Alfandegado de Destino Registrado",
                    self.cell_style,
                ),
                Paragraph(
                    f"<b>Packing List No:</b> {pkl.packing_list_number}<br/>"
                    f"<b>Related Invoice No:</b> {inv.invoice_number}<br/>"
                    f"<b>Total Packages:</b> {pkl.total_packages} volumes<br/>"
                    f"<b>Units / Containers:</b> {', '.join(pkl.container_numbers)}",
                    self.cell_style,
                ),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[4.2 * inch, 3.3 * inch])
        meta_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        elements.append(meta_table)

        elements.append(Spacer(1, 15))
        elements.append(Paragraph("<b>PACKAGE BREAKDOWN & MEASURED WEIGHTS (KILOGRAMS)</b>", self.cell_bold))
        elements.append(Spacer(1, 5))

        # Tabela de Itens e Pesos
        items_data = [
            [
                Paragraph("<b>Item / SKU</b>", self.cell_bold),
                Paragraph("<b>Package Type</b>", self.cell_bold),
                Paragraph("<b>Qty Vol</b>", self.cell_bold),
                Paragraph("<b>Net Weight (Kg)</b>", self.cell_bold),
                Paragraph("<b>Gross Weight (Kg)</b>", self.cell_bold),
            ]
        ]

        for it in pkl.items:
            items_data.append([
                Paragraph(it.sku, self.cell_style),
                Paragraph(it.package_type, self.cell_style),
                Paragraph(f"{it.package_count:,.0f}", self.cell_right),
                Paragraph(f"{it.net_weight_kg:,.2f} kg", self.cell_right),
                Paragraph(f"{it.gross_weight_kg:,.2f} kg", self.cell_right),
            ])

        # Linha Total
        items_data.append([
            Paragraph("<b>TOTALS</b>", self.cell_bold),
            Paragraph("-", self.cell_style),
            Paragraph(f"<b>{pkl.total_packages}</b>", self.cell_right),
            Paragraph(f"<b>{pkl.total_net_weight_kg:,.2f} kg</b>", self.cell_right),
            Paragraph(f"<b>{pkl.total_gross_weight_kg:,.2f} kg</b>", self.cell_right),
        ])

        items_table = Table(items_data, colWidths=[2.2 * inch, 1.4 * inch, 0.9 * inch, 1.5 * inch, 1.5 * inch])
        items_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        elements.append(items_table)

        elements.append(Spacer(1, 30))

        # Rodapé e Validação de Balança
        footer_data = [
            [
                Paragraph("<b>PORT TERMINAL WEIGHBRIDGE CERTIFICATION:</b><br/>"
                          "Weights verified and certified under IMO SOLAS VGM (Verified Gross Mass) standards.", self.subtitle_style),
                Paragraph("__________________________________________<br/>Terminal Operations Officer", self.cell_right),
            ]
        ]
        footer_table = Table(footer_data, colWidths=[4.5 * inch, 3.0 * inch])
        elements.append(footer_table)

        doc.build(elements)
        return filepath

    def generate_all_samples(self) -> List[Dict[str, str]]:
        """Gera todos os arquivos PDF de Invoices e Packing Lists de todos os cenários."""
        scenarios = SampleScenariosRepository.get_all_scenarios()
        generated_files = []

        file_mappings = {
            "byd_ev_shipment": ("INV_BYD_9921.pdf", "PKL_BYD_9921.pdf"),
            "gwm_haval_parts": ("INV_GWM_3301.pdf", "PKL_GWM_3301.pdf"),
            "pace_automotive_parts": ("INV_PACE_302.pdf", "PKL_PACE_302.pdf"),
            "aviation_turbine_gulfstream": ("INV_GULFSTREAM_CFM56.pdf", "PKL_GULFSTREAM_CFM56.pdf"),
            "aviation_landing_gear_alert": ("INV_SAFRAN_LANDING_GEAR.pdf", "PKL_SAFRAN_LANDING_GEAR.pdf"),
            "chemical_fertilizer_alert": ("INV_SINOCHEM_UREA.pdf", "PKL_SINOCHEM_UREA.pdf"),
            "fertilizer_kcl_potassium": ("INV_CANPOTEX_KCL.pdf", "PKL_CANPOTEX_KCL.pdf"),
            "steel_coils_stainless": ("INV_POSCO_STAINLESS_STEEL.pdf", "PKL_POSCO_STAINLESS_STEEL.pdf"),
        }

        for sc in scenarios:
            sc_id = sc["id"]
            if sc_id in file_mappings:
                inv_file, pkl_file = file_mappings[sc_id]

                inv_path = self.generate_invoice_pdf(sc_id, inv_file)
                pkl_path = self.generate_packing_list_pdf(sc_id, pkl_file)

                generated_files.append({
                    "scenario_id": sc_id,
                    "title": sc["title"],
                    "category": sc["category"],
                    "invoice_filename": inv_file,
                    "invoice_path": inv_path,
                    "packing_list_filename": pkl_file,
                    "packing_list_path": pkl_path,
                })

        return generated_files


if __name__ == "__main__":
    generator = DocumentPDFGenerator()
    files = generator.generate_all_samples()
    print(f"Sucesso! Gerados {len(files) * 2} documentos PDF em {generator.output_dir}:")
    for f in files:
        print(f" - {f['invoice_filename']} & {f['packing_list_filename']} ({f['title']})")
