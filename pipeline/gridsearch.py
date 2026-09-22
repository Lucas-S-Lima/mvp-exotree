"""Módulo de busca de hiperparâmetros (GridSearch) exclusivo para Random Forest."""

import logging
import time
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from pipeline.training import load_split_data

logger = logging.getLogger(__name__)

FULL_PARAM_GRID = {
    "n_estimators": [150, 200, 300],
    "max_depth": [None, 10, 20, 30],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2"],
    "class_weight": [None, "balanced", "balanced_subsample"],
}

QUICK_PARAM_GRID = {
    "n_estimators": [50, 100],
    "max_depth": [10, 20],
    "min_samples_leaf": [1],
}


def run_random_forest_gridsearch(
    split_pkl_path: str | Path = "data/exoplanets_split.pkl",
    quick: bool = False,
    cv_splits: int = 5,
    n_jobs: int = -1,
    verbose: int = 1,
) -> dict:
    """Executa a busca de hiperparâmetros com validação cruzada para Random Forest."""
    data = load_split_data(split_pkl_path)
    x_train, y_train = data["x_train"], data["y_train"]

    param_grid = QUICK_PARAM_GRID if quick else FULL_PARAM_GRID

    base_estimator = RandomForestClassifier(
        criterion="entropy",
        random_state=42,
    )

    cv = StratifiedKFold(
        n_splits=cv_splits,
        shuffle=True,
        random_state=0,
    )

    grid_search = GridSearchCV(
        estimator=base_estimator,
        param_grid=param_grid,
        scoring=["accuracy", "precision_macro", "recall_macro", "f1_macro"],
        refit="f1_macro",
        cv=cv,
        n_jobs=n_jobs,
        verbose=verbose,
    )

    logger.info("Iniciando GridSearch do Random Forest (quick=%s)...", quick)
    start_time = time.perf_counter()
    grid_search.fit(x_train, y_train)
    elapsed_time = time.perf_counter() - start_time

    df_results = pd.DataFrame(grid_search.cv_results_)
    top_configs = (
        df_results.sort_values("rank_test_f1_macro")[
            [
                "rank_test_f1_macro",
                "mean_test_f1_macro",
                "std_test_f1_macro",
                "mean_test_accuracy",
                "mean_fit_time",
                "params",
            ]
        ]
        .head(5)
        .to_dict(orient="records")
    )

    logger.info(
        "GridSearch finalizado em %.2f s. Melhor F1-Macro: %.4f com parâmetros: %s",
        elapsed_time,
        grid_search.best_score_,
        grid_search.best_params_,
    )

    return {
        "best_score": float(grid_search.best_score_),
        "best_params": grid_search.best_params_,
        "elapsed_time_seconds": float(elapsed_time),
        "total_combinations": len(grid_search.cv_results_["params"]),
        "top_configurations": top_configs,
        "best_estimator": grid_search.best_estimator_,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_random_forest_gridsearch(quick=True)

