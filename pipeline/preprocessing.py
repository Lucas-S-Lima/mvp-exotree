"""Módulo de limpeza, tratamento, transformação e divisão de dados para Random Forest."""

import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from pipeline.constants import (
    COLUMN_RENAME,
    FEATURE_NAMES,
    LOG_TRANSFORM_COLUMNS,
    TARGET_COLUMN,
)

logger = logging.getLogger(__name__)


def rename_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia colunas para identificadores padronizados."""
    df_renamed = df.rename(columns=COLUMN_RENAME)
    if TARGET_COLUMN in df_renamed.columns:
        cols = [c for c in df_renamed.columns if c != TARGET_COLUMN] + [TARGET_COLUMN]
        df_renamed = df_renamed[cols]
    return df_renamed


def clean_inconsistent_values(df: pd.DataFrame) -> pd.DataFrame:
    """Remove candidatos com zeros implausíveis e faz imputação por mediana por classe."""
    cleaned = df.copy()

    # Remover CANDIDATE com zeros implausíveis em medidas essenciais
    mask_inconsistente = (cleaned[TARGET_COLUMN] == "CANDIDATE") & (
        (cleaned["transit_signal_to_noise"] == 0)
        | (cleaned["transit_depth_ppm"] == 0)
        | (cleaned["insolation_flux_earth"] == 0)
    )
    n_removidos = mask_inconsistente.sum()
    if n_removidos > 0:
        cleaned = cleaned.drop(cleaned[mask_inconsistente].index)
        logger.info("Removidos %d registros CANDIDATE com valores nulos/implausíveis.", n_removidos)

    # Imputação de valores nulos com mediana por classe
    numeric_cols_with_nulls = [
        col for col in FEATURE_NAMES if col in cleaned.columns and cleaned[col].isnull().any()
    ]
    for col in numeric_cols_with_nulls:
        cleaned[col] = cleaned.groupby(TARGET_COLUMN)[col].transform(
            lambda s: s.fillna(s.median())
        )

    # Caso ainda restem nulos (ex.: alguma classe com todos nulos na feature), imputar mediana global
    if cleaned[FEATURE_NAMES].isnull().any().any():
        for col in FEATURE_NAMES:
            if cleaned[col].isnull().any():
                cleaned[col] = cleaned[col].fillna(cleaned[col].median())

    # Remover duplicatas com base no identificador
    if "kepler_object_of_interest_name" in cleaned.columns:
        cleaned = cleaned.drop_duplicates(subset=["kepler_object_of_interest_name"])

    return cleaned


def transform_features(
    df: pd.DataFrame,
    scaler: StandardScaler | None = None,
    fit_scaler: bool = False,
) -> tuple[np.ndarray, StandardScaler]:
    """Aplica log1p nas colunas assimétricas e normalização via StandardScaler."""
    features_df = df[FEATURE_NAMES].copy()

    # Aplica transformação logarítmica
    features_df[LOG_TRANSFORM_COLUMNS] = np.log1p(features_df[LOG_TRANSFORM_COLUMNS])

    if fit_scaler:
        scaler = StandardScaler()
        scaled_array = scaler.fit_transform(features_df)
    else:
        if scaler is None:
            raise ValueError("Scaler deve ser fornecido quando fit_scaler=False.")
        scaled_array = scaler.transform(features_df)

    return scaled_array, scaler


def encode_target(labels: pd.Series | np.ndarray) -> tuple[np.ndarray, LabelEncoder]:
    """Codifica rótulos (CONFIRMED -> 0, FALSE POSITIVE -> 1)."""
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(labels)
    return encoded, encoder


def run_full_preprocessing(
    raw_csv_path: str | Path = "data/cumulative_koi.csv",
    output_treated_csv: str | Path = "data/cumulative_koi_treated.csv",
    output_split_pkl: str | Path = "data/exoplanets_split.pkl",
    output_scaler_path: str | Path = "artifacts/scaler.joblib",
    test_size: float = 0.25,
    random_state: int = 0,
) -> dict:
    """Executa o pipeline completo de pré-processamento e divisão dos dados."""
    raw_path = Path(raw_csv_path)
    output_treated_csv = Path(output_treated_csv)
    output_split_pkl = Path(output_split_pkl)
    output_scaler_path = Path(output_scaler_path)

    output_treated_csv.parent.mkdir(parents=True, exist_ok=True)
    output_split_pkl.parent.mkdir(parents=True, exist_ok=True)
    output_scaler_path.parent.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        # Se não tiver raw_path mas já tiver output_treated_csv, usa o tratado
        if output_treated_csv.exists():
            logger.info("Usando arquivo tratado existente em %s", output_treated_csv)
            treated_df = pd.read_csv(output_treated_csv)
        else:
            raise FileNotFoundError(f"Arquivo não encontrado: {raw_path}")
    else:
        raw_df = pd.read_csv(raw_path)
        renamed_df = rename_dataset(raw_df)
        treated_df = clean_inconsistent_values(renamed_df)
        treated_df.to_csv(output_treated_csv, index=False)
        logger.info("Dados tratados salvos em %s (shape: %s)", output_treated_csv, treated_df.shape)

    # Filtrar dados com rótulo conhecido para treino/teste (CONFIRMED e FALSE POSITIVE)
    mask_known = treated_df[TARGET_COLUMN].isin(["CONFIRMED", "FALSE POSITIVE"])
    known_df = treated_df[mask_known].copy()

    # Features e Target
    x_known_df = known_df[FEATURE_NAMES].copy()
    y_known_raw = known_df[TARGET_COLUMN].to_numpy()

    # Log-transform e fit do scaler
    x_scaled, scaler = transform_features(x_known_df, fit_scaler=True)
    joblib.dump(scaler, output_scaler_path)
    logger.info("StandardScaler salvo em %s", output_scaler_path)

    # Codificação do target
    y_encoded, target_encoder = encode_target(y_known_raw)

    # Split estratificado de treino e teste
    x_train, x_test, y_train, y_test = train_test_split(
        x_scaled,
        y_encoded,
        test_size=test_size,
        random_state=random_state,
        stratify=y_encoded,
    )

    data_split = {
        "x_train": x_train,
        "x_test": x_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": FEATURE_NAMES,
        "target_classes": target_encoder.classes_.tolist(),
    }

    joblib.dump(data_split, output_split_pkl)
    logger.info(
        "Split salvo em %s (Treino: %s, Teste: %s)",
        output_split_pkl,
        x_train.shape,
        x_test.shape,
    )

    return data_split


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_full_preprocessing()

