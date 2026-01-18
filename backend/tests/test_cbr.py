"""Tests for CBR integration in estimate endpoint."""

from unittest.mock import patch

import pytest


def test_estimate_includes_similar_cases(client):
    """POST /estimate response includes similar_cases array."""
    response = client.post(
        "/estimate",
        json={"sqft": 1500, "category": "Bardeaux"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "similar_cases" in data
    assert isinstance(data["similar_cases"], list)


def test_similar_case_structure(client):
    """Each similar case has required fields."""
    # Mock Pinecone to return predictable data
    mock_cases = [
        {
            "case_id": "123",
            "similarity": 0.95,
            "category": "Bardeaux",
            "sqft": 1400.0,
            "total": 15000.0,
            "per_sqft": 10.71,
            "year": 2023
        }
    ]

    # Patch where the function is imported (in the router module)
    with patch("backend.app.routers.estimate.query_similar_cases", return_value=mock_cases):
        response = client.post(
            "/estimate",
            json={"sqft": 1500, "category": "Bardeaux"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["similar_cases"]) == 1

        case = data["similar_cases"][0]
        assert case["case_id"] == "123"
        assert case["similarity"] == 0.95
        assert case["category"] == "Bardeaux"
        assert case["sqft"] == 1400.0
        assert case["total"] == 15000.0


def test_estimate_works_without_pinecone(client):
    """Estimate still works when Pinecone is not configured."""
    # query_similar_cases returns empty list when not initialized
    with patch("backend.app.routers.estimate.query_similar_cases", return_value=[]):
        response = client.post(
            "/estimate",
            json={"sqft": 2000, "category": "Bardeaux"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "estimate" in data
        assert data["similar_cases"] == []


def test_build_query_text():
    """Query text built correctly from inputs."""
    from backend.app.services.embeddings import build_query_text

    text = build_query_text(
        sqft=1500,
        category="Bardeaux",
        complexity=15,
        material_lines=10,
        labor_lines=3
    )
    assert "Toiture Bardeaux" in text
    assert "1500" in text
    assert "complexite 15" in text
    assert "10 lignes materiaux" in text
    assert "3 lignes main-d'oeuvre" in text


def test_build_query_text_minimal():
    """Query text handles minimal inputs."""
    from backend.app.services.embeddings import build_query_text

    text = build_query_text(
        sqft=1000,
        category="Elastomere",
        complexity=10
    )
    assert "Toiture Elastomere" in text
    assert "1000" in text
    assert "complexite 10" in text
    # Should not have material/labor lines without values
    assert "lignes materiaux" not in text


def test_embedding_model_generates_correct_dimensions(client):
    """Embedding model outputs 384-dim vectors."""
    from backend.app.services.embeddings import generate_query_embedding

    # Model should be loaded by app lifespan
    try:
        embedding = generate_query_embedding("Test roofing job")
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
    except RuntimeError:
        # Model not loaded in test environment - skip
        pytest.skip("Embedding model not loaded")
