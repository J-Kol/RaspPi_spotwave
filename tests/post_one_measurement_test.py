import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_post_one_measurement_endpoint():
    response = client.post("/measurement", json={
    "name": "measurement_1",
    "config_name": "config_2.toml",
    "count": 1})

    assert response.status_code == 200