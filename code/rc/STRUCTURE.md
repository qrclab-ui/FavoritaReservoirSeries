# Estrutura do codigo

Esta implementacao foi organizada para mostrar claramente o paradigma de Reservoir Computing.

## Fluxo

1. `run.py` carrega o recorte Favorita.
2. `common/sequential_features.py` gera os sinais de entrada sequenciais: demanda passada, promocao e calendario.
3. `model.py` constroi um reservatorio aleatorio fixo e treina apenas o readout linear.
4. A previsao do horizonte de teste e feita de forma recursiva, reaproveitando a previsao anterior como novo sinal de entrada.
5. As metricas e os artefatos sao salvos em `results/`.

## Responsabilidades

- `model.py`
  Define a dinamica do reservatorio, o ajuste do readout e a previsao recursiva.
- `run.py`
  Orquestra o experimento completo.
- `test_model.py`
  Valida o comportamento em series sinteticas.

## Valor didatico

Essa estrutura evidencia a principal ideia de RC:

- a dinamica rica fica no reservatorio fixo;
- o treino e concentrado em um readout simples;
- a memoria emerge da evolucao do estado interno.
