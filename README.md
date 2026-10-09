# 🚢 Comexport - Microsserviço de Conciliação Aduaneira Inteligente
### Powered by Google Cloud • Gemini 3.8 Flash & Document AI

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Google Gemini 3.8 Flash](https://img.shields.io/badge/Google%20AI-Gemini%203.8%20Flash-4285F4.svg)](https://cloud.google.com/vertex-ai)
[![Google Cloud Run](https://img.shields.io/badge/GCP-Cloud%20Run%20Ready-EA4335.svg)](https://cloud.google.com/run)
[![Tests](https://img.shields.io/badge/tests-9%20passed-brightgreen.svg)]()

Protótipo full-stack desenvolvido sob a ótica de orquestração logística **5PL da Comexport**, demonstrando como a plataforma **Google Cloud** e o ecossistema **Antigravity** resolvem de ponta a ponta o maior gargalo operacional do comércio exterior: **a validação e pré-parametrização da DUIMP (Declaração Única de Importação)** antes do registro no Siscomex.

---

## 📌 Contexto & Por que este projeto é estratégico para a Comexport?

Como a maior empresa de comércio exterior do Brasil e líder 5PL na cadeia automotiva (BYD, GWM, Polo Automotivo do Ceará - PACE), aviação executiva e fertilizantes, a Comexport gerencia milhares de processos simultâneos.

1. **Transição Regulatória DUIMP / Portal Único Siscomex (2025/2026):**
   A Receita Federal está descontinuando a antiga DI e exigindo o preenchimento da DUIMP baseado no **Catálogo de Produtos**. Erros de NCM ou atributos agora bloqueiam o despacho em malhas fiscais automáticas.
2. **Mitigação de Custos Ocultos (Demurrage & Armazenagem):**
   Um contêiner retido em Canal Vermelho gera custos portuários de **US$ 150 a US$ 400/dia**.
3. **Riscos de Multas Pesadas:**
   - Erro de classificação de NCM: **1% do valor aduaneiro** (mínimo de R$ 500,00).
   - Inexatidão cadastral: penalidades de R$ 1.000,00 por declaração.

---

## 🧠 Arquitetura de Inteligência Artificial

```
                      +-----------------------------------+
                      |   Google Cloud Document AI        |
                      |  (Invoice Parser v2 / OCR Vision) |
                      +-----------------+-----------------+
                                        | (Entidades Extraídas)
                                        v
+------------------+         +--------------------+         +--------------------+
| Commercial       |         | Packing List       |         | Rascunho DUIMP     |
| Invoice          |         | (Pesos e Volumes)  |         | (Siscomex / PTAX)  |
+--------+---------+         +---------+----------+         +---------+----------+
         |                             |                              |
         +-----------------------------+------------------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |   Motor de Conciliação Aduaneira    |
                    | (Regras Fiscais Brasileiras / PTAX) |
                    +------------------+------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |       GEMINI 3.8 FLASH              |
                    |  - Validação Semântica de NCM       |
                    |  - Diagnóstico Executivo & Risco    |
                    +------------------+------------------+
                                       |
                                       v
                    +-------------------------------------+
                    | Dashboard Operacional Interativo    |
                    | (Canal Verde / Amarelo / Vermelho)  |
                    +-------------------------------------+
```

### Onde a IA atua:
1. **Google Cloud Document AI:** Extrai dados de faturas estrangeiras e romaneios em PDF sem depender de templates rígidos.
2. **Gemini 3.8 Flash (Classificação Semântica de NCM):** Avalia se a descrição em inglês do fabricante no exterior (ex: *"Prilled Urea 46%"*) coincide tecnicamente com o enquadramento fiscal declarado na DUIMP (ex: NCM *3102.10.10* vs erro para *3103.19.00*).
3. **Gemini 3.8 Flash (Parecer Executivo Explicável):** Gera sínteses em linguagem natural para os analistas e gerentes da Comexport com alertas de multas e ações imediatas.

---

## 🎯 Cenários de Demonstração Pré-Carregados

O protótipo vem com 3 operações reais pré-configuradas para a apresentação:

| Cenário | Cliente / Operação | Desfecho | Diagnóstico |
|---|---|---|---|
| **1. Lote BYD Eletromobilidade** | BYD Auto do Brasil / Porto de Vitória | 🟢 **Canal Verde (99.4%)** | 120 veículos elétricos (Dolphin & Seal). Faturas, Incoterm CIF, frete e NCM 8703.80.00 100% conciliados. Aprovado para registro imediato. |
| **2. Insumos Agrícolas** | Kalium Chemical / Comexport Agro | 🔴 **Canal Vermelho (30.0%)** | Carga de Ureia com NCM preenchida incorretamente como Superfosfatos (3103.19.00) e estouro de peso de 9.1% (460 toneladas). Multa evitada: **R$ 84.475,00**. |
| **3. Polo Automotivo PACE** | PACE Ceará / Porto do Pecém | 🟡 **Canal Amarelo (76.0%)** | Importação de sistemas ABS/ESP sob FOB. Divergência na PTAX e omissão de seguro aduaneiro. Alerta preventivo para ajuste contábil. |

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.11+
- Virtualenv ativo

```bash
# 1. Clonar o repositório
git clone https://github.com/lombardi12/comexport-reconciliation.git
cd comexport-reconciliation

# 2. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependências
pip install -r backend/requirements.txt

# 4. Iniciar o servidor com a interface web
PYTHONPATH=backend uvicorn backend.app.main:app --reload --port 8000
```

Abra seu navegador em:
- **Dashboard Operacional:** `http://localhost:8000`
- **Documentação Interativa Swagger:** `http://localhost:8000/docs`

---

## 🧪 Executando os Testes Automatizados

O projeto conta com suíte completa de testes unitários e de integração testando a integridade das regras da Receita Federal e a resposta do modelo Gemini 3.8 Flash:

```bash
PYTHONPATH=backend pytest -v backend/tests
```

**Resultado:**
```text
backend/tests/test_api.py::test_api_health_endpoint[asyncio] PASSED
backend/tests/test_api.py::test_api_list_scenarios[asyncio] PASSED
backend/tests/test_api.py::test_api_reconcile_byd_scenario[asyncio] PASSED
backend/tests/test_api.py::test_api_semantic_ncm_check[asyncio] PASSED
backend/tests/test_reconciliation.py::test_byd_scenario_approves_green_channel[asyncio] PASSED
backend/tests/test_reconciliation.py::test_chemical_scenario_blocks_red_channel[asyncio] PASSED
backend/tests/test_reconciliation.py::test_pace_scenario_flags_yellow_channel[asyncio] PASSED
backend/tests/test_reconciliation.py::test_tax_calculator_customs_value PASSED
backend/tests/test_reconciliation.py::test_tax_calculator_penalty_estimation PASSED
============================== 9 passed in 0.22s ===============================
```

---

## ☁️ Deploy no Google Cloud Run

O serviço é nativamente stateless e preparado para contêinerização e escalabilidade serverless no Google Cloud:

```bash
# Deploy automatizado via Cloud Build
gcloud run deploy comexport-reconciliation \
  --source . \
  --region southamerica-east1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL=gemini-3.8-flash
```

---

## 🎤 Roteiro Sugerido para a Demonstração com a Equipe Técnica

1. **Abertura (2 min):** Contextualizar os desafios da Comexport com o Catálogo de Produtos da DUIMP 2026 e o custo de um Canal Vermelho/demurrage em operações de grande porte como BYD.
2. **Cenário 1 - BYD (Canal Verde) (3 min):**
   - Mostrar os documentos extraídos na coluna esquerda.
   - Clicar em "Conciliar com Gemini 3.8 Flash".
   - Destacar o semáforo verde, a acurácia semântica de 98.5% na NCM e o parecer executivo liberando o lote para desembaraço no Porto de Vitória.
3. **Cenário 2 - Químicos (Canal Vermelho) (4 min):**
   - Alternar para o cenário de Fertilizantes.
   - Mostrar a detecção do erro de peso (+460 toneladas) e o alerta do Gemini 3.8 Flash identificando que Ureia (adubo nitrogenado) não pode receber NCM de superfosfatos (adubo fosfatado).
   - Mostrar o cálculo da penalidade de R$ 84.475,00 evitada pelo sistema.
4. **Cenário 3 - PACE Ceará (Canal Amarelo) (2 min):**
   - Mostrar a flexibilidade do semáforo com tolerâncias de PTAX e seguro.
5. **Arquitetura Google Cloud & Antigravity (4 min):**
   - Mostrar como a solução roda de forma desacoplada via Cloud Run, conectando-se ao ERP atual (CMS) via API REST simples.
