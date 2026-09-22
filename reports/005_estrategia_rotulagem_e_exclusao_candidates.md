# Relatório de Decisão #005 — Estratégia de Rotulagem Binária e Exclusão da Classe CANDIDATE no Treino

**Projeto:** MVP Exoplanetas (`mvp-exo`)  
**Data:** 22/09/2026  
**Status:** Aprovado  

---

## 1. Problema

Na tabela oficial `cumulative` da missão Kepler (NASA Exoplanet Archive), a coluna de disposição (`koi_disposition` / `label`) apresenta três categorias distintas:

1. **`CONFIRMED`:** Objeto cuja assinatura de trânsito foi minuciosamente validada por observações espectroscópicas de acompanhamento e velocidade radial, confirmando-se como exoplaneta real.
2. **`FALSE POSITIVE`:** Objeto cujo sinal parecia um planeta, mas análises detalhadas revelaram ser uma estrela binária eclipsante, contaminação de fundo, manchas solares ou ruído instrumental do sensor CCD.
3. **`CANDIDATE`:** Objeto que exibe padrão de trânsito periódico com significância estatística, mas que **ainda não concluiu o processo de validação humana e observacional**.

Se treinássemos o algoritmo incluindo `CANDIDATE` como uma terceira classe independente, o modelo estaria aprendendo um estado burocrático de verificação da NASA, e não a física da detecção planetária.

---

## 2. Objetivo

Estruturar o problema como uma **classificação binária supervisionada cientificamente fundamentada**, na qual o algoritmo aprende com o padrão-ouro de dados confirmados e fica apto a classificar qualquer novo sinal duvidoso.

---

## 3. Porquê da Decisão

### A. Ausência de Verdade Fundamental (*Ground Truth*)
Um objeto `CANDIDATE` não é uma terceira entidade astrofísica; ele é, na verdade, um `CONFIRMED` ou um `FALSE POSITIVE` cujo veredito ainda não foi publicado. Adicionar rótulos incertos ao conjunto de treinamento introduziria ruído severo de rotulagem (*label noise*), prejudicando a definição das fronteiras de decisão das árvores.

### B. O Propósito Real da Aplicação (Caso de Uso de Produção)
O objetivo principal da API desenvolvida no MVP é justamente atender ao astrônomo que possui um novo sinal na mão (um candidato) e pergunta:
> *"Com base nas características de trânsito e estelares detectadas, qual é a probabilidade desse candidato ser um planeta real versus um alarme falso?"*

Para responder a essa pergunta, o classificador deve emitir uma probabilidade binária calibrada entre ser exoplaneta ou falso positivo.

---

## 4. Escolha Feita

1. **Filtragem no Pré-processamento ([`pipeline/preprocessing.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/preprocessing.py)):**
   Os dados são divididos em duas populações:
   ```python
   mask_known = treated_df["label"].isin(["CONFIRMED", "FALSE POSITIVE"])
   known_df = treated_df[mask_known].copy()
   ```
2. **Codificação Binária:**
   Utilizou-se o `LabelEncoder` com mapeamento alfabético determinístico:
   * **`0`**: `CONFIRMED` (Exoplaneta Confirmado)
   * **`1`**: `FALSE POSITIVE` (Falso Positivo)
3. **Mapeamento Amigável na API ([`pipeline/inference.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/inference.py)):**
   Na saída dos endpoints, a predição é traduzida para:
   ```json
   {
     "label": "CONFIRMED",
     "is_exoplanet": true,
     "probability_confirmed": 0.9846,
     "probability_false_positive": 0.0154,
     "confidence": 0.9846
   }
   ```
4. **Benefício:** Redução de ruído no treinamento, permitindo que o Random Forest alcance métricas de teste puras acima de 93% de acurácia.

