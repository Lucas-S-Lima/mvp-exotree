"""Views e endpoints REST da aplicação mvp-exo."""

import logging
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import Algorithm, ExoplanetCandidate, ModelRun, PredictionResult
from core.serializers import (
    DirectPredictInputSerializer,
    ExoplanetCandidateSerializer,
    ModelRunSerializer,
    PredictionResultSerializer,
    UserRegistrationSerializer,
)
from pipeline.constants import FEATURE_NAMES
from pipeline.inference import ExoplanetRFPredictor

logger = logging.getLogger(__name__)
User = get_user_model()

# Instância de inferência com caminhos do Django settings
rf_predictor = ExoplanetRFPredictor(
    model_path=getattr(settings, "RF_MODEL_PATH", "artifacts/rf_model.joblib"),
    scaler_path=getattr(settings, "SCALER_PATH", "artifacts/scaler.joblib"),
)


# ==============================================================================
# Autenticação
# ==============================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """Registra um novo usuário astrônomo."""
    serializer = UserRegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "User registered successfully",
            "username": user.username,
            "email": user.email,
            "token": token.key,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def obtain_token(request):
    """Obtém o token de autenticação via e-mail e senha."""
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"message": "E-mail e senha são obrigatórios."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(email=email).first()
    if user is None or not user.check_password(password):
        return Response(
            {"message": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    """Invalida o token antigo e gera uma nova chave de acesso."""
    old_key = request.data.get("token")
    if not old_key:
        return Response(
            {"message": "Token é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_obj = Token.objects.filter(key=old_key).first()
    if token_obj is None:
        return Response(
            {"message": "Invalid token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = token_obj.user
    token_obj.delete()

    new_token = Token.objects.create(user=user)
    return Response({"token": new_token.key}, status=status.HTTP_200_OK)


# ==============================================================================
# Candidatos a Exoplanetas (CRUD)
# ==============================================================================

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def exoplanets_list_create(request):
    """Lista todos os candidatos do usuário autenticado ou cadastra um novo."""
    if request.method == "GET":
        candidates = ExoplanetCandidate.objects.filter(user=request.user)
        serializer = ExoplanetCandidateSerializer(candidates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = ExoplanetCandidateSerializer(data=request.data)
        if serializer.is_valid():
            candidate = serializer.save(user=request.user)
            return Response(
                ExoplanetCandidateSerializer(candidate).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def exoplanet_detail(request, pk):
    """Recupera, atualiza ou remove um candidato específico do usuário autenticado."""
    candidate = get_object_or_404(ExoplanetCandidate, id=pk, user=request.user)

    if request.method == "GET":
        serializer = ExoplanetCandidateSerializer(candidate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method in ["PUT", "PATCH"]:
        serializer = ExoplanetCandidateSerializer(
            candidate,
            data=request.data,
            partial=(request.method == "PATCH"),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        candidate.delete()
        return Response(
            {"message": "Candidato removido com sucesso."},
            status=status.HTTP_204_NO_CONTENT,
        )


# ==============================================================================
# Predição com Random Forest
# ==============================================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def predict_candidate_view(request, pk):
    """Classifica um candidato cadastrado utilizando o modelo Random Forest."""
    candidate = get_object_or_404(ExoplanetCandidate, id=pk, user=request.user)

    features = {feat: getattr(candidate, feat) for feat in FEATURE_NAMES}

    try:
        prediction = rf_predictor.predict(features)
    except Exception as exc:
        logger.error("Erro na inferência: %s", exc)
        return Response(
            {"message": f"Erro na classificação: {str(exc)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Buscar última execução do modelo registrada
    latest_run = ModelRun.objects.order_by("-trained_at").first()

    pred_record = PredictionResult.objects.create(
        candidate=candidate,
        modelrun=latest_run,
        label=prediction["label"],
        is_exoplanet=prediction["is_exoplanet"],
        probability=Decimal(f"{prediction['probability_confirmed']:.4f}"),
        confidence=Decimal(f"{prediction['confidence']:.4f}"),
    )

    return Response(
        {
            "prediction_id": pred_record.id,
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "label": prediction["label"],
            "is_exoplanet": prediction["is_exoplanet"],
            "probability_confirmed": prediction["probability_confirmed"],
            "probability_false_positive": prediction["probability_false_positive"],
            "confidence": prediction["confidence"],
            "algorithm": "Random Forest",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def predict_direct_view(request):
    """Classifica diretamente um exoplaneta a partir de payload JSON com 12 features."""
    serializer = DirectPredictInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        prediction = rf_predictor.predict(serializer.validated_data)
    except Exception as exc:
        logger.error("Erro na inferência direta: %s", exc)
        return Response(
            {"message": f"Erro na classificação: {str(exc)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "label": prediction["label"],
            "is_exoplanet": prediction["is_exoplanet"],
            "probability_confirmed": prediction["probability_confirmed"],
            "probability_false_positive": prediction["probability_false_positive"],
            "confidence": prediction["confidence"],
            "algorithm": "Random Forest",
        },
        status=status.HTTP_200_OK,
    )


# ==============================================================================
# Métricas do Modelo Random Forest
# ==============================================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def model_metrics_view(request):
    """Retorna as métricas vigentes do modelo Random Forest em produção."""
    latest_run = ModelRun.objects.order_by("-trained_at").first()

    if latest_run:
        data = ModelRunSerializer(latest_run).data
        return Response(data, status=status.HTTP_200_OK)

    # Caso ainda não haja execução gravada no banco, retornar info do artefato
    return Response(
        {
            "algorithm": "Random Forest",
            "status": "ready",
            "message": "Modelo pronto e carregado. Nenhuma execução registrada na base de dados.",
        },
        status=status.HTTP_200_OK,
    )

