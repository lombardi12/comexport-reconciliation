import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .api.routes import router as api_router

app = FastAPI(
    title="Comexport - Customs Reconciliation Service",
    description=(
        "Microsserviço de Conciliação Aduaneira 5PL integrado com Google Gemini 3.8 Flash "
        "e Google Cloud Document AI para validação prévia de DUIMP, faturas e romaneios."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui rotas da API
app.include_router(api_router)

# Monta arquivos estáticos do Frontend
static_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def serve_index():
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend static files directory found, but index.html is missing."}
else:
    @app.get("/")
    async def serve_fallback():
        return {
            "service": "Comexport Customs Reconciliation Microservice",
            "docs": "/docs",
            "status": "online"
        }
