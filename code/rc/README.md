# RC

Implementacao didatica de Reservoir Computing classico para previsao de demanda no Favorita.

## Objetivo

Usar um reservatorio recorrente fixo com readout linear para prever demanda no mesmo recorte experimental usado pelos demais modelos da serie.

## Arquivos principais

- `STRUCTURE.md`: explica a arquitetura do codigo.
- `THEORY.md`: resume o fundamento teorico do RC implementado.
- `model.py`: define o reservatorio, o treino e a previsao.
- `run.py`: executa o experimento ponta a ponta.
- `test_model.py`: testes automatizados.
- `results/`: artefatos gerados pela execucao.

## Como executar

```bash
python /Users/anderson/Desktop/QRCNotebooks/favorita_reservoir_series/code/rc/run.py
```
