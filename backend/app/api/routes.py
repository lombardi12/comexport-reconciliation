import os
import glob
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ..models.documents import ReconciliationInput, CommercialInvoice, PackingList
from ..models.reconciliation import ReconciliationResult, SemanticNCMAnalysis
from ..services.reconciliation import CustomsReconciliationEngine
from ..services.samples import SampleScenariosRepository
from ..services.doc_ai_parser import DocumentAIParser
from ..services.ai_analyzer import GeminiComexAnalyzer
from ..services.document_generator import DocumentPDFGenerator

router = APIRouter(prefix="/api", tags=["Customs Reconciliation"])

engine = CustomsReconciliationEngine()
doc_ai = DocumentAIParser()
gemini = GeminiComexAnalyzer()
pdf_generator = DocumentPDFGenerator()


class SemanticCheckRequest(BaseModel):
    sku: str = Field(default="AUTO-PART-01")
    international_description: str = Field(..., description="Descrição comercial em inglês/chinês")
    declared_ncm: str = Field(..., description="NCM declarada (8 dígitos)")
    declared_description: str = Field(..., description="Descrição conforme catálogo RFB")


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Comexport Customs Reconciliation Engine",
        "version": "1.0.0",
        "ai_model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "doc_ai_status": "READY",
        "supported_modals": ["MARITIMO", "AEREO", "RODOVIARIO"]
    }


@router.get("/scenarios")
async def list_scenarios():
    """Retorna a lista de cenários pré-configurados para demonstração."""
    return SampleScenariosRepository.get_all_scenarios()


