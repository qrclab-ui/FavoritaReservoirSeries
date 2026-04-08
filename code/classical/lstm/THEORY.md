# Fundamento teorico

A LSTM e uma variante de rede neural recorrente desenhada para lidar melhor com dependencias temporais.

## Ideia central

A LSTM mantem um estado interno atualizado ao longo do tempo e usa portas para decidir:

- o que lembrar;
- o que esquecer;
- o que expor na saida.

## Intuicao

Em previsao de demanda, isso permite que o modelo:

- combine padroes recentes e antigos;
- use o contexto temporal de forma treinavel;
- aprenda relacoes entre sequencia de vendas, promocao e calendario.

## O que ela captura bem

- dependencia temporal sequencial;
- relacoes nao lineares entre eventos ao longo do tempo;
- memoria treinavel.

## O que ela custa

- mais parametros;
- treino mais caro;
- maior sensibilidade a configuracao e seed;
- menor interpretabilidade do que modelos estatisticos simples.

## Papel didatico nesta serie

A LSTM e uma comparacao importante porque representa a estrategia classica de "treinar a memoria". Isso contrasta diretamente com RC, onde o reservatorio fornece dinamica rica e apenas o readout e ajustado.
