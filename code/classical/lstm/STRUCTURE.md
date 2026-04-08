# Estrutura do codigo

Esta implementacao organiza a LSTM como um baseline sequencial transparente e reproduzivel.

## Fluxo

1. `run.py` carrega o recorte Favorita.
2. `classical/shared.py` transforma a serie em sequencias com variaveis exogenas e calendarios.
3. `model.py` treina uma LSTM pequena em PyTorch.
4. A previsao no horizonte de teste e feita de forma recursiva, alimentando o modelo com a propria previsao passada.
5. Os resultados sao salvos em `results/`.

## Responsabilidades

- `model.py`
  Preparacao das sequencias, treino da rede e previsao.
- `run.py`
  Orquestracao do experimento completo.
- `test_model.py`
  Verificacao automatizada em uma serie sintetica.

## Valor didatico

Essa organizacao ajuda o leitor a ver claramente como uma rede recorrente aprende memoria treinavel, contrastando com RC, onde a dinamica principal nao e treinada.
