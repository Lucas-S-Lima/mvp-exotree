# Relatório de Decisão #003 — Persistência do Scaler para Produção e Prevenção de Data Leakage

**Projeto:** MVP Exoplanetas (`mvp-exo`)  
**Data:** 22/09/2026  
**Status:** Aprovado  

---

## 1. Problema

Durante a fase de treinamento, as 12 variáveis físicas de candidatos a exoplanetas foram padronizadas com o `StandardScaler`, que subtrai a média ($\mu$) e divide pelo desvio padrão ($\sigma$) de cada atributo:

$$z = \frac{x - \mu}{\sigma}$$

Quando a aplicação é colocada em produção através de uma API REST, surge um desafio crucial:
* O usuário envia para a API **uma única observação** de um candidato com valores astronômicos brutos (ex.: `orbital_period_days = 9.4880`, `transit_depth_ppm = 615.8`).
* É matematicamente impossível calcular média e desvio padrão significativos sobre **uma única amostra** (o desvio padrão de 1 ponto amostral é zero ou indefinido).
* Se tentássemos re-ajustar (*fit*) o scaler com novos dados acumulados na API, cometeríamos o erro grave de **Data Leakage** (vazamento de dados) e mudaríamos a distribuição espacial das features que o Random Forest aprendeu no treino.

---

## 2. Objetivo

Assegurar **paridade matemática estrita** entre o treinamento e a inferência em tempo real, garantindo que qualquer amostra recebida via API seja transformada de forma determinística com a mesma régua estatística usada no treinamento.

---

## 3. Porquê da Decisão

### A. O Scaler como Artefato de Produção
Um erro comum em pipelines de Machine Learning é tratar o scaler como um script transitório de preparação, descartando-o após o treino e salvando apenas o modelo. No entanto, o `StandardScaler` armazena conhecimento empírico fundamental:
* `scaler.mean_`: vetor com a média de cada uma das 12 colunas;
* `scaler.scale_`: vetor com o desvio padrão de cada uma das 12 colunas.

Sem esses dois vetores preservados, o modelo treinado se torna inútil em ambiente real, pois receberia números em escalas completamente divergentes das árvores de decisão.

### B. Separação Estrita de `fit` e `transform`
* **Durante o Treino:** Executa-se `scaler.fit_transform(x_known)`. O scaler "aprende" os parâmetros e transforma a base.
* **Durante a Inferência (API):** Executa-se **apenas** `scaler.transform(x_novo)`. O scaler nunca reaprende nem altera seus parâmetros internos em produção.

---

## 4. Escolha Feita

A decisão foi transformar o `StandardScaler` em um artefato persistido de primeira classe no MVP:

1. **Persistência Automática no Pré-processamento ([`pipeline/preprocessing.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/preprocessing.py)):**
   ```python
   x_scaled, scaler = transform_features(x_known_df, fit_scaler=True)
   joblib.dump(scaler, output_scaler_path)  # Salvo em artifacts/scaler.joblib
   ```
2. **Carregamento no Motor de Inferência ([`pipeline/inference.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/inference.py)):**
   O `ExoplanetRFPredictor` carrega o arquivo `artifacts/scaler.joblib` juntamente com o modelo `rf_model.joblib`.
3. **Pipeline de Inferência Determinístico:**
   Toda entrada da API é submetida a `scaler.transform(df_novo)`, assegurando que uma entrada igual receba rigorosamente a mesma pontuação e probabilidade, sem qualquer interferência de amostras vizinhas.