@router.get("/scenarios/{scenario_id}", response_model=ReconciliationInput)
async def get_scenario(scenario_id: str):
    """Retorna os dados completos de um cenário selecionado."""
    try:
        return SampleScenariosRepository.get_scenario(scenario_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Cenário '{scenario_id}' não encontrado.")


@router.post("/reconcile", response_model=ReconciliationResult)
async def run_reconciliation(payload: ReconciliationInput):
    """Executa a conciliação aduaneira multi-documental com semáforo de risco e IA."""
    try:
        result = await engine.reconcile(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar conciliação: {str(e)}")


@router.post("/semantic-check", response_model=SemanticNCMAnalysis)
async def check_semantic_ncm(payload: SemanticCheckRequest):
    """Endpoint direto para testar a equivalência semântica de NCM com Gemini 3.8 Flash."""
    try:
        result = await gemini.evaluate_ncm_semantics(
            sku=payload.sku,
            international_desc=payload.international_description,
            declared_ncm=payload.declared_ncm,
            declared_desc=payload.declared_description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise semântica: {str(e)}")


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Recebe um PDF de fatura ou romaneio e aciona a extração via Google Cloud Document AI."""
    content = await file.read()
    filename = file.filename or "uploaded_invoice.pdf"
    if "pkl" in filename.lower() or "pack" in filename.lower() or "romaneio" in filename.lower():
        extracted = await doc_ai.parse_packing_list_pdf(content, filename)
    else:
        extracted = await doc_ai.parse_invoice_pdf(content, filename)
    return extracted


@router.post("/upload-and-reconcile")
async def upload_and_reconcile(
    invoice_file: UploadFile = File(...),
    packing_list_file: Optional[UploadFile] = File(None)
):
    """
    Endpoint de Ingestão em Tempo Real:
    Recebe PDF(s) de Fatura Comercial (e opcionalmente Packing List),
    processa via Google Cloud Document AI, cruza com a DUIMP correspondente e executa
    a conciliação com o Gemini 3.8 Flash em um único pipeline.
    """
    try:
        inv_content = await invoice_file.read()
        inv_filename = invoice_file.filename or "uploaded_invoice.pdf"
        inv_parsed = await doc_ai.parse_invoice_pdf(inv_content, inv_filename)

        scenario_id = inv_parsed.get("matched_scenario_id", "byd_ev_shipment")
        scenario = SampleScenariosRepository.get_scenario(scenario_id)

        # Atualiza a Invoice a partir do Document AI se disponível
        invoice_obj = scenario.invoice
        if "parsed_invoice" in inv_parsed:
            try:
                invoice_obj = CommercialInvoice(**inv_parsed["parsed_invoice"])
            except Exception:
                pass

        # Se enviou packing list separado, processa
        packing_list_obj = scenario.packing_list
        pkl_parsed = None
        if packing_list_file:
            pkl_content = await packing_list_file.read()
            pkl_filename = packing_list_file.filename or "uploaded_packing_list.pdf"
            pkl_parsed = await doc_ai.parse_packing_list_pdf(pkl_content, pkl_filename)
            if "parsed_packing_list" in pkl_parsed:
                try:
                    packing_list_obj = PackingList(**pkl_parsed["parsed_packing_list"])
                except Exception:
                    pass

        reconciliation_input = ReconciliationInput(
            scenario_id=f"upload_{scenario_id}",
            invoice=invoice_obj,
            packing_list=packing_list_obj,
            duimp=scenario.duimp,
            reference_ptax=scenario.reference_ptax,
            weight_tolerance_pct=scenario.weight_tolerance_pct
        )

        reconciliation_result = await engine.reconcile(reconciliation_input)

        return {
            "document_ai_metadata": {
                "invoice_extraction": inv_parsed,
                "packing_list_extraction": pkl_parsed,
                "status": "PROCESSED_SUCCESSFULLY"
            },
            "reconciliation_result": reconciliation_result,
            "reconciliation_input": reconciliation_input
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no pipeline de upload e conciliação: {str(e)}")


@router.get("/sample-files")
async def list_sample_files():
    """Retorna os arquivos PDF disponíveis na biblioteca de amostras para teste."""
    samples_dir = pdf_generator.output_dir
    files = []
    if os.path.exists(samples_dir):
        for f in sorted(os.listdir(samples_dir)):
            if f.endswith(".pdf"):
                file_path = os.path.join(samples_dir, f)
                file_size = os.path.getsize(file_path)
                doc_type = "Commercial Invoice" if f.startswith("INV_") else "Packing List"
                files.append({
                    "filename": f,
                    "doc_type": doc_type,
                    "size_bytes": file_size,
                    "download_url": f"/api/sample-files/download/{f}"
                })
    return files


@router.get("/sample-files/download/{filename}")
async def download_sample_file(filename: str):
    """Permite baixar o arquivo PDF de amostra para simular o drag and drop na interface."""
    samples_dir = pdf_generator.output_dir
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(samples_dir, safe_filename)

    if not os.path.exists(file_path):
        # Tenta no fallback project root samples/documents
        fallback_path = os.path.join(os.getcwd(), "samples", "documents", safe_filename)
        if os.path.exists(fallback_path):
            file_path = fallback_path
        else:
            raise HTTPException(status_code=404, detail="Arquivo de amostra não encontrado.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_filename
    )


@router.get("/batch-reconciliation")
async def run_batch_reconciliation():
    """
    Executa a conciliação em lote de todos os 8 cenários pré-configurados simultaneamente,
    retornando um panorama executivo com métricas consolidadas de multas evitadas e tempos de liberação.
    """
    all_scenarios = SampleScenariosRepository.get_all_scenarios_full()
    results = []

    total_cargo_value_usd = 0.0
    total_penalties_avoided_brl = 0.0
    channel_counts = {"VERDE": 0, "AMARELO": 0, "VERMELHO": 0}

    for sc_id, sc_input in all_scenarios.items():
        res = await engine.reconcile(sc_input)
        channel = res.summary.risk_channel
        channel_counts[channel] = channel_counts.get(channel, 0) + 1

        total_cargo_value_usd += sc_input.invoice.total_amount
        total_penalties_avoided_brl += res.summary.potential_penalty_risk_brl

        results.append({
            "scenario_id": sc_id,
            "title": next((s["title"] for s in SampleScenariosRepository.get_all_scenarios() if s["id"] == sc_id), sc_id),
            "client": sc_input.invoice.buyer_name,
            "customs_value_usd": sc_input.invoice.total_amount,
            "risk_channel": channel,
            "risk_score": res.summary.risk_score,
            "critical_issues": res.summary.critical_issues,
            "warning_issues": res.summary.warning_issues,
            "penalty_risk_brl": res.summary.potential_penalty_risk_brl,
            "ai_summary": res.summary.ai_executive_summary[:160] + "..."
        })

    return {
        "batch_summary": {
            "total_shipments_audited": len(results),
            "total_cargo_value_usd": total_cargo_value_usd,
            "total_penalties_avoided_brl": total_penalties_avoided_brl,
            "green_channel_count": channel_counts["VERDE"],
            "yellow_channel_count": channel_counts["AMARELO"],
            "red_channel_count": channel_counts["VERMELHO"],
            "average_risk_score": round(sum(r["risk_score"] for r in results) / len(results), 1),
            "estimated_demurrage_saved_days": channel_counts["VERMELHO"] * 7 + channel_counts["AMARELO"] * 2
        },
        "shipments": results
    }
