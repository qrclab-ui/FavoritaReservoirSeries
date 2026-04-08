# Funcao objetivo para tuning do QRC

## Objetivo

Transformar `MAE`, `RMSE`, `WAPE` e `sMAPE` em um unico escalar que possa ser minimizado ao ajustar `n_qubits` e `window`.

## Forma recomendada

Para uma configuracao `x = (n_qubits, window)`, defina:

- `m_k(x)` como a metrica observada do QRC para `k in {MAE, RMSE, WAPE, sMAPE}`
- `r_k` como a metrica de referencia vinda do benchmark nao quantico
- `w_k` como o peso de cada metrica, com `sum_k w_k = 1`

A funcao objetivo implementada e:

`J(x) = G(x) * C(x)`

onde

`G(x) = exp(sum_k w_k * log(m_k(x) / r_k))`

e

`C(x) = 1 + lambda * 0.5 * (norm_qubits(x) + norm_window(x))`

## Interpretacao

- `G(x)` e a media geometrica ponderada das razoes entre o QRC e a referencia.
- `G(x) = 1` significa que o QRC igualou a referencia nas metricas escolhidas.
- `G(x) > 1` significa que o QRC ainda esta pior que a referencia.
- `C(x)` adiciona uma penalizacao leve por complexidade para evitar escolher mais qubits e janelas maiores sem ganho real.

## Parametros usados no projeto

- pesos: `MAE = 0.30`, `RMSE = 0.30`, `WAPE = 0.20`, `sMAPE = 0.20`
- penalizacao de complexidade: `lambda = 0.05`
- faixa de qubits: `4` a `16`
- faixa de janela: `3` a `13`
- referencia padrao: melhor resultado entre os modelos nao-QRC no benchmark atual

## Local da implementacao

- codigo: `/Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/qrc/objective.py`
- script de pontuacao: `/Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/qrc/experiments/score_objective.py`

## Resultado atual com esse criterio

No conjunto focal de configuracoes ja testadas:

- o criterio puramente multi-metrica escolheu `14` qubits com `window = 7`
- a funcao objetivo escalar com penalizacao leve de complexidade escolheu `8` qubits com `window = 5`

Isso mostra duas visoes complementares:

- `14x7` e melhor quando o foco e apertar as metricas do QRC
- `8x5` e melhor quando se quer um compromisso entre qualidade e custo de complexidade
