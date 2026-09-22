# Relatório de Decisão #006 — Estratégia de GridSearch com Métrica F1-Macro e Validação Cruzada Estratificada

**Projeto:** MVP Exoplanetas (`mvp-exo`)  
**Data:** 22/09/2026  
**Status:** Aprovado  

---

## 1. Problema

No conjunto de dados com rótulo conhecido da missão Kepler, há um desbalanceamento natural entre as classes:
* **CONFIRMED:** ~36% das amostras;
* **FALSE POSITIVE:** ~64% das amostras (quase o dobro da classe de planetas confirmados).

Se utilizássemos a **Acurácia Simples** como métrica para guiar a busca de hiperparâmetros no `GridSearchCV`:
* Um modelo enviesado que simplesmente previsse sempre a classe majoritária (`FALSE POSITIVE`) atingiria ~64% de acurácia sem identificar um único exoplaneta real sequer.
* O otimizador priorizaria configurações de hiperparâmetros conservadoras, com alto viés a favor da classe majoritária, prejudicando o recall da classe minoritária (`CONFIRMED`).

Além disso, rodar uma grade exaustiva de hiperparâmetros (216 combinações $\times$ 5 folds = **1.080 treinamentos de Random Forest**) em pipelines de Integração Contínua (CI) ou testes locais rápidos pode demorar de 15 a 30 minutos, inviabilizando testes ágeis.

---

## 2. Objetivo

1. Definir uma métrica de otimização que trate ambas as classes com igual relevância física e estatística.
2. Garantir que a amostragem da validação cruzada seja representativa em todos os folds.
3. Disponibilizar um mecanismo operacional flexível de execução do GridSearch tanto em modo ágil (`--quick`) quanto exaustivo.

---

## 3. Porquê da Decisão

### A. Escolha do F1-Score Macro
O **F1-Macro** calcula a média aritmética não ponderada do F1-score de cada classe individualmente:

$$F1_{\text{macro}} = \frac{F1_{\text{CONFIRMED}} + F1_{\text{FALSE POSITIVE}}}{2}$$

Diferente do F1-Weighted ou da Acurácia, o F1-Macro penaliza severamente modelos que negligenciam a classe minoritária. Uma configuração só é considerada a melhor se mantiver precisão e recall equilibrados para ambas as categorias.

### B. Validação Cruzada Estratificada (StratifiedKFold)
Em vez de uma validação cruzada aleatória simples, o `StratifiedKFold` garante que cada um dos 5 folds contenha exatamente a mesma proporção de ~36% CONFIRMED e ~64% FALSE POSITIVE, prevenindo folds anômalos que distorçam as estimativas de desempenho.

### C. Abordagem de Grade Dual (Quick vs Completa)
* **Modo Completo (216 combinações):** Utilizado para treinamento e descoberta oficial de hiperparâmetros ótimos (`n_estimators`, `max_depth`, `min_samples_leaf`, `max_features`, `class_weight`).
* **Modo Rápido (4 combinações):** Essencial para checagem rápida em testes automatizados (`pytest`), garantindo que o pipeline de busca permaneça íntegro sem sobrecarregar recursos computacionais.

---

## 4. Escolha Feita

A estratégia foi codificada de forma nativa e desacoplada em [`pipeline/gridsearch.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/gridsearch.py) e exposta via comando CLI do Django:

```python
grid_search = GridSearchCV(
    estimator=base_estimator,
    param_grid=param_grid,
    scoring=["accuracy", "precision_macro", "recall_macro", "f1_macro"],
    refit="f1_macro",
    cv=StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=0),
    n_jobs=n_jobs,
)
```

1. **Hiperparâmetros Vencedores Identificados:**
   * `n_estimators`: **200**
   * `criterion`: **"entropy"**
   * `class_weight`: **"balanced_subsample"**
   * `max_depth`: **30**
   * `min_samples_leaf`: **1**
   * `max_features`: **"sqrt"**
   * **F1-Macro alcançado no CV:** **0.9187** (e **0.9259** no teste cego).
2. **Operação via Linha de Comando:**
   ```bash
   # Validação ágil (executa em ~5 segundos):
   python manage.py rf_gridsearch --quick

   # Busca completa:
   python manage.py rf_gridsearch
   ```

