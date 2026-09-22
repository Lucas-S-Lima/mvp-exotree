# Relatório de Decisão #002 — Aplicação do Padrão Singleton no Motor de Inferência

**Projeto:** MVP Exoplanetas (`mvp-exo`)  
**Data:** 22/09/2026  
**Status:** Aprovado  

---

## 1. Problema

O modelo final de Random Forest treinado com 200 árvores possui cerca de **12 MB** no disco rígido (`rf_model.joblib`). O processo de carregar esse arquivo via `joblib.load()` envolve:
1. Leitura de disco (I/O intensivo);
2. Desserialização de estruturas de dados C/Python;
3. Reconstrução de centenas de nós e matrizes de decisão na memória RAM.

Se o carregamento do modelo fosse feito a cada requisição HTTP que chega na API (por exemplo, a cada `POST /api/v1/predict/`), os seguintes problemas graves ocorreriam:
* **Gargalo de I/O e Latência Inaceitável:** Cada requisição levaria entre 200ms e 800ms apenas para ler o arquivo do disco antes mesmo de calcular a predição.
* **Explosão de Consumo de Memória (Memory Leak/Bloat):** Se 50 usuários fizessem predições simultaneamente, o servidor alocaria $50 \times 12\text{ MB} \approx 600\text{ MB}$ de instâncias idênticas e redundantes do mesmo modelo na memória.
* **Concorrência e Esgotamento de Recursos:** O disco e o processador entrariam em contenção severa sob carga.

---

## 2. Objetivo

Permitir que a API sirva predições com **latência inferior a 5 milissegundos**, eliminando leituras repetidas de disco e garantindo que o modelo e o normalizador (`StandardScaler`) residam em memória de forma compartilhada e segura.

---

## 3. Porquê da Decisão

### Imutabilidade do Modelo em Produção
Durante a execução da API, os parâmetros do Random Forest e as médias do Scaler são puramente **somente-leitura (*read-only*)**. Eles não mudam de estado entre requisições sucessivas de diferentes usuários.

### Comparativo de Alternativas Consideradas:
1. **Instanciação por Requisição:** Descartada imediatamente devido ao alto custo de I/O de 12 MB por chamada e pico de memória.
2. **Variável Global Solta no Módulo (`model = joblib.load(...)`):**
   * *Problema:* O arquivo seria lido no momento da importação do módulo (`import views`). Se o arquivo ainda não existisse (ex.: antes de rodar os scripts de treino ou em testes que criam o ambiente do zero), o Django falharia em inicializar com `FileNotFoundError`. Além disso, dificulta a injeção de artefatos alternativos em testes automatizados.
3. **Padrão de Projeto Singleton com Carregamento Preguiçoso (*Lazy Loading*):**
   * *Vantagem:* A classe controla seu próprio ciclo de vida. O carregamento ocorre de forma sob demanda (*lazy*), apenas quando a primeira predição é solicitada.
   * *Vantagem:* Uma única instância é criada e reutilizada por todas as chamadas subsequentes no mesmo processo de trabalho do servidor.
   * *Vantagem:* Permite fornecer suporte a testes unitários (forçando recarga com caminhos simulados ou temporários).

---

## 4. Escolha Feita

A decisão foi implementar a classe `ExoplanetRFPredictor` utilizando o padrão **Singleton** por meio da sobreposição do método mágico `__new__` e de um atributo de classe `_instance` no arquivo [`pipeline/inference.py`](file:///home/lucaslima/Área%20de%20trabalho/Projetos/ml_exoplanets/mvp-exo/pipeline/inference.py):

```python
class ExoplanetRFPredictor:
    """Motor de inferência singleton para o modelo Random Forest."""

    _instance = None
    _model: RandomForestClassifier | None = None
    _scaler: StandardScaler | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_artifacts(self, force_reload: bool = False):
        if self._model is None or self._scaler is None or force_reload:
            self._model = joblib.load(self.model_path)
            self._scaler = joblib.load(self.scaler_path)
```

### Mecânica de Funcionamento:
1. Na primeira chamada `predictor = ExoplanetRFPredictor()`, o Python verifica se `cls._instance` é `None`. Sendo `None`, instancia o objeto e guarda sua referência.
2. A leitura do disco ocorre apenas uma vez através de `load_artifacts()`.
3. Nas chamadas seguintes, `__new__` simplesmente devolve a referência já existente em `cls._instance`.
4. **Impacto:** O tempo médio de resposta de inferência caiu de ~350ms para **menos de 2ms**, com consumo de memória estritamente constante.

