# Fundamento teorico

O XGBoost e um metodo de gradient boosting sobre arvores de decisao.

## Ideia central

Em vez de treinar uma unica arvore forte, o modelo treina varias arvores pequenas em sequencia. Cada nova arvore tenta corrigir os erros cometidos pelas anteriores.

## Intuicao para forecasting

Quando convertemos a serie temporal em um conjunto de atributos, como:

- lags da demanda;
- medias moveis;
- calendario;
- promocoes;

o problema passa a ser uma regressao supervisionada. O XGBoost entao aprende combinacoes nao lineares entre esses sinais.

## O que ele captura bem

- interacoes nao lineares;
- efeitos de threshold;
- combinacoes entre lags e variaveis exogenas;
- comportamento robusto em dados tabulares.

## O que ele nao resolve sozinho

- dependencia temporal longa sem boa engenharia de atributos;
- estrutura sequencial explicita como em modelos recorrentes;
- extrapolacao estrutural fora do padrao visto.

## Papel didatico nesta serie

O XGBoost e um benchmark muito importante porque e forte, popular no mercado e serve como referencia competitiva antes de comparar com RC e QRC.
