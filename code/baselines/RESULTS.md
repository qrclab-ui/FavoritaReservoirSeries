# Resultados iniciais dos baselines

## Recorte experimental

- dataset: Favorita `train.csv`
- serie: `store_nbr = 1`, `family = BEVERAGES`
- frequencia: diaria
- janela de teste: ultimos 90 dias
- sazonalidade principal considerada: 7 dias

## Metricas observadas

| Modelo | MAE | RMSE | WAPE | sMAPE |
| :-- | --: | --: | --: | --: |
| Seasonal Naive | 259.067 | 352.280 | 0.1196 | 0.1361 |
| ETS | 216.303 | 307.638 | 0.0999 | 0.1042 |
| Prophet | 257.584 | 321.818 | 0.1189 | 0.1319 |

## Leitura inicial

- O ETS foi o melhor dos tres neste recorte, superando tanto o Seasonal Naive quanto o Prophet em todas as metricas principais.
- O Seasonal Naive continua sendo uma referencia importante, porque fixa um piso honesto para o problema.
- O Prophet ficou proximo do Seasonal Naive, mas nao ultrapassou o ETS neste primeiro experimento.

## Artefatos gerados

- `seasonal_naives/results/`
- `ets/results/`
- `prophet/results/`

Cada pasta contem:

- `predictions.csv`
- `metrics.json`
- `forecast_plot.png`

## Benchmark completo

Para a comparacao consolidada com os modelos classicos implementados depois, consulte:

- `/Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/RESULTS.md`
