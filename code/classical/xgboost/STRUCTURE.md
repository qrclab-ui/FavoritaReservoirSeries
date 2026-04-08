# Estrutura do codigo

Esta implementacao foi organizada para deixar claro como um modelo tabular e aplicado a forecasting.

## Fluxo

1. `run.py` carrega o recorte Favorita.
2. `classical/shared.py` constroi atributos baseados em lags, medias moveis, calendario e promocao.
3. `model.py` ajusta um `XGBRegressor`.
4. A previsao para o horizonte de teste e feita de forma recursiva, reutilizando previsoes anteriores como parte dos lags futuros.
5. As metricas e os artefatos sao salvos em `results/`.

## Responsabilidades

- `model.py`
  Treino, previsao recursiva e avaliacao.
- `run.py`
  Orquestracao do pipeline experimental.
- `test_model.py`
  Verificacao automatizada em uma serie sintetica sazonal.

## Valor didatico

Essa estrutura mostra como transformar uma serie temporal em um problema supervisionado tabular sem esconder a engenharia de atributos.
