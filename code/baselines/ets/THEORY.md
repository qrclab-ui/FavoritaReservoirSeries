# Fundamento teorico

ETS significa Error, Trend, Seasonality. Na pratica, essa familia modela uma serie temporal decompondo-a em componentes atualizados recursivamente ao longo do tempo.

## Ideia central

Um modelo ETS tenta representar a serie como combinacao de:

- nivel;
- tendencia;
- sazonalidade;
- ruido.

Na variante Holt-Winters aditiva, a previsao combina essas partes por soma.

## Intuicao

Para demanda no varejo, isso e util porque:

- existe um nivel medio de vendas;
- pode haver mudanca gradual de patamar;
- ha padroes sazonais, como ciclo semanal;
- ha ruido de operacao e comportamento do consumidor.

## O que o ETS captura

- nivel dinamico;
- tendencia suave;
- sazonalidade recorrente;
- atualizacao gradual da serie.

## O que ele nao captura bem

- efeitos exogenos fortes sem extensao adicional;
- mudancas muito abruptas;
- interacoes nao lineares complexas.

## Papel didatico nesta serie

O ETS e uma excelente ponte entre baselines simples e modelos mais sofisticados. Se RC ou QRC quiserem mostrar valor, precisam competir com referencias estatisticas fortes como esta.
