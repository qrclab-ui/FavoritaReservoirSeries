# Benchmark consolidado

## Recorte experimental comum

- dataset: Favorita `train.csv`
- serie: `store_nbr = 1`, `family = BEVERAGES`
- frequencia: diaria
- janela de teste: ultimos 90 dias
- objetivo: comparar todos os modelos no mesmo recorte e sob o mesmo split temporal

## Resultados

| Modelo | Familia | MAE | RMSE | WAPE | sMAPE |
| :-- | :-- | --: | --: | --: | --: |
| ETS | baseline estatistico | 216.303 | 307.638 | 0.0999 | 0.1042 |
| XGBoost | ML classico | 256.666 | 332.828 | 0.1185 | 0.1237 |
| Prophet | baseline estatistico | 257.584 | 321.818 | 0.1189 | 0.1319 |
| Seasonal Naive | baseline estatistico | 259.067 | 352.280 | 0.1196 | 0.1361 |
| RC | reservoir computing classico | 324.294 | 423.417 | 0.1498 | 0.1653 |
| LSTM | DL classico | 371.827 | 461.342 | 0.1717 | 0.1822 |
| QRC | reservoir computing quantico | 441.286 | 525.325 | 0.2038 | 0.2269 |

## Leitura inicial

- O ETS foi o melhor modelo neste primeiro recorte, liderando todas as metricas.
- O XGBoost e o Prophet ficaram competitivos e formam uma faixa intermediaria forte.
- O Seasonal Naive continuou sendo uma referencia importante e dificil de superar por larga margem.
- O RC classico funcionou de ponta a ponta e superou a LSTM, mas ainda ficou abaixo dos melhores modelos estatisticos e tabulares.
- O QRC, implementado com Qiskit, tambem funcionou de ponta a ponta. Depois de extrapolar a busca ate `16` qubits e janelas maiores, a melhor configuracao robusta passou a ser `14` qubits com `window = 7`, melhorando o resultado anterior do QRC, mas ainda ficando abaixo das alternativas classicas neste recorte.
- A LSTM, com configuracao simples e sem tuning pesado, ficou abaixo dos demais modelos mais fortes. Isso e pedagogicamente util para mostrar que redes recorrentes nao vencem automaticamente em series pequenas e com pouco ajuste.

## Implicacao para a serie

Este benchmark define um ponto de referencia concreto para os proximos artigos:

- RC e QRC nao devem ser comparados apenas com baselines fracos;
- o protocolo atual ja inclui referencias estatisticas, ML tabular e DL sequencial;
- o benchmark agora ja inclui RC classico e QRC em um problema de negocio real;
- qualquer ganho futuro deve ser interpretado frente a esta tabela.
