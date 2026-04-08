# Estrutura do codigo

Esta implementacao organiza o QRC como um pipeline didatico, reproduzivel e comparavel com o RC classico.

## Fluxo

1. `run.py` carrega o recorte Favorita.
2. `common/sequential_features.py` gera a sequencia de sinais de entrada.
3. `model.py` monta um circuito quantico em Qiskit para uma janela curta de entradas com reuploading.
4. Observaveis quanticos sao convertidos em features classicas.
5. Um readout linear e treinado sobre essas features.
6. A previsao no teste e feita recursivamente.

## Responsabilidades

- `model.py`
  Circuito, observaveis, extracao de features, treino e previsao.
- `run.py`
  Orquestracao do experimento.
- `test_model.py`
  Validacao em uma serie sintetica.

## Valor didatico

Essa estrutura deixa explicito que:

- a dinamica rica vem da evolucao quantica;
- as medidas transformam estados quanticos em features classicas;
- o readout continua simples, preservando o espirito de RC.
