# Fundamento teorico

O Prophet modela uma serie temporal como uma soma de componentes interpretaveis.

## Forma geral

Em alto nivel, a previsao pode ser vista como:

`y(t) = tendencia + sazonalidades + feriados/eventos + regressoras + erro`

## Intuicao

Isso e interessante para previsao de demanda porque separa:

- crescimento ou mudanca lenta de patamar;
- padroes sazonais, como semana e ano;
- eventos conhecidos;
- sinais externos, como promocoes.

## O que o Prophet captura

- tendencia com pontos de mudanca;
- sazonalidades multiplas;
- regressoras adicionais;
- interpretabilidade razoavel.

## O que ele nao captura tao bem

- dinamicas altamente nao lineares de curto prazo;
- dependencias internas muito ricas como em alguns modelos recorrentes;
- interacoes complexas nao especificadas.

## Papel didatico nesta serie

O Prophet serve como uma referencia forte e popular de mercado. Comparar RC e QRC contra ele ajuda a posicionar os resultados em um contexto que muitos leitores ja conhecem.
