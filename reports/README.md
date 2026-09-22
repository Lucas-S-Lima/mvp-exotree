# Relatórios de Decisão Arquitetural e de Machine Learning — MVP Exoplanetas

Esta pasta reúne os relatórios técnicos que documentam formalmente as principais decisões tomadas no desenvolvimento do **`mvp-exo`**. Cada documento detalha o **problema**, o **objetivo**, os **motivos da decisão** e a **escolha implementada**.

---

## 📑 Índice de Decisões

| ID | Documento | Assunto |
|:---:|---|---|
| **#001** | [001_escolha_exclusiva_random_forest.md](file:///home/lucaslima/%C3%81rea%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/reports/001_escolha_exclusiva_random_forest.md) | Escolha do Random Forest como classificador único do MVP |
| **#002** | [002_padrao_singleton_motor_inferencia.md](file:///home/lucaslima/%C3%81rea%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/reports/002_padrao_singleton_motor_inferencia.md) | Aplicação do padrão Singleton no Motor de Inferência (`ExoplanetRFPredictor`) |
| **#003** | [003_persistencia_scaler_producao.md](file:///home/lucaslima/%C3%81rea%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/reports/003_persistencia_scaler_producao.md) | Persistência do `StandardScaler` e mitigação de *Data Leakage* |
| **#004** | [004_transformacao_logaritmica_features_assimetricas.md](file:///home/lucaslima/%C3%81rea%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/reports/004_transformacao_logaritmica_features_assimetricas.md) | Transformação `log1p` em variáveis de cauda longa (*right-skewed*) |
| **#005** | [005_estrategia_rotulagem_e_exclusao_candidates.md](file:///home/lucaslima/%C3%81rea%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/reports/005_estrategia_rotulagem_e_exclusao_candidates.md) | Formulação de classificação binária e exclusão da classe `CANDIDATE` no treino |
| **#006** | [006_otimizacao_gridsearch_metrica_f1_macro.md](file:///home/lucaslima/%C3%81rea%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/reports/006_otimizacao_gridsearch_metrica_f1_macro.md) | Estratégia do GridSearch com `StratifiedKFold`, F1-Macro e modo `--quick` |
| **#007** | [007_arquitetura_api_drf_duplo_endpoint_predicao.md](file:///home/lucaslima/%C3%81rea%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/reports/007_arquitetura_api_drf_duplo_endpoint_predicao.md) | Arquitetura REST em DRF com suporte a duplo fluxo de predição |

