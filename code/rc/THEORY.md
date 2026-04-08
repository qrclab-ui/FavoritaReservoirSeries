# Fundamento teorico

Reservoir Computing e um paradigma em que um sistema dinamico fixo transforma a entrada em um estado rico, e apenas uma camada de leitura e treinada.

## Ideia central

O reservatorio recebe uma entrada temporal `u_t` e atualiza um estado interno `x_t`.

Uma forma simples do modelo e:

`x_t = (1 - leak) * x_(t-1) + leak * tanh(W_res x_(t-1) + W_in u_t + b)`

Depois disso, um readout linear prediz a saida:

`y_hat_t = W_out [1, u_t, x_t]`

## Intuicao

O reservatorio funciona como um expansor dinamico de representacoes:

- mistura o passado recente e o presente;
- cria estados nao lineares;
- entrega ao readout um conjunto de features temporais ricas.

## O que e treinado

- somente `W_out`, o readout linear.

## O que fica fixo

- pesos de entrada;
- pesos recorrentes do reservatorio;
- vieses internos.

## Papel didatico nesta serie

Este codigo implementa o caso classico que servira de ponte natural para o QRC:

- no RC classico, o reservatorio e recorrente e real-valued;
- no QRC, a dinamica rica vem da evolucao quantica e das medidas.
