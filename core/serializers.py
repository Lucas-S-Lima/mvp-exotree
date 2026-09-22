"""Serializers para a API REST (Django REST Framework)."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import ExoplanetCandidate, ModelRun, PredictionResult
from pipeline.constants import FEATURE_NAMES

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


class ExoplanetCandidateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = ExoplanetCandidate
        fields = [
            "id",
            "name",
            "user",
            "orbital_period_days",
            "transit_duration_hours",
            "transit_depth_ppm",
            "planet_radius_earth",
            "insolation_flux_earth",
            "equilibrium_temperature_k",
            "impact_parameter",
            "transit_signal_to_noise",
            "stellar_effective_temperature_k",
            "stellar_surface_gravity",
            "stellar_radius_solar",
            "kepler_magnitude",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class DirectPredictInputSerializer(serializers.Serializer):
    """Valida as 12 variáveis de entrada para predição direta."""

    orbital_period_days = serializers.FloatField(min_value=0.0)
    transit_duration_hours = serializers.FloatField(min_value=0.0)
    transit_depth_ppm = serializers.FloatField(min_value=0.0)
    planet_radius_earth = serializers.FloatField(min_value=0.0)
    insolation_flux_earth = serializers.FloatField(min_value=0.0)
    equilibrium_temperature_k = serializers.FloatField(min_value=0.0)
    impact_parameter = serializers.FloatField(min_value=0.0)
    transit_signal_to_noise = serializers.FloatField(min_value=0.0)
    stellar_effective_temperature_k = serializers.FloatField(min_value=0.0)
    stellar_surface_gravity = serializers.FloatField()
    stellar_radius_solar = serializers.FloatField(min_value=0.0)
    kepler_magnitude = serializers.FloatField()


class PredictionResultSerializer(serializers.ModelSerializer):
    candidate_id = serializers.ReadOnlyField(source="candidate.id")
    candidate_name = serializers.ReadOnlyField(source="candidate.name")

    class Meta:
        model = PredictionResult
        fields = [
            "id",
            "candidate_id",
            "candidate_name",
            "label",
            "is_exoplanet",
            "probability",
            "confidence",
            "modelrun",
            "created_at",
        ]


class ModelRunSerializer(serializers.ModelSerializer):
    algorithm_name = serializers.ReadOnlyField(source="algorithm.algorithm")

    class Meta:
        model = ModelRun
        fields = [
            "id",
            "algorithm_name",
            "trained_at",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "true_positive",
            "true_negative",
            "false_positive",
            "false_negative",
            "hyperparameters",
            "model_artifact_path",
        ]

