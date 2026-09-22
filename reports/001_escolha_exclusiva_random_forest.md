# Relatório de Decisão #001 — Escolha Exclusiva do Random Forest para o MVP

**Projeto:** MVP Exoplanetas (`mvp-exo`)  
**Data:** 22/09/2026  
**Status:** Aprovado  

---

## 1. Problema

No projeto original de pesquisa (`ml_exoplanets`), diversos algoritmos de Machine Learning foram desenvolvidos e comparados em paralelo: **Regressão Logística**, **Support Vector Machines (SVM)** e **Random Forest**.

Manter múltiplos modelos em um produto mínimo viável (MVP) gera diversos problemas práticos:
1. **Complexidade excessiva de manutenção:** Código duplicado de treinamento, grids de busca heterogêneos e dependências desnecessárias.
2. **Arquitetura da API dispersa:** Endpoints precisavam lidar com parâmetros e comportamentos distintos de cada algoritmo.
3. **Incerteza na inferência em produção:** Usuários finais e sistemas consumidores precisavam escolher qual modelo chamar, sem saber com precisão qual algoritmo entregava a melhor relação entre acurácia e estabilidade em dados reais.

---

## 2. Objetivo

Selecionar e padronizar **um único algoritmo de classificação** para compor a espinha dorsal do MVP, garantindo:
* O mais alto desempenho preditivo e equilíbrio entre classes (F1-Macro);
* Robustez contra não-linearidades e valores extremos típicos de dados astrofísicos;
* Baixo tempo de resposta em produção;
* Arquitetura de software enxuta e focada.

---

## 3. Porquê da Decisão

Avaliando o comportamento teórico e os resultados empíricos obtidos na base de dados da missão Kepler (tabela Cumulative KOI com 12 atributos e 9.564 registros), comparamos as opções:

### A. Regressão Logística
* **Limitação:** É um modelo linear. As relações entre variáveis físicas como período orbital, profundidade de trânsito e fluxo de insolação são altamente não-lineares. Mesmo após a transformação logarítmica das variáveis de cauda longa, a Regressão Logística não conseguiu capturar interações complexas entre múltiplos atributos estelares e planetários simultaneamente.
* **Resultado:** Desempenho inferior nos testes (F1-score significativamente mais baixo).

### B. Support Vector Machines (SVM)
* **Limitação:** O SVM com kernel RBF apresentou bom poder preditivo, mas impõe custo computacional elevado de treinamento ($O(n^2)$ a $O(n^3)$), alta sensibilidade à escala das variáveis e tempo de inferência mais lento. O ajuste conjunto dos hiperparâmetros $C$ e $\gamma$ é muito sensível e menos interpretável.

### C. Random Forest (Vencedor)
* **Estrutura de Ensemble (*Bagging*):** Combina centenas de árvores de decisão descorrelacionadas geradas com amostragem aleatória de dados (*bootstrap*) e de atributos (*feature subsampling*), reduzindo a variância e mitigando o risco de overfitting.
* **Capacidade Não-Linear Inerente:** Modela com perfeição fronteiras de decisão complexas e interações de alta ordem entre características astronômicas sem exigir engenharia manual de polinômios.
* **Robustez a Outliers e Escalas:** Embora tenhamos padronizado os dados para uniformidade do pipeline, as árvores de decisão baseiam suas divisões em ordenação, sendo naturalmente resilientes a variações abruptas de magnitude.
* **Probabilidade via Votação de Árvores:** A fração de árvores que votam em determinada classe fornece uma estimativa de probabilidade suave e altamente confiável para a API.
* **Resultados Comprovados:** Nos experimentos com validação cruzada e teste cego, o Random Forest atingiu a liderança absoluta:
  * **Acurácia:** **93.15%**
  * **F1-Macro:** **92.59%**
  * **OOB Score:** **92.07%**

---

## 4. Escolha Feita

A decisão foi **eliminar completamente os outros classificadores do escopo do MVP e especializar toda a arquitetura no Random Forest**:

1. **Configuração Ótima de Hiperparâmetros:**
   ```python
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
   ```
2. **Modelagem no Banco de Dados:** A tabela `Algorithm` no Django foi simplificada para conter unicamente a opção `"random_forest"`, eliminando complexidade relacional desnecessária.
3. **Pipeline Otimizado:** Todo o pipeline de pré-processamento, GridSearch e inferência foi direcionado para maximizar a eficiência e a estabilidade deste algoritmo específico.

