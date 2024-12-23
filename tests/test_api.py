import pytest
import httpx

BASE_URL = "http://localhost:8000/api"

@pytest.mark.asyncio
async def test_create_series():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/series", json={"name": "test-series"})
        assert response.status_code == 200
        assert response.json()["name"] == "test-series"

@pytest.mark.asyncio
async def test_get_series():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/series")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_upload_document():
    series_id = "test-series"
    async with httpx.AsyncClient() as client:
        files = {'file': ('test.pdf', b'%PDF-1.4 test content', 'application/pdf')}
        response = await client.post(f"{BASE_URL}/series/{series_id}/documents", files=files)
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_documents():
    series_id = "test-series"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/series/{series_id}/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list) 