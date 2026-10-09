#!/usr/bin/env bash
# ==============================================================================
# Script de Deploy Direto para o Google Cloud Run
# Microsserviço de Conciliação Aduaneira Comexport (Gemini 3.8 Flash)
# ==============================================================================

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "seu-projeto-gcp")
REGION="southamerica-east1"
SERVICE_NAME="comexport-reconciliation"

echo "======================================================================"
echo "Iniciando Deploy do Microsserviço Comexport no Google Cloud Run"
echo "Projeto GCP: $PROJECT_ID"
echo "Região:      $REGION"
echo "Serviço:     $SERVICE_NAME"
echo "Modelo IA:   gemini-3.8-flash"
echo "======================================================================"

# Submissão de build e deploy direto via Cloud Build
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL="gemini-3.8-flash"

echo "Deploy concluído com sucesso!"
