# Resultados dos modelos classicos

## Recorte experimental

- dataset: Favorita `train.csv`
- serie: `store_nbr = 1`, `family = BEVERAGES`
- teste: ultimos 90 dias

## Metricas observadas

| Modelo | MAE | RMSE | WAPE | sMAPE |
| :-- | --: | --: | --: | --: |
| XGBoost | 256.666 | 332.828 | 0.1185 | 0.1237 |
| LSTM | 371.827 | 461.342 | 0.1717 | 0.1822 |

## Leitura inicial

- O XGBoost foi claramente mais forte do que a LSTM neste primeiro recorte.
- A LSTM ficou como um baseline neural valido, mas exigiria mais tuning para competir.
- Para a comparacao completa com baselines estatisticos, consulte `code/RESULTS.md`.
