# XGBoost

Implementacao do baseline classico de gradient boosting para o recorte didatico do Favorita.

## Objetivo

Oferecer um modelo tabular forte, usando lags, medias moveis, calendario e promocao, no mesmo recorte usado pelos baselines estatisticos.

## Arquivos principais

- `STRUCTURE.md`: explica a arquitetura do codigo.
- `THEORY.md`: resume o fundamento teorico do XGBoost.
- `model.py`: implementa o treino e a previsao recursiva.
- `run.py`: executa o experimento ponta a ponta.
- `test_model.py`: testes automatizados.
- `results/`: artefatos gerados pela execucao.

## Como executar

```bash
python /Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/classical/xgboost/run.py
```
