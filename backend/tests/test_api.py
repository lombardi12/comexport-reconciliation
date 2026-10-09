import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.anyio
async def test_api_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "gemini" in data["ai_model"].lower()


@pytest.mark.anyio
async def test_api_list_scenarios():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) == 8
    assert any(s["id"] == "byd_ev_shipment" for s in scenarios)
    assert any(s["id"] == "aviation_turbine_gulfstream" for s in scenarios)
    assert any(s["id"] == "steel_coils_stainless" for s in scenarios)


@pytest.mark.anyio
async def test_api_reconcile_byd_scenario():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        scenario_resp = await ac.get("/api/scenarios/byd_ev_shipment")
        assert scenario_resp.status_code == 200
        payload = scenario_resp.json()

        reconcile_resp = await ac.post("/api/reconcile", json=payload)
        assert reconcile_resp.status_code == 200
        result = reconcile_resp.json()
        assert result["duimp_approved"] is True
        assert result["summary"]["risk_channel"] == "VERDE"


@pytest.mark.anyio
async def test_api_batch_reconciliation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/batch-reconciliation")
    assert response.status_code == 200
    data = response.json()
    assert "batch_summary" in data
    assert data["batch_summary"]["total_shipments_audited"] == 8
    assert data["batch_summary"]["green_channel_count"] >= 3
    assert data["batch_summary"]["red_channel_count"] >= 3
    assert data["batch_summary"]["total_penalties_avoided_brl"] > 100_000.0
    assert len(data["shipments"]) == 8


@pytest.mark.anyio
async def test_api_sample_files_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/sample-files")
    assert response.status_code == 200
    files = response.json()
    assert len(files) >= 8
    assert any(f["filename"] == "INV_BYD_9921.pdf" for f in files)


@pytest.mark.anyio
async def test_api_upload_and_reconcile_pdf():
    pdf_path = os.path.join(os.getcwd(), "samples", "documents", "INV_BYD_9921.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("PDF de teste ainda não gerado")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"invoice_file": ("INV_BYD_9921.pdf", pdf_bytes, "application/pdf")}
        response = await ac.post("/api/upload-and-reconcile", files=files)

    assert response.status_code == 200
    result = response.json()
    assert "document_ai_metadata" in result
    assert "reconciliation_result" in result
    assert result["reconciliation_result"]["summary"]["risk_channel"] == "VERDE"
