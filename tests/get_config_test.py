import sys
from pathlib import Path
import tomli

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_config_endpoint():
    response = client.get("/config", params={"name": "config.toml"})
    assert response.status_code == 200
    
    with open(Path(__file__).parent.parent / "config"/"config.toml", mode="rb") as f:
        config_data = tomli.load(f)
    assert response.json() == config_data