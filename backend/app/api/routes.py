import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from ..models.documents import ReconciliationInput
from ..models.reconciliation import ReconciliationResult, SemanticNCMAnalysis
from ..services.reconciliation import CustomsReconciliationEngine
from ..services.samples import SampleScenariosRepository
from ..services.doc_ai_parser import DocumentAIParser
from ..services.ai_analyzer import GeminiComexAnalyzer

router = APIRouter(prefix="/api", tags=["Customs Reconciliation"])

engine = CustomsReconciliationEngine()
doc_ai = DocumentAIParser()
gemini = GeminiComexAnalyzer()


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
        raise HTTPException(status_status=404, detail=f"Cenário '{scenario_id}' não encontrado.")


@router.post("/reconcile", response_model=ReconciliationResult)
async def run_reconciliation(payload: ReconciliationInput):
    """Executa a conciliação aduaneira multi-documental com semáforo de risco e IA."""
    try:
        result = await engine.reconcile(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante a conciliação: {str(e)}")


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
    extracted = await doc_ai.parse_invoice_pdf(content, file.filename or "uploaded_invoice.pdf")
    return extracted
