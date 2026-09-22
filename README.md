# MVP Exoplanetas — Classificação com Random Forest

MVP autocontido para detecção e classificação de candidatos a exoplanetas (Kepler Objects of Interest - KOI) utilizando **exclusivamente o algoritmo Random Forest**.

O projeto engloba todo o ciclo de vida de Machine Learning e engenharia de software: extração de dados da NASA, pré-processamento, engenharia de atributos (transformação logarítmica e padronização), busca de hiperparâmetros (GridSearch), treinamento, persistência de artefatos e uma API REST completa construída com Django REST Framework (DRF).

---

## 🚀 Desempenho do Modelo Random Forest

Configuração ótima obtida via validação cruzada estratificada (5 folds, 216 combinações):

- **Hiperparâmetros Ótimos**:
  - `n_estimators`: 200
  - `criterion`: "entropy"
  - `class_weight`: "balanced_subsample"
  - `max_depth`: 30
  - `min_samples_leaf`: 1
  - `max_features`: "sqrt"
  - `random_state`: 42
- **Resultados no Conjunto de Teste (1.897 amostras)**:
  - **Acurácia**: ~93.15%
  - **F1-Score Macro**: ~92.59%
  - **Precisão Macro**: ~92.56%
  - **Recall Macro**: ~92.61%
  - **OOB Score**: ~92.07%

---

## 📁 Estrutura de Arquivos

```text
mvp-exo/
├── data/
│   ├── cumulative_koi.csv              # Dados originais da NASA (cópia local para funcionamento offline)
│   ├── cumulative_koi_treated.csv      # Dataset limpo e tratado
│   └── exoplanets_split.pkl            # Split estratificado de treino/teste (x_train, x_test, y_train, y_test)
├── artifacts/
│   ├── rf_model.joblib                 # Artefato do modelo Random Forest treinado
│   └── scaler.joblib                   # StandardScaler ajustado para novas predições
├── pipeline/
│   ├── constants.py                    # 12 variáveis KOI, colunas log, mapeamento de classes e hiperparâmetros
│   ├── extraction.py                   # Download da NASA Exoplanet Archive (TAP) com retry e fallback offline
│   ├── preprocessing.py                # Limpeza, imputação por mediana por classe, log1p e padronização
│   ├── training.py                     # Treinamento do Random Forest, cálculo de métricas e persistência
│   ├── gridsearch.py                   # GridSearchCV com StratifiedKFold e scoring F1-Macro
│   └── inference.py                    # Motor de inferência singleton para novas predições
├── config/
│   ├── settings.py                     # Configurações Django (DRF, SQLite, caminhos de artefatos)
│   ├── urls.py                         # Roteador principal
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── models.py                       # Modelos: User, ExoplanetCandidate, Algorithm, ModelRun, PredictionResult
│   ├── serializers.py                  # Serializers DRF para autenticação, candidatos, predições e métricas
│   ├── views.py                        # Views da API REST
│   ├── urls.py                         # Rotas da API (/api/v1/...)
│   ├── admin.py                        # Django Admin
│   ├── migrations/                     # Migrações do banco SQLite
│   └── management/
│       └── commands/
│           ├── run_pipeline.py         # python manage.py run_pipeline
│           ├── rf_train.py             # python manage.py rf_train
│           └── rf_gridsearch.py        # python manage.py rf_gridsearch [--quick]
├── tests/
│   ├── conftest.py                     # Fixtures do pytest
│   ├── test_pipeline.py                # Testes do pipeline (dados, treino, inferência)
│   ├── test_gridsearch.py              # Testes do GridSearch
│   └── test_api.py                     # Testes dos endpoints DRF
├── manage.py                           # CLI do Django
├── pyproject.toml                      # Configuração uv / pip
├── requirements.txt                    # Dependências
├── pytest.ini                          # Configuração de testes
└── README.md
```

---

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.12+
- `pip` ou `uv`

### 1. Instalar Dependências

Utilizando `pip`:
```bash
pip install -r requirements.txt
```

Ou utilizando `uv`:
```bash
uv pip install -r requirements.txt
```

### 2. Configurar o Banco de Dados

Execute as migrações para inicializar o banco de dados SQLite (`db.sqlite3`):
```bash
python manage.py migrate
```

Opcional: crie um superusuário para acessar o Django Admin (`/admin/`):
```bash
python manage.py createsuperuser
```

---

## ⚙️ Comandos de Machine Learning

### 1. Executar o Pipeline Completo
Executa verificação dos dados brutos, pré-processamento, split e treinamento:
```bash
python manage.py run_pipeline
```

### 2. Treinar o Random Forest
Treina o modelo nos dados tratados, salva o artefato `artifacts/rf_model.joblib` e registra as métricas em `ModelRun`:
```bash
python manage.py rf_train
```

Parâmetros opcionais:
```bash
python manage.py rf_train --n-estimators 200 --max-depth 30
```

