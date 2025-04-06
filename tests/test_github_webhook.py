from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_github_webhook():
    response = client.post("/api/v1/webhook", json={
        "action": "opened",
        "repository": {"name": "test"},
        "sender": {"login": "testuser"},
        "installation": {
            "id": 1234567890,
            "account": {
                "login": "testuser",
                "id": 1234567890
            }
        }
    })
    assert response.status_code == 200
    assert response.json() == {"status": "Event processed successfully"}
