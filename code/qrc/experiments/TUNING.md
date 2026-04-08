# Tuning de qubits e janela do QRC

## Objetivo

Encontrar valores mais robustos para `n_qubits` e `window` no recorte Favorita usado pela serie.

## Protocolo

- dataset: Favorita `train.csv`
- serie: `store_nbr = 1`, `family = BEVERAGES`
- teste: ultimos 90 dias
- `input_scale = 1.2`
- `ridge_alpha = 0.1`
- busca ampliada de `n_qubits`: `5, 6, 7, 8, 10, 12, 14, 16`
- busca ampliada de `window`: `3, 5, 7, 9, 11, 13`
- validacao focalizada com `seeds = 3, 7, 11` nas configuracoes mais promissoras

## Regra de selecao

As configuracoes foram ordenadas por:

1. menor media de rank em `MAE`, `RMSE`, `WAPE` e `sMAPE`;
2. desempate por menor `WAPE` medio;
3. depois menor `RMSE` medio;
4. depois menor `MAE` medio.

## Resumo dos resultados medios da validacao focalizada

| n_qubits | window | mean MAE | mean RMSE | mean WAPE | mean sMAPE | avg rank |
| :-- | :-- | --: | --: | --: | --: | --: |
| 14 | 7 | 436.819 | 522.161 | 0.2017 | 0.2265 | 1.25 |
| 12 | 9 | 445.061 | 524.709 | 0.2055 | 0.2306 | 2.25 |
| 5 | 7 | 445.920 | 530.752 | 0.2059 | 0.2313 | 3.50 |
| 8 | 5 | 447.947 | 520.913 | 0.2068 | 0.2313 | 3.50 |
| 12 | 3 | 447.168 | 540.572 | 0.2065 | 0.2319 | 4.50 |
| 16 | 5 | 464.763 | 554.138 | 0.2146 | 0.2409 | 6.50 |
| 16 | 7 | 465.764 | 552.452 | 0.2151 | 0.2425 | 7.00 |

## Melhor configuracao balanceada

- `n_qubits = 14`
- `window = 7`

Essa combinacao foi a melhor pelo criterio balanceado, liderando `MAE`, `WAPE` e `sMAPE`, e ficando em segundo lugar em `RMSE`.

## Melhor configuracao por RMSE medio

- `n_qubits = 8`
- `window = 5`

Ela manteve o menor `RMSE` medio, mas perdeu em robustez geral quando consideramos todas as metricas ao mesmo tempo.

## O que a extrapolacao mostrou

- Aumentar ate `16` qubits e janelas mais longas nao garantiu melhora robusta.
- `16x7` teve um run isolado forte, mas piorou bastante quando olhamos a media em varias seeds.
- O melhor ponto robusto apareceu em `14x7`, nao no limite maximo de qubits testado.

## Conclusao pratica

Para manter um unico padrao no codigo e no benchmark da serie, a configuracao adotada foi:

- `n_qubits = 14`
- `window = 7`

Essa escolha representa o melhor compromisso encontrado depois da extrapolacao da busca ate `16` qubits.

## Observacao sobre funcao objetivo escalar

Tambem foi implementada uma funcao objetivo escalar em `/Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/qrc/objective.py`, documentada em `/Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/qrc/OBJECTIVE.md`.

Ela combina as quatro metricas com uma penalizacao leve de complexidade. Com esse criterio, o melhor ponto do conjunto focal ficou em `8` qubits com `window = 5`, enquanto o criterio puramente multi-metrica deste arquivo continua favorecendo `14x7`.
