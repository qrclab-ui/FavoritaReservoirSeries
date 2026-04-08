# Estrutura do codigo

Esta implementacao foi organizada para ser didatica e reutilizavel.

## Fluxo

1. `run.py` carrega o recorte padrao do Favorita.
2. O split temporal e feito com as funcoes compartilhadas em `code/common`.
3. `model.py` gera a previsao repetindo o ultimo ciclo sazonal observado no treino.
4. As metricas sao calculadas por `code/common/metrics.py`.
5. Os resultados sao salvos em `results/` como CSV, JSON e grafico.

## Responsabilidades

- `model.py`
  Implementa a regra de previsao e a funcao de avaliacao.
- `run.py`
  Orquestra leitura, treino, previsao, metricas e persistencia dos artefatos.
- `test_model.py`
  Verifica comportamento esperado em series sinteticas.

## Por que esta estrutura ajuda

Ela separa claramente:

- logica do modelo;
- infraestrutura de experimento;
- documentacao teorica;
- verificacao automatizada.
