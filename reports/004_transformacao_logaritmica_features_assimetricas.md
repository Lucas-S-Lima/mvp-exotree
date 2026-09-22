# Relatório de Decisão #004 — Transformação Logarítmica (log1p) em Variáveis de Cauda Longa

**Projeto:** MVP Exoplanetas (`mvp-exo`)  
**Data:** 22/09/2026  
**Status:** Aprovado  

---

## 1. Problema

A análise exploratória dos dados astrofísicos da missão Kepler revelou que quatro variáveis essenciais possuem distribuições com **assimetria positiva extrema (*right-skewness / heavy-tailed*)**:

| Variável | Descrição Física | Comportamento Observado |
|---|---|---|
| `orbital_period_days` | Período de translação orbital (dias) | Varia de horas até centenas de dias |
| `transit_depth_ppm` | Profundidade da queda de brilho (ppm) | De dezenas a milhões de partes por milhão |
| `planet_radius_earth` | Raio planetário em raios terrestres | De sub-terrestres a gigantes gasosos ou anomalias |
| `insolation_flux_earth` | Fluxo de insolação recebido da estrela | Variação por várias ordens de magnitude exponencial |

A assimetria (*skewness*) original dessas colunas apresentava valores muito superiores a 15, com a grande maioria dos planetas concentrada em valores baixos e uma cauda esparsa de eventos extremos estendendo-se por várias ordens de magnitude.

---

## 2. Objetivo

Reduzir o impacto das ordens de magnitude extremas, aproximar a distribuição dos atributos de uma forma mais simétrica e compactar a escala das variáveis físicas para potencializar a capacidade de divisão dos nós de decisão e a normalização subsequente.

---

## 3. Porquê da Decisão

### A. Compressão de Cauda Longa
Ao aplicar o logaritmo natural, uma variação de $10$ para $100$ (um salto de 1 ordem de magnitude) passa a ter o mesmo peso relativo que um salto de $1.000$ para $10.000$. Isso reflete com muito mais fidelidade a física dos sistemas planetários (onde leis como a Terceira Lei de Kepler operam em escalas de potências e logaritmos).

### B. Por que `log1p(x)` em vez de `log(x)`?
A função matemática $\log(x)$ não é definida para $x \le 0$ e tende a $-\infty$ quando $x \to 0$. Em dados reais de trânsito planetário, pequenos valores próximos de zero são comuns.
* A função $\log1p(x) = \ln(1 + x)$ resolve esse problema:
  * Quando $x = 0$, $\ln(1 + 0) = \ln(1) = 0$.
  * Mantém total estabilidade numérica computacional para valores próximos de zero.

---

## 4. Escolha Feita

A decisão foi padronizar a aplicação de `np.log1p` nas quatro variáveis assimétricas em todas as etapas do pipeline:

1. **Constante Centralizada ([`pipeline/constants.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/constants.py)):**
   ```python
   LOG_TRANSFORM_COLUMNS = [
       "orbital_period_days",
       "transit_depth_ppm",
       "planet_radius_earth",
       "insolation_flux_earth",
   ]
   ```
2. **Execução no Pré-processamento ([`pipeline/preprocessing.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/preprocessing.py)):**
   Aplicada antes do ajuste do `StandardScaler`.
3. **Execução na Inferência em Produção ([`pipeline/inference.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/inference.py)):**
   Todo payload de candidato que chega via API é transformado automaticamente antes de ser normalizado pelo scaler, garantindo paridade perfeita com os dados de treino.

