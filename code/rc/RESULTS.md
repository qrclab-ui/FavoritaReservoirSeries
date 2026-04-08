# Resultados do RC

## Recorte experimental

- dataset: Favorita `train.csv`
- serie: `store_nbr = 1`, `family = BEVERAGES`
- teste: ultimos 90 dias

## Configuracao usada

- `n_reservoir = 80`
- `spectral_radius = 0.6`
- `leak_rate = 0.15`
- `washout = 14`

## Metricas observadas

| Modelo | MAE | RMSE | WAPE | sMAPE |
| :-- | --: | --: | --: | --: |
| RC | 324.294 | 423.417 | 0.1498 | 0.1653 |

## Leitura inicial

- O RC superou a LSTM neste primeiro recorte, mas ficou abaixo dos melhores baselines estatisticos e do XGBoost.
- Isso e consistente com o objetivo didatico da serie: RC nao deve ser tratado como um atalho magico, mas como um paradigma a ser comparado honestamente.
