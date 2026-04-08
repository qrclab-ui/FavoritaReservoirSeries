# Artigo 3

## Titulo sugerido

Primeiro pipeline reproduzivel: previsao de demanda no Favorita com baselines e RC

## Pergunta central

Como montar um primeiro experimento simples, completo e reproduzivel de previsao de demanda?

## Contribuicao do artigo

Entregar o primeiro pipeline ponta a ponta da serie, saindo do dataset bruto para uma comparacao inicial entre baseline e RC em um recorte univariado ou quase univariado.

## O que o leitor aprende

- como escolher uma serie inicial dentro do Favorita;
- como fazer split temporal sem vazamento;
- como construir um baseline util;
- como rodar um primeiro modelo de RC com readout linear.

## Estrutura sugerida

1. Definicao do recorte inicial
   Escolher uma loja e uma familia de produto, ou um pequeno conjunto reproduzivel.
2. Preparacao dos dados
   Limpeza, ordenacao temporal, janela de treino e teste.
3. Baseline inicial
   Seasonal naive ou media movel como referencia minima.
4. Primeiro modelo de RC
   Configuracao simples e explicavel.
5. Resultados iniciais
   Comparar previsoes, erros e comportamento visual.
6. Interpretacao
   Mostrar o que RC ja captura e o que ainda nao captura.
7. Proximos passos
   Introduzir a necessidade de estudar memoria e nao linearidade.

## Entregaveis do artigo

- notebook reproduzivel;
- primeiro grafico de previsao vs. observado;
- tabela comparando baseline e RC;
- recorte experimental fixado para os artigos seguintes.
