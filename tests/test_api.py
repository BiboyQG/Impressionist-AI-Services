from fastapi.testclient import TestClient
from app import create_app

app = create_app()
client = TestClient(app)

def test_generate_endpoint():
    response = client.post("/api/generate", json={"prompt": "Hello, world"})
    assert response.status_code == 200
    data = response.json()
    assert "generated_text" in data
