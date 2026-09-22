from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import Algorithm, ExoplanetCandidate, ModelRun, PredictionResult, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "is_staff", "is_active", "date_joined"]
    search_fields = ["username", "email"]


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ["algorithm"]


@admin.register(ModelRun)
class ModelRunAdmin(admin.ModelAdmin):
    list_display = [
        "algorithm",
        "trained_at",
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "model_artifact_path",
    ]
    list_filter = ["trained_at"]


@admin.register(ExoplanetCandidate)
class ExoplanetCandidateAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "orbital_period_days",
        "transit_duration_hours",
        "transit_depth_ppm",
        "planet_radius_earth",
        "created_at",
    ]
    search_fields = ["name", "user__username"]
    list_filter = ["created_at"]


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = [
        "candidate",
        "label",
        "is_exoplanet",
        "probability",
        "confidence",
        "modelrun",
        "created_at",
    ]
    list_filter = ["label", "is_exoplanet", "created_at"]

