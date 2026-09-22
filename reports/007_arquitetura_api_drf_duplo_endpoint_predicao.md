# Relatório de Decisão #007 — Arquitetura de API com Duplo Fluxo de Predição (Persistido vs Stateless)

**Projeto:** MVP Exoplanetas (`mvp-exo`)  
**Data:** 22/09/2026  
**Status:** Aprovado  

---

## 1. Problema

Ao projetar uma API REST para servir modelos de Machine Learning com Django REST Framework (DRF), deparamo-nos com dois perfis de integração com necessidades divergentes:

1. **Perfil Pesquisador / Plataforma (Com Estado e Auditoria):**
   * O astrônomo autenticado cria sua conta, cadastra candidatos a exoplanetas (`ExoplanetCandidate`), edita suas características ao longo do tempo e deseja manter o histórico de cada predição realizada (`PredictionResult`), associada à versão do modelo (`ModelRun`) que realizou a classificação.
2. **Perfil Pipeline Automatizado / Integração de Sistemas (Sem Estado - *Stateless*):**
   * Sistemas de aquisição contínua de dados de telescópios, scripts Python externos ou ferramentas analíticas em lote querem apenas enviar um JSON com as 12 medições de trânsito e obter a probabilidade instantaneamente, sem o overhead de criar registros no banco de dados a cada chamada.

Forçar um único padrão tornaria a API ou excessivamente burocrática para integrações em tempo real ou deficiente em termos de auditoria e governança.

---

## 2. Objetivo

Projetar uma arquitetura de API REST em DRF flexível que atenda aos dois cenários de integração mantendo código limpo, reaproveitamento máximo da lógica de inferência e isolamento seguro de dados entre usuários.

---

## 3. Porquê da Decisão

### A. Reuso do Motor de Inferência
Ambos os fluxos precisam da mesma validação de entrada, da mesma transformação $\log(1 + x)$, da mesma normalização `StandardScaler` e da mesma execução do Random Forest. Centralizar essa lógica no motor singleton `ExoplanetRFPredictor` permitiu que múltiplos endpoints compartilhassem o mesmo núcleo preditivo sem duplicação de regras.

### B. Isolamento de Dados por Usuário (*Multi-tenant Segurança*)
No fluxo persistido, um usuário não pode visualizar, alterar ou classificar candidatos pertencentes a outro usuário. O DRF garante isso através da filtragem estrita por `request.user` nas views e permissions (`IsAuthenticated`).

---

## 4. Escolha Feita

A decisão foi disponibilizar **dois fluxos complementares de predição** na API:

### Fluxo 1: Predição de Candidato Persistido (Auditada)
* **Endpoint:** `POST /api/v1/exoplanets/<id>/predict/`
* **Autenticação:** Obrigatória (`TokenAuthentication`).
* **Comportamento:**
  1. Recupera o candidato garantindo que pertence ao `request.user`.
  2. Extrai as 12 variáveis cadastradas.
  3. Classifica com o Random Forest.
  4. Localiza a execução mais recente em `ModelRun`.
  5. Salva um novo registro em `PredictionResult` associando candidato, modelo e resultado.
  6. Devolve o diagnóstico completo com `prediction_id`.

### Fluxo 2: Predição Direta sob Demanda (Stateless)
* **Endpoint:** `POST /api/v1/predict/`
* **Autenticação:** Aberta/Opcional.
* **Serializer de Entrada:** `DirectPredictInputSerializer` (valida os tipos e limites das 12 variáveis).
* **Comportamento:**
  1. Valida o payload JSON recebido.
  2. Executa a inferência diretamente na memória em menos de 2 milissegundos.
  3. Devolve a classificação, probabilidades e nível de confiança sem tocar no disco ou banco de dados.

### Resumo dos Endpoints Implementados:
```
POST /api/v1/register/               -> Cadastro de astrônomos
POST /api/v1/token/                  -> Obtenção de Token
POST /api/v1/token/refresh/          -> Rotação de Token
GET  /api/v1/exoplanets/             -> Listagem de candidatos do usuário
POST /api/v1/exoplanets/             -> Criação de candidato
POST /api/v1/exoplanets/<id>/predict/ -> Classificação vinculada e persistida
POST /api/v1/predict/                -> Classificação instantânea via JSON
GET  /api/v1/model/metrics/          -> Métricas vigentes do modelo em produção
```

