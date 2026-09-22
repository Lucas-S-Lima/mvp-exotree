"""Módulo de inferência e predição com o modelo Random Forest treinado."""

import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from pipeline.constants import (
    FEATURE_NAMES,
    LOG_TRANSFORM_COLUMNS,
    REVERSE_LABEL_MAP,
)

logger = logging.getLogger(__name__)


class ExoplanetRFPredictor:
    """Motor de inferência singleton para o modelo Random Forest."""

    _instance = None
    _model: RandomForestClassifier | None = None
    _scaler: StandardScaler | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        model_path: str | Path = "artifacts/rf_model.joblib",
        scaler_path: str | Path = "artifacts/scaler.joblib",
    ):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)

    def load_artifacts(self, force_reload: bool = False):
        """Carrega os artefatos de modelo e scaler em memória."""
        if self._model is None or self._scaler is None or force_reload:
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Modelo não encontrado em: {self.model_path}. Execute o treino antes de inferir."
                )
            if not self.scaler_path.exists():
                raise FileNotFoundError(
                    f"Scaler não encontrado em: {self.scaler_path}. Execute o pré-processamento antes de inferir."
                )

            self._model = joblib.load(self.model_path)
            self._scaler = joblib.load(self.scaler_path)
            logger.info("Artefatos de Random Forest e Scaler carregados com sucesso.")

    def preprocess_input(self, features_dict: dict) -> np.ndarray:
        """Valida, transforma com log e padroniza as features de entrada."""
        # Verificar se todas as 12 features estão presentes
        missing = [f for f in FEATURE_NAMES if f not in features_dict]
        if missing:
            raise ValueError(f"Features ausentes no payload de entrada: {missing}")

        # Montar DataFrame ordenado
        df = pd.DataFrame([{f: float(features_dict[f]) for f in FEATURE_NAMES}])

        # Log transform
        df[LOG_TRANSFORM_COLUMNS] = np.log1p(df[LOG_TRANSFORM_COLUMNS])

        # Standard Scaler
        scaled = self._scaler.transform(df)
        return scaled

    def predict(self, features_dict: dict) -> dict:
        """Executa a predição para um conjunto de atributos de candidato."""
        self.load_artifacts()

        scaled_features = self.preprocess_input(features_dict)
        pred_class = int(self._model.predict(scaled_features)[0])
        probabilities = self._model.predict_proba(scaled_features)[0]

        prob_confirmed = float(probabilities[0])
        prob_false_positive = float(probabilities[1])
        label_str = REVERSE_LABEL_MAP.get(pred_class, "UNKNOWN")

        return {
            "prediction_class": pred_class,
            "label": label_str,
            "is_exoplanet": bool(pred_class == 0),
            "probability_confirmed": prob_confirmed,
            "probability_false_positive": prob_false_positive,
            "confidence": float(max(probabilities)),
        }


# Instância padrão para conveniência
default_predictor = ExoplanetRFPredictor()


def predict_candidate(features_dict: dict, predictor: ExoplanetRFPredictor | None = None) -> dict:
    """Função utilitária direta para prever a classificação de um exoplaneta."""
    predictor = predictor or default_predictor
    return predictor.predict(features_dict)

