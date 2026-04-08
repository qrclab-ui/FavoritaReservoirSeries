# Estrutura do codigo

O codigo do ETS foi dividido para destacar a separacao entre teoria, modelo, execucao e teste.

## Fluxo

1. `run.py` carrega a serie Favorita e aplica o split temporal.
2. `model.py` ajusta um modelo Holt-Winters aditivo com sazonalidade semanal.
3. As previsoes sao avaliadas com as metricas compartilhadas.
4. Os resultados sao persistidos em `results/`.

## Responsabilidades

- `model.py`
  Ajuste do ETS e geracao da previsao.
- `run.py`
  Orquestracao do experimento ponta a ponta.
- `test_model.py`
  Testes com uma serie sintetica sazonal para validar o comportamento.

## Valor didatico

Essa estrutura permite mostrar claramente que um baseline forte nao precisa ser um "modelo pesado". Ele pode ser apenas um modelo estatistico bem escolhido.
