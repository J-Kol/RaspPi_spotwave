from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def example_endpoint(): #to activate: test_...
    response = client.get("/example/Sam/7")
    assert response.status_code == 200
    assert response.json() == {"name": "Sam", "id": 7}