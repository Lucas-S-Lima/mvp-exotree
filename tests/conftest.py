import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import ExoplanetCandidate

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="kepler_astronomer",
        email="kepler@nasa.gov",
        password="secure_password123",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="tess_astronomer",
        email="tess@nasa.gov",
        password="secure_password123",
    )


@pytest.fixture
def auth_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def candidate_payload():
    return {
        "name": "Kepler-Test-Candidate",
        "orbital_period_days": 9.4880,
        "transit_duration_hours": 2.9575,
        "transit_depth_ppm": 615.8,
        "planet_radius_earth": 2.26,
        "insolation_flux_earth": 93.59,
        "equilibrium_temperature_k": 793.0,
        "impact_parameter": 0.146,
        "transit_signal_to_noise": 35.8,
        "stellar_effective_temperature_k": 5455.0,
        "stellar_surface_gravity": 4.467,
        "stellar_radius_solar": 0.927,
        "kepler_magnitude": 15.347,
    }


@pytest.fixture
def candidate_instance(db, user, candidate_payload):
    return ExoplanetCandidate.objects.create(user=user, **candidate_payload)