### 3. Executar o GridSearch
Realiza a busca em grade com validação cruzada de 5 folds:
```bash
# Modo rápido (validação de 4 combinações):
python manage.py rf_gridsearch --quick

# Modo completo (216 combinações):
python manage.py rf_gridsearch
```

---

## 🧪 Executando os Testes

Para rodar toda a suíte de testes com `pytest`:
```bash
pytest
```

Ou com verbosidade:
```bash
pytest -v
```

---

## 🌐 Endpoints da API REST (DRF)

Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

Acesse a API em: `http://127.0.0.1:8000/`

### 1. Autenticação

#### Registro de Usuário
- **POST** `/api/v1/register/`
- **Body**:
```json
{
  "username": "astronomo1",
  "email": "astronomo1@nasa.gov",
  "password": "senha_segura_123"
}
```
- **Resposta (201 Created)**:
```json
{
  "message": "User registered successfully",
  "username": "astronomo1",
  "email": "astronomo1@nasa.gov",
  "token": "4a7b9c..."
}
```

#### Obter Token
- **POST** `/api/v1/token/`
- **Body**:
```json
{
  "email": "astronomo1@nasa.gov",
  "password": "senha_segura_123"
}
```

#### Renovar Token
- **POST** `/api/v1/token/refresh/`
- **Body**:
```json
{
  "token": "token_antigo"
}
```

---

### 2. Candidatos a Exoplanetas (CRUD)
*Requer header `Authorization: Token <seu_token>`.*

#### Listar Candidatos do Usuário
- **GET** `/api/v1/exoplanets/`

#### Cadastrar Novo Candidato
- **POST** `/api/v1/exoplanets/`
- **Body**:
```json
{
  "name": "Kepler-Candidate-Alpha",
  "orbital_period_days": 9.4880,
  "transit_duration_hours": 2.9575,
  "transit_depth_ppm": 615.8,
  "planet_radius_earth": 2.26,
  "insolation_flux_earth": 93.59,
  "equilibrium_temperature_k": 793.0,
  "impact_parameter": 0.146,
  "transit_signal_to_noise": 35.8,
  "stellar_effective_temperature_k": 5455.0,
  "stellar_surface_gravity": 4.467,
  "stellar_radius_solar": 0.927,
  "kepler_magnitude": 15.347
}
```

#### Detalhes / Atualização / Exclusão
- **GET / PUT / PATCH / DELETE** `/api/v1/exoplanets/<id>/`

---

### 3. Predição com Random Forest

#### Classificar Candidato Cadastrado
- **POST** `/api/v1/exoplanets/<id>/predict/` *(Requer Auth)*
- **Resposta (200 OK)**:
```json
{
  "prediction_id": 1,
  "candidate_id": 1,
  "candidate_name": "Kepler-Candidate-Alpha",
  "label": "CONFIRMED",
  "is_exoplanet": true,
  "probability_confirmed": 0.9846,
  "probability_false_positive": 0.0154,
  "confidence": 0.9846,
  "algorithm": "Random Forest"
}
```

#### Predição Direta sob Demanda (JSON)
- **POST** `/api/v1/predict/` *(Público ou autenticado)*
- **Body**:
```json
{
  "orbital_period_days": 9.4880,
  "transit_duration_hours": 2.9575,
  "transit_depth_ppm": 615.8,
  "planet_radius_earth": 2.26,
  "insolation_flux_earth": 93.59,
  "equilibrium_temperature_k": 793.0,
  "impact_parameter": 0.146,
  "transit_signal_to_noise": 35.8,
  "stellar_effective_temperature_k": 5455.0,
  "stellar_surface_gravity": 4.467,
  "stellar_radius_solar": 0.927,
  "kepler_magnitude": 15.347
}
```
- **Resposta (200 OK)**:
```json
{
  "label": "CONFIRMED",
  "is_exoplanet": true,
  "probability_confirmed": 0.9846,
  "probability_false_positive": 0.0154,
  "confidence": 0.9846,
  "algorithm": "Random Forest"
}
```

---

### 4. Métricas do Modelo em Produção

- **GET** `/api/v1/model/metrics/`
- **Resposta (200 OK)**:
```json
{
  "id": 1,
  "algorithm_name": "Random Forest",
  "trained_at": "2026-09-22T14:31:40.000Z",
  "accuracy": 0.9315,
  "precision": 0.9256,
  "recall": 0.9261,
  "f1_score": 0.9259,
  "true_positive": 1144,
  "true_negative": 623,
  "false_positive": 64,
  "false_negative": 66,
  "hyperparameters": {
    "n_estimators": 200,
    "criterion": "entropy",
    "class_weight": "balanced_subsample",
    "max_depth": 30,
    "min_samples_leaf": 1,
    "max_features": "sqrt",
    "random_state": 42
  },
  "model_artifact_path": ".../artifacts/rf_model.joblib"
}
```

