"""Testes para o pipeline de machine learning (pré-processamento, treino e inferência)."""

import pytest
from sklearn.ensemble import RandomForestClassifier

from pipeline.constants import FEATURE_NAMES, LOG_TRANSFORM_COLUMNS
from pipeline.inference import ExoplanetRFPredictor, predict_candidate
from pipeline.training import compute_metrics, load_split_data, train_random_forest


def test_split_data_structure():
    """Garante que os dados divididos possuem os atributos e formatos corretos."""
    data = load_split_data("data/exoplanets_split.pkl")
    assert "x_train" in data
    assert "x_test" in data
    assert "y_train" in data
    assert "y_test" in data

    x_train = data["x_train"]
    x_test = data["x_test"]
    assert x_train.shape[1] == 12
    assert x_test.shape[1] == 12
    assert len(x_train) > len(x_test)


def test_random_forest_training_and_metrics():
    """Valida o treinamento do Random Forest e qualidade das métricas obtidas."""
    rf, metrics = train_random_forest(
        split_pkl_path="data/exoplanets_split.pkl",
        model_output_path="mvp-exo/artifacts/rf_model.joblib",
        hyperparameters={"n_estimators": 50, "max_depth": 15},
    )

    assert isinstance(rf, RandomForestClassifier)
    assert metrics["accuracy"] >= 0.85
    assert metrics["f1_macro"] >= 0.85
    assert "confusion_matrix" in metrics
    assert "feature_importances" in metrics
    assert len(metrics["feature_importances"]) == 12


def test_rf_inference_engine(candidate_payload):
    """Testa a inferência direta utilizando o motor de predição."""
    features = {k: v for k, v in candidate_payload.items() if k != "name"}
    predictor = ExoplanetRFPredictor(
        model_path="mvp-exo/artifacts/rf_model.joblib",
        scaler_path="mvp-exo/artifacts/scaler.joblib",
    )
    result = predictor.predict(features)

    assert "prediction_class" in result
    assert result["prediction_class"] in [0, 1]
    assert "label" in result
    assert result["label"] in ["CONFIRMED", "FALSE POSITIVE"]
    assert "is_exoplanet" in result
    assert isinstance(result["is_exoplanet"], bool)
    assert 0.0 <= result["probability_confirmed"] <= 1.0
    assert 0.0 <= result["probability_false_positive"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


def test_rf_inference_missing_feature():
    """Garante que a inferência falha com erro claro se faltar alguma feature."""
    incomplete_features = {
        "orbital_period_days": 10.0,
        "transit_duration_hours": 3.0,
    }
    predictor = ExoplanetRFPredictor(
        model_path="mvp-exo/artifacts/rf_model.joblib",
        scaler_path="mvp-exo/artifacts/scaler.joblib",
    )
    with pytest.raises(ValueError, match="Features ausentes"):
        predictor.predict(incomplete_features)

