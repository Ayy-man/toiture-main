"""Tests for estimate endpoint."""


def test_estimate_valid_bardeaux(client):
    """POST /estimate with Bardeaux returns 200 with estimate, range, confidence."""
    response = client.post(
        "/estimate",
        json={"sqft": 1500, "category": "Bardeaux"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "estimate" in data
    assert "range_low" in data
    assert "range_high" in data
    assert "confidence" in data
    assert "model" in data
    assert data["confidence"] == "HIGH"
    assert "Bardeaux" in data["model"]


def test_estimate_valid_elastomere_accented(client):
    """POST /estimate with accented Elastomere returns 200."""
    response = client.post(
        "/estimate",
        json={"sqft": 2000, "category": "Élastomère"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "estimate" in data
    assert data["confidence"] == "MEDIUM"


def test_estimate_elastomere_without_accent(client):
    """POST /estimate with non-accented Elastomere is normalized correctly."""
    response = client.post(
        "/estimate",
        json={"sqft": 2000, "category": "Elastomere"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "estimate" in data
    # Should be treated as Elastomere and get MEDIUM confidence
    assert data["confidence"] == "MEDIUM"


def test_estimate_invalid_category(client):
    """POST /estimate with invalid category returns 422."""
    response = client.post(
        "/estimate",
        json={"sqft": 1500, "category": "BadCategory"},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_estimate_negative_sqft(client):
    """POST /estimate with negative sqft returns 422."""
    response = client.post(
        "/estimate",
        json={"sqft": -100, "category": "Bardeaux"},
    )
    assert response.status_code == 422


def test_estimate_missing_required(client):
    """POST /estimate without sqft returns 422."""
    response = client.post(
        "/estimate",
        json={"category": "Bardeaux"},
    )
    assert response.status_code == 422


def test_estimate_sqft_exceeds_max(client):
    """POST /estimate with sqft > 100000 returns 422."""
    response = client.post(
        "/estimate",
        json={"sqft": 150000, "category": "Bardeaux"},
    )
    assert response.status_code == 422


def test_estimate_with_optional_params(client):
    """POST /estimate with all optional params works."""
    response = client.post(
        "/estimate",
        json={
            "sqft": 3000,
            "category": "Other",
            "material_lines": 10,
            "labor_lines": 5,
            "has_subs": 1,
            "complexity": 50,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estimate"] > 0
    assert data["range_low"] < data["estimate"]
    assert data["range_high"] > data["estimate"]
