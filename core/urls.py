"""Roteamento da API do mvp-exo."""

from django.urls import path
from core import views

urlpatterns = [
    # Autenticação
    path("api/v1/register/", views.register_user, name="register_user"),
    path("api/v1/token/", views.obtain_token, name="obtain_token"),
    path("api/v1/token/refresh/", views.refresh_token, name="refresh_token"),

    # Candidatos a exoplanetas (CRUD)
    path("api/v1/exoplanets/", views.exoplanets_list_create, name="exoplanets_list_create"),
    path("api/v1/exoplanets/<int:pk>/", views.exoplanet_detail, name="exoplanet_detail"),

    # Predição com Random Forest
    path("api/v1/exoplanets/<int:pk>/predict/", views.predict_candidate_view, name="predict_candidate"),
    path("api/v1/predict/", views.predict_direct_view, name="predict_direct"),

    # Métricas do Modelo
    path("api/v1/model/metrics/", views.model_metrics_view, name="model_metrics"),
]

