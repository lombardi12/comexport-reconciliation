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
    assert len(scenarios) == 3
    assert any(s["id"] == "byd_ev_shipment" for s in scenarios)


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
async def test_api_semantic_ncm_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "sku": "EV-BATTERY-MODULE",
            "international_description": "Lithium Iron Phosphate Battery Pack 150Ah for EV",
            "declared_ncm": "8507.60.00",
            "declared_description": "Acumuladores elétricos de íon de lítio"
        }
        response = await ac.post("/api/semantic-check", json=payload)
        assert response.status_code == 200
        result = response.json()
        assert result["semantic_match"] is True
        assert result["confidence_score_pct"] > 80.0
