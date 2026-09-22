"""Constantes e definições globais do pipeline de Machine Learning (Random Forest)."""

COLUMN_RENAME = {
    "kepoi_name": "kepler_object_of_interest_name",
    "koi_disposition": "label",
    "koi_period": "orbital_period_days",
    "koi_duration": "transit_duration_hours",
    "koi_depth": "transit_depth_ppm",
    "koi_prad": "planet_radius_earth",
    "koi_insol": "insolation_flux_earth",
    "koi_teq": "equilibrium_temperature_k",
    "koi_impact": "impact_parameter",
    "koi_model_snr": "transit_signal_to_noise",
    "koi_steff": "stellar_effective_temperature_k",
    "koi_slogg": "stellar_surface_gravity",
    "koi_srad": "stellar_radius_solar",
    "koi_kepmag": "kepler_magnitude",
}

FEATURE_NAMES = [
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
]

LOG_TRANSFORM_COLUMNS = [
    "orbital_period_days",
    "transit_depth_ppm",
    "planet_radius_earth",
    "insolation_flux_earth",
]

TARGET_COLUMN = "label"

# Classes conhecidas e codificação
LABEL_MAP = {
    "CONFIRMED": 0,
    "FALSE POSITIVE": 1,
}

REVERSE_LABEL_MAP = {
    0: "CONFIRMED",
    1: "FALSE POSITIVE",
}

# Hiperparâmetros otimizados identificados via GridSearch para o Random Forest
OPTIMAL_RF_HYPERPARAMETERS = {
    "n_estimators": 200,
    "criterion": "entropy",
    "class_weight": "balanced_subsample",
    "max_depth": 30,
    "min_samples_leaf": 1,
    "max_features": "sqrt",
    "random_state": 42,
    "n_jobs": -1,
}

