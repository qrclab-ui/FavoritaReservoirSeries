# Estrutura do codigo

O codigo do Prophet foi separado em camadas para deixar o raciocinio didatico.

## Fluxo

1. `run.py` carrega o recorte Favorita com a coluna `onpromotion`.
2. `model.py` ajusta o Prophet usando a serie de vendas e o regressor exogeno.
3. As previsoes sao avaliadas com as mesmas metricas dos outros baselines.
4. Os artefatos sao salvos em `results/`.

## Responsabilidades

- `model.py`
  Construcao do modelo Prophet e geracao da previsao.
- `run.py`
  Execucao completa do experimento.
- `test_model.py`
  Verificacao automatizada em uma serie sintetica com padrao semanal.

## Valor didatico

Essa organizacao evidencia que um modelo popular de forecasting pode ser comparado com RC e QRC dentro do mesmo protocolo experimental.
