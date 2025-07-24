import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_analyzer_endpoint():
    response = client.get("/analyzer", params={"datapath": "2_sensor_measurments/20250527_plexiglass/csv_data_2", "plot": True, "sensor_distance": 0.1})
    assert response.status_code == 200