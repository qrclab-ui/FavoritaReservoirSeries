# Resultados do QRC

## Recorte experimental

- dataset: Favorita `train.csv`
- serie: `store_nbr = 1`, `family = BEVERAGES`
- teste: ultimos 90 dias

## Configuracao usada

- `n_qubits = 14`
- `window = 7`
- `input_scale = 1.2`
- `ridge_alpha = 0.1`

## Metricas observadas

| Modelo | MAE | RMSE | WAPE | sMAPE |
| :-- | --: | --: | --: | --: |
| QRC | 441.286 | 525.325 | 0.2038 | 0.2269 |

## Leitura inicial

- O QRC funcionou de ponta a ponta com Qiskit e gerou um benchmark reproduzivel no Favorita.
- A busca foi extrapolada ate `16` qubits e janelas maiores, e a validacao robusta com varias seeds em `qrc/experiments/TUNING.md` apontou `14` qubits com `window = 7` como a melhor configuracao balanceada.
- A extrapolacao melhorou o QRC em relacao ao padrao anterior de `8x5`, especialmente em `MAE`, `WAPE` e `sMAPE`.
- Neste primeiro recorte, ele ainda ficou abaixo dos modelos classicos e do RC.
- Isso e didaticamente importante: em um problema real de negocio, a comparacao precisa ser metodologicamente honesta, mesmo quando o resultado quantico inicial nao vence.
