# Fundamento teorico

O Seasonal Naive e um baseline classico em previsao de series temporais.

## Ideia central

Se a serie possui uma sazonalidade dominante de periodo `s`, a previsao para o instante futuro `t + h` e o valor observado um periodo sazonal antes.

Em notacao simples:

`y_hat(t + h) = y(t + h - s)`

## Intuicao

Em demanda de varejo, padroes semanais sao comuns:

- segunda costuma se parecer com segunda;
- sabado costuma se parecer com sabado;
- domingo costuma se parecer com domingo.

Por isso, um baseline semanal com `s = 7` e um teste importante. Se um modelo mais complexo nao supera essa referencia, ele provavelmente nao esta agregando valor.

## O que ele captura

- sazonalidade dominante;
- repeticao de padroes de curto prazo;
- estrutura temporal minima sem treino.

## O que ele nao captura

- tendencia;
- mudancas estruturais;
- feriados moveis;
- promocoes;
- efeitos exogenos.

## Papel didatico nesta serie

Este baseline define o piso de qualidade para os demais modelos. Ele ensina que, antes de falar em RC, QRC ou IA classica, precisamos vencer uma referencia simples e honesta.
