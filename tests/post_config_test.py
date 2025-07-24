import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_post_config_endpoint():
    response = client.post("/config?name=config_5", json={"config": {}, "filter": {}})
    assert response.status_code == 200
#doesn't work