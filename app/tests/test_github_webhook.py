from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_github_webhook():
    response = client.post("/webhook/", json={"action": "opened", "repository": {"name": "test"}})
    assert response.status_code == 200
    assert response.json() == {"status": "Event processed successfully"}
