# ETS

Implementacao do baseline ETS para o recorte didatico do dataset Favorita.

## Objetivo

Oferecer um baseline estatistico mais forte do que o seasonal naive, capturando nivel, tendencia e sazonalidade.

## Arquivos principais

- `STRUCTURE.md`: organiza o fluxo da implementacao.
- `THEORY.md`: apresenta o fundamento teorico do ETS.
- `model.py`: fit e previsao com Exponential Smoothing.
- `run.py`: executa o pipeline completo no Favorita.
- `test_model.py`: testes automatizados do modelo.
- `results/`: artefatos gerados pela execucao.

## Como executar

```bash
python /Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/baselines/ets/run.py
```
