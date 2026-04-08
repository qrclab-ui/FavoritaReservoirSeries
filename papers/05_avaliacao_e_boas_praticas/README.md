# Artigo 5

## Titulo sugerido

Avaliacao justa em previsao de demanda: baselines, IA classica e Reservoir Computing

## Pergunta central

Como comparar modelos temporais de maneira justa, util e reproduzivel?

## Contribuicao do artigo

Definir o protocolo experimental oficial da serie e estabelecer a comparacao entre baselines, modelos classicos e RC antes da passagem para QRC.

## O que o leitor aprende

- como evitar vazamento temporal;
- como escolher metricas certas;
- como comparar desempenho estatistico e valor de negocio;
- como interpretar custo computacional e estabilidade.

## Estrutura sugerida

1. Por que avaliacao em series temporais e delicada
   Mostrar erros comuns e vazamento.
2. Definicao do protocolo temporal
   Treino, validacao, teste e, se possivel, rolling origin.
3. Metricas de previsao e negocio
   MAE, RMSE, WAPE, MAPE e uma metrica ligada a estoque.
4. Modelos comparados
   Seasonal naive, ETS, Prophet, XGBoost, LSTM e RC.
5. Resultados comparativos
   Tabelas, boxplots e analise de variancia entre seeds.
6. Discussao
   Quando RC ganha, quando perde e por que isso importa.
7. Regras para a fase QRC
   Fixar o protocolo que sera herdado pelo Artigo 7.

## Entregaveis do artigo

- protocolo experimental formalizado;
- benchmark comparativo inicial da serie;
- checklist de boas praticas;
- definicao do subconjunto que sera usado no QRC.
