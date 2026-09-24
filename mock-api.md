# Guia de Mock da API REST — Entradas e Saídas Esperadas

Este documento apresenta a especificação completa de cada endpoint da API do **`mvp-exo`**, com exemplos realistas e mockados de payloads de entrada (*Request*), cabeçalhos (*Headers*), códigos de status HTTP e corpos de resposta (*Response*).

---

## 🧭 Visão Geral dos Endpoints

| Método | Endpoint | Descrição | Autenticação |
|---|---|---|---|
| `POST` | `/api/v1/register/` | Registro de novo usuário astrônomo | Pública |
| `POST` | `/api/v1/token/` | Obtenção do token de acesso | Pública |
| `POST` | `/api/v1/token/refresh/` | Rotação / Renovação do token de acesso | Pública |
| `GET` | `/api/v1/exoplanets/` | Listagem dos candidatos do usuário autenticado | `Token <key>` |
| `POST` | `/api/v1/exoplanets/` | Cadastro de um novo candidato com 12 features | `Token <key>` |
| `GET` | `/api/v1/exoplanets/<id>/` | Detalhes de um candidato específico | `Token <key>` |
| `PATCH` | `/api/v1/exoplanets/<id>/` | Atualização parcial de dados de um candidato | `Token <key>` |
| `DELETE` | `/api/v1/exoplanets/<id>/` | Exclusão de um candidato | `Token <key>` |
| `POST` | `/api/v1/exoplanets/<id>/predict/` | Classificação com Random Forest de um candidato persistido | `Token <key>` |
| `POST` | `/api/v1/predict/` | Classificação instantânea sob demanda (JSON com 12 features) | Pública |
| `GET` | `/api/v1/model/metrics/` | Consulta das métricas vigentes do modelo em produção | Pública |

---

## 1. Autenticação

### 1.1 Registrar Novo Usuário
Cadastra um novo usuário no sistema e já retorna seu token de acesso inicial.

* **Método:** `POST`
* **URL:** `/api/v1/register/`
* **Headers:**
  ```http
  Content-Type: application/json
  ```
* **Request Body (Mock):**
  ```json
  {
    "username": "carl_sagan",
    "email": "carl.sagan@cosmos.org",
    "password": "pale_blue_dot_1990"
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "message": "User registered successfully",
    "username": "carl_sagan",
    "email": "carl.sagan@cosmos.org",
  }
  ```
* **Erro Comum (400 Bad Request - E-mail Duplicado):**
  ```json
  {
    "email": [
      "Este e-mail já está cadastrado."
    ]
  }
  ```

---

### 1.2 Obter Token de Autenticação (Login)
Autentica o usuário via e-mail e senha, retornando o token ativo.

* **Método:** `POST`
* **URL:** `/api/v1/token/`
* **Headers:**
  ```http
  Content-Type: application/json
  ```
* **Request Body (Mock):**
  ```json
  {
    "email": "carl.sagan@cosmos.org",
    "password": "pale_blue_dot_1990"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "token": "9b7d8c4e5f2a1b3c8d7e6f5a4b3c2d1e0f9a8b7c"
  }
  ```
* **Erro (401 Unauthorized):**
  ```json
  {
    "message": "Invalid credentials"
  }
  ```

---

### 1.3 Renovar Token de Autenticação
Invalida o token anterior por motivos de segurança e emite uma nova chave.

* **Método:** `POST`
* **URL:** `/api/v1/token/refresh/`
* **Headers:**
  ```http
  Content-Type: application/json
  ```
* **Request Body (Mock):**
  ```json
  {
    "token": "9b7d8c4e5f2a1b3c8d7e6f5a4b3c2d1e0f9a8b7c"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "new_token": "e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0"
  }
  ```

---

## 2. Gerenciamento de Candidatos a Exoplanetas (CRUD)

> [!NOTE]
> Todos os endpoints desta seção exigem o cabeçalho:
> `Authorization: Token <seu_token>`

---

### 2.1 Listar Candidatos do Usuário
Recupera apenas os candidatos registrados pelo usuário autenticado.

