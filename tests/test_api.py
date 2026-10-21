"""API tests for the Flask prediction service.

Minimum tests:
    1. Root endpoint
    2. Health endpoint
    3. Valid prediction
    4. Invalid input
    5. Prediction response
"""

import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

from app import app  # noqa: E402


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Service running" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_valid_prediction(client):
    response = client.post(
        "/predict", json={"features": [5.1, 3.5, 1.4, 0.2]}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "prediction" in data
    assert data["class_name"] in ["setosa", "versicolor", "virginica"]


def test_prediction_response_shape(client):
    response = client.post(
        "/predict", json={"features": [6.7, 3.0, 5.2, 2.3]}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data["prediction"], int)
    assert data["features"] == [6.7, 3.0, 5.2, 2.3]


def test_invalid_input_not_json(client):
    response = client.post(
        "/predict", data="not json", content_type="text/plain"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_invalid_input_missing_features(client):
    response = client.post("/predict", json={"wrong": [1, 2, 3, 4]})
    assert response.status_code == 400
    assert "features" in response.get_json()["error"]


def test_invalid_input_wrong_length(client):
    response = client.post("/predict", json={"features": [1, 2, 3]})
    assert response.status_code == 400
    assert "exactly 4" in response.get_json()["error"]


def test_invalid_input_non_numeric(client):
    response = client.post("/predict", json={"features": [1, 2, 3, "x"]})
    assert response.status_code == 400
    assert "numeric" in response.get_json()["error"]
