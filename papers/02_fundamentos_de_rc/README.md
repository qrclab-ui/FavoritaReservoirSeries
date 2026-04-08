# Artigo 2

## Titulo sugerido

Fundamentos de Reservoir Computing: da intuicao ao modelo minimo

## Pergunta central

O que e computacao de reservatorio e por que ela pode ser util para problemas temporais?

## Contribuicao do artigo

Apresentar RC de forma didatica, com o minimo de formalismo necessario, conectando entrada, estado, dinamica e readout ao problema de previsao de demanda.

## O que o leitor aprende

- a intuicao de um reservatorio como expansor dinamico de features;
- o que e treinado e o que nao e treinado;
- o papel de memoria, nao linearidade e readout;
- como mapear RC para forecasting.

## Estrutura sugerida

1. Motivacao conceitual
   Explicar por que nem todo problema temporal precisa treinar toda a dinamica.
2. Intuicao de RC
   Apresentar o reservatorio como sistema dinamico fixo.
3. Formula minimo
   Definir entrada, estado interno, observacao e readout.
4. Como o tempo entra no modelo
   Explicar memoria, washout e dependencia temporal.
5. Exemplo de brinquedo
   Usar uma serie simples para mostrar como o estado evolui.
6. Ligacao com o caso Favorita
   Mostrar como uma serie de demanda pode alimentar o reservatorio.
7. Limites e promessas do paradigma
   Preparar o leitor para um primeiro experimento.

## Entregaveis do artigo

- diagrama do pipeline de RC;
- equacoes minimas do modelo;
- pseudocodigo curto;
- explicacao de como RC sera usado no Artigo 3.