* **Método:** `GET`
* **URL:** `/api/v1/exoplanets/`
* **Headers:**
  ```http
  Authorization: Token e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
  ```
* **Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "name": "Kepler-22b-Candidate",
      "user": "carl_sagan",
      "orbital_period_days": 289.8623,
      "transit_duration_hours": 7.42,
      "transit_depth_ppm": 492.0,
      "planet_radius_earth": 2.38,
      "insolation_flux_earth": 1.11,
      "equilibrium_temperature_k": 262.0,
      "impact_parameter": 0.12,
      "transit_signal_to_noise": 18.5,
      "stellar_effective_temperature_k": 5518.0,
      "stellar_surface_gravity": 4.44,
      "stellar_radius_solar": 0.98,
      "kepler_magnitude": 11.664,
      "created_at": "2026-09-22T14:30:00Z"
    }
  ]
  ```

---

### 2.2 Cadastrar Novo Candidato
Registra um novo candidato associado à conta do usuário com as 12 variáveis de trânsito e estelares.

* **Método:** `POST`
* **URL:** `/api/v1/exoplanets/`
* **Headers:**
  ```http
  Authorization: Token e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
  Content-Type: application/json
  ```
* **Request Body (Mock):**
  ```json
  {
    "name": "KOI-0752.01",
    "orbital_period_days": 9.48803557,
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
* **Response (201 Created):**
  ```json
  {
    "id": 2,
    "name": "KOI-0752.01",
    "user": "carl_sagan",
    "orbital_period_days": 9.48803557,
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
    "kepler_magnitude": 15.347,
    "created_at": "2026-09-22T14:45:00Z"
  }
  ```

---

### 2.3 Obter Detalhes de um Candidato
* **Método:** `GET`
* **URL:** `/api/v1/exoplanets/2/`
* **Headers:**
  ```http
  Authorization: Token e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
  ```
* **Response (200 OK):**
  ```json
  {
    "id": 2,
    "name": "KOI-0752.01",
    "user": "carl_sagan",
    "orbital_period_days": 9.48803557,
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
    "kepler_magnitude": 15.347,
    "created_at": "2026-09-22T14:45:00Z"
  }
  ```
* **Erro (404 Not Found — Candidato de outro usuário ou inexistente):**
  ```json
  {
    "detail": "Não encontrado."
  }
  ```

---

### 2.4 Atualizar Parcialmente um Candidato
* **Método:** `PATCH`
* **URL:** `/api/v1/exoplanets/2/`
* **Headers:**
  ```http
  Authorization: Token e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
  Content-Type: application/json
  ```
* **Request Body (Mock):**
  ```json
  {
    "name": "KOI-0752.01-Revisado",
    "transit_signal_to_noise": 36.4
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "id": 2,
    "name": "KOI-0752.01-Revisado",
    "user": "carl_sagan",
    "orbital_period_days": 9.48803557,
    "transit_duration_hours": 2.9575,
    "transit_depth_ppm": 615.8,
    "planet_radius_earth": 2.26,
    "insolation_flux_earth": 93.59,
    "equilibrium_temperature_k": 793.0,
    "impact_parameter": 0.146,
    "transit_signal_to_noise": 36.4,
    "stellar_effective_temperature_k": 5455.0,
    "stellar_surface_gravity": 4.467,
    "stellar_radius_solar": 0.927,
    "kepler_magnitude": 15.347,
    "created_at": "2026-09-22T14:45:00Z"
  }
  ```

---

### 2.5 Remover um Candidato
* **Método:** `DELETE`
* **URL:** `/api/v1/exoplanets/2/`
* **Headers:**
  ```http
  Authorization: Token e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
  ```
* **Response (204 No Content):**
  *(Corpo de resposta vazio)*

---

## 3. Predição com o Modelo Random Forest

### 3.1 Classificar Candidato Persistido (Com Auditoria)
Executa a predição para um candidato já registrado no banco de dados, vinculando o resultado ao modelo vigente e salvando o histórico em `PredictionResult`.

* **Método:** `POST`
* **URL:** `/api/v1/exoplanets/1/predict/`
* **Headers:**
  ```http
  Authorization: Token e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
  ```
* **Response (200 OK):**
  ```json
  {
    "prediction_id": 1,
    "candidate_id": 1,
    "candidate_name": "Kepler-22b-Candidate",
    "label": "CONFIRMED",
    "is_exoplanet": true,
    "probability_confirmed": 0.9846,
    "probability_false_positive": 0.0154,
    "confidence": 0.9846,
    "algorithm": "Random Forest"
  }
  ```

---

### 3.2 Predição Direta sob Demanda (Stateless)
Classifica um exoplaneta instantaneamente através de um payload JSON com as 12 medições, sem necessidade de autenticação prévia nem gravação em banco.

* **Método:** `POST`
* **URL:** `/api/v1/predict/`
* **Headers:**
  ```http
  Content-Type: application/json
  ```

#### Cenário A: Candidato com Perfil de Exoplaneta Confirmado
* **Request Body (Mock):**
  ```json
  {
    "orbital_period_days": 9.48803557,
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
* **Response (200 OK):**
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

#### Cenário B: Objeto com Perfil de Falso Positivo (Ex.: Binária Eclipsante ou Queda Imensa)
* **Request Body (Mock):**
  ```json
  {
    "orbital_period_days": 1.73695,
    "transit_duration_hours": 2.4064,
    "transit_depth_ppm": 8079.2,
    "planet_radius_earth": 33.46,
    "insolation_flux_earth": 891.96,
    "equilibrium_temperature_k": 1395.0,
    "impact_parameter": 1.276,
    "transit_signal_to_noise": 505.6,
    "stellar_effective_temperature_k": 5805.0,
    "stellar_surface_gravity": 4.564,
    "stellar_radius_solar": 0.791,
    "kepler_magnitude": 15.597
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "label": "FALSE POSITIVE",
    "is_exoplanet": false,
    "probability_confirmed": 0.0412,
    "probability_false_positive": 0.9588,
    "confidence": 0.9588,
    "algorithm": "Random Forest"
  }
  ```

#### Erro Comum de Validação (400 Bad Request — Campo Faltante):
Se o payload for enviado sem alguma das 12 features obrigatórias:
```json
{
  "transit_signal_to_noise": [
    "Este campo é obrigatório."
  ]
}
```

---

## 4. Métricas do Modelo em Produção

Retorna o relatório de saúde, acurácia, F1-Score, matriz de confusão e hiperparâmetros da execução oficial do Random Forest registrada no banco de dados.

* **Método:** `GET`
* **URL:** `/api/v1/model/metrics/`
* **Headers:**
  ```http
  Accept: application/json
  ```
* **Response (200 OK):**
  ```json
  {
    "id": 1,
    "algorithm_name": "random_forest",
    "trained_at": "2026-09-22T14:31:40.512Z",
    "accuracy": 0.9314707432788614,
    "precision": 0.9255562779144405,
    "recall": 0.926149176378411,
    "f1_score": 0.9258482613589146,
    "true_positive": 1144,
    "true_negative": 623,
    "false_positive": 64,
    "false_negative": 66,
    "hyperparameters": {
      "bootstrap": true,
      "ccp_alpha": 0.0,
      "class_weight": "balanced_subsample",
      "criterion": "entropy",
      "max_depth": 30,
      "max_features": "sqrt",
      "max_leaf_nodes": null,
      "max_samples": null,
      "min_impurity_decrease": 0.0,
      "min_samples_leaf": 1,
      "min_samples_split": 2,
      "min_weight_fraction_leaf": 0.0,
      "monotonic_cst": null,
      "n_estimators": 200,
      "n_jobs": -1,
      "oob_score": true,
      "random_state": 42,
      "verbose": 0,
      "warm_start": false
    },
    "model_artifact_path": "/home/lucaslima/Área de trabalho/Projetos/ml_exoplanets/mvp-exo/artifacts/rf_model.joblib"
  }
  ```

