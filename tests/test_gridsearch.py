"""Testes para o módulo de GridSearch do Random Forest."""

import pytest
from pipeline.gridsearch import run_random_forest_gridsearch


def test_quick_gridsearch_execution():
    """Valida que o GridSearch em modo quick executa e retorna estrutura válida."""
    res = run_random_forest_gridsearch(
        split_pkl_path="data/exoplanets_split.pkl",
        quick=True,
        cv_splits=3,
        n_jobs=-1,
        verbose=0,
    )

    assert "best_score" in res
    assert res["best_score"] > 0.80
    assert "best_params" in res
    assert "n_estimators" in res["best_params"]
    assert "top_configurations" in res
    assert len(res["top_configurations"]) > 0
    assert res["total_combinations"] == 4
    assert res["elapsed_time_seconds"] > 0.0

