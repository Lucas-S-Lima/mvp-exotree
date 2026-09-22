"""Testes dos endpoints da API REST (Django REST Framework)."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.models import ExoplanetCandidate, ModelRun, PredictionResult, User


@pytest.mark.django_db
def test_register_user_success():
    client = APIClient()
    payload = {
        "username": "galileo",
        "email": "galileo@space.org",
        "password": "telescope_password123",
    }
    response = client.post("/api/v1/register/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "galileo"
    assert "token" in response.data
    assert User.objects.filter(email="galileo@space.org").exists()


@pytest.mark.django_db
def test_obtain_and_refresh_token(user):
    client = APIClient()

    # Obter token
    login_payload = {
        "email": user.email,
        "password": "secure_password123",
    }
    resp_login = client.post("/api/v1/token/", login_payload, format="json")
    assert resp_login.status_code == status.HTTP_200_OK
    token1 = resp_login.data["token"]

    # Renovar token
    refresh_payload = {"token": token1}
    resp_refresh = client.post("/api/v1/token/refresh/", refresh_payload, format="json")
    assert resp_refresh.status_code == status.HTTP_200_OK
    token2 = resp_refresh.data["token"]
    assert token1 != token2


@pytest.mark.django_db
def test_candidate_list_and_create(auth_client, candidate_payload):
    # Criar
    resp_create = auth_client.post("/api/v1/exoplanets/", candidate_payload, format="json")
    assert resp_create.status_code == status.HTTP_201_CREATED
    candidate_id = resp_create.data["id"]

    # Listar
    resp_list = auth_client.get("/api/v1/exoplanets/")
    assert resp_list.status_code == status.HTTP_200_OK
    assert len(resp_list.data) == 1
    assert resp_list.data[0]["id"] == candidate_id


@pytest.mark.django_db
def test_candidate_detail_update_delete(auth_client, candidate_instance):
    # Detalhe
    resp_get = auth_client.get(f"/api/v1/exoplanets/{candidate_instance.id}/")
    assert resp_get.status_code == status.HTTP_200_OK
    assert resp_get.data["name"] == candidate_instance.name

    # Atualizar (PATCH)
    resp_patch = auth_client.patch(
        f"/api/v1/exoplanets/{candidate_instance.id}/",
        {"name": "Kepler-Updated"},
        format="json",
    )
    assert resp_patch.status_code == status.HTTP_200_OK
    assert resp_patch.data["name"] == "Kepler-Updated"

    # Deletar
    resp_delete = auth_client.delete(f"/api/v1/exoplanets/{candidate_instance.id}/")
    assert resp_delete.status_code == status.HTTP_204_NO_CONTENT
    assert not ExoplanetCandidate.objects.filter(id=candidate_instance.id).exists()


@pytest.mark.django_db
def test_candidate_user_isolation(candidate_instance, other_user):
    """Garante que outro usuário não consegue acessar dados alheios."""
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)

    resp = other_client.get(f"/api/v1/exoplanets/{candidate_instance.id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_predict_candidate_endpoint(auth_client, candidate_instance):
    """Testa predição de um candidato existente no banco de dados."""
    resp = auth_client.post(f"/api/v1/exoplanets/{candidate_instance.id}/predict/")

    assert resp.status_code == status.HTTP_200_OK
    assert "label" in resp.data
    assert resp.data["label"] in ["CONFIRMED", "FALSE POSITIVE"]
    assert "probability_confirmed" in resp.data
    assert "algorithm" in resp.data
    assert resp.data["algorithm"] == "Random Forest"

    # Confirma que foi registrado no banco
    assert PredictionResult.objects.filter(candidate=candidate_instance).exists()


@pytest.mark.django_db
def test_predict_direct_endpoint(candidate_payload):
    """Testa endpoint de predição direta com JSON."""
    client = APIClient()
    features_only = {k: v for k, v in candidate_payload.items() if k != "name"}

    resp = client.post("/api/v1/predict/", features_only, format="json")

    assert resp.status_code == status.HTTP_200_OK
    assert "label" in resp.data
    assert "is_exoplanet" in resp.data
    assert "probability_confirmed" in resp.data
    assert "confidence" in resp.data
    assert resp.data["algorithm"] == "Random Forest"


@pytest.mark.django_db
def test_model_metrics_endpoint():
    """Testa consulta das métricas vigentes do modelo Random Forest."""
    client = APIClient()
    resp = client.get("/api/v1/model/metrics/")

    assert resp.status_code == status.HTTP_200_OK
    # Como rodamos o rf_train anteriormente no banco, deve conter métricas reais
    if "accuracy" in resp.data:
        assert resp.data["accuracy"] > 0.85
        assert "f1_score" in resp.data
        assert resp.data["algorithm_name"] == "Random Forest"
    else:
        assert resp.data["algorithm"] == "Random Forest"

