"""Módulo de treinamento e avaliação do modelo Random Forest."""

import logging
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from pipeline.constants import (
    FEATURE_NAMES,
    OPTIMAL_RF_HYPERPARAMETERS,
    REVERSE_LABEL_MAP,
)

logger = logging.getLogger(__name__)


def load_split_data(split_pkl_path: str | Path = "data/exoplanets_split.pkl") -> dict:
    """Carrega dados de treino e teste serializados."""
    split_path = Path(split_pkl_path)
    if not split_path.exists():
        raise FileNotFoundError(f"Arquivo de split não encontrado em: {split_path}")
    return joblib.load(split_path)


def compute_metrics(model: RandomForestClassifier, x_test: np.ndarray, y_test: np.ndarray) -> dict:
    """Calcula todas as métricas relevantes de teste e matriz de confusão."""
    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average="macro"))
    rec_macro = float(recall_score(y_test, y_pred, average="macro"))
    f1_macro = float(f1_score(y_test, y_pred, average="macro"))

    report_str = classification_report(
        y_test,
        y_pred,
        target_names=[REVERSE_LABEL_MAP[0], REVERSE_LABEL_MAP[1]],
    )
    report_dict = classification_report(
        y_test,
        y_pred,
        target_names=[REVERSE_LABEL_MAP[0], REVERSE_LABEL_MAP[1]],
        output_dict=True,
    )

    oob_score = getattr(model, "oob_score_", None)

    return {
        "accuracy": acc,
        "precision_macro": prec_macro,
        "recall_macro": rec_macro,
        "f1_macro": f1_macro,
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "confusion_matrix": cm.tolist(),
        "classification_report_str": report_str,
        "classification_report_dict": report_dict,
        "oob_score": float(oob_score) if oob_score is not None else None,
        "feature_importances": {
            feat: float(imp)
            for feat, imp in zip(FEATURE_NAMES, model.feature_importances_)
        },
    }


def train_random_forest(
    split_pkl_path: str | Path = "data/exoplanets_split.pkl",
    model_output_path: str | Path = "artifacts/rf_model.joblib",
    hyperparameters: dict | None = None,
    oob_score: bool = True,
) -> tuple[RandomForestClassifier, dict]:
    """Treina o Random Forest com os hiperparâmetros informados e salva o modelo."""
    data = load_split_data(split_pkl_path)
    x_train, y_train = data["x_train"], data["y_train"]
    x_test, y_test = data["x_test"], data["y_test"]

    params = OPTIMAL_RF_HYPERPARAMETERS.copy()
    if hyperparameters:
        params.update(hyperparameters)

    # Configura o modelo
    rf = RandomForestClassifier(
        n_estimators=params.get("n_estimators", 200),
        criterion=params.get("criterion", "entropy"),
        class_weight=params.get("class_weight", "balanced_subsample"),
        max_depth=params.get("max_depth", 30),
        min_samples_leaf=params.get("min_samples_leaf", 1),
        max_features=params.get("max_features", "sqrt"),
        random_state=params.get("random_state", 42),
        n_jobs=params.get("n_jobs", -1),
        oob_score=oob_score,
    )

    logger.info("Iniciando treinamento do Random Forest...")
    rf.fit(x_train, y_train)
    logger.info("Treinamento concluído com sucesso.")

    metrics = compute_metrics(rf, x_test, y_test)
    logger.info(
        "Resultados no Teste -> Accuracy: %.4f | F1-Macro: %.4f | Precision: %.4f | Recall: %.4f",
        metrics["accuracy"],
        metrics["f1_macro"],
        metrics["precision_macro"],
        metrics["recall_macro"],
    )

    # Persistência
    model_path = Path(model_output_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, model_path)
    logger.info("Modelo Random Forest salvo em %s", model_path)

    return rf, metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_random_forest()

