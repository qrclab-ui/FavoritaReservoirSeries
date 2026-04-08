# Code

Esta pasta organiza os modelos que serao comparados ao longo da serie.

## Estrutura

- `common/`: utilitarios compartilhados, metricas, splits e configuracoes.
- `baselines/`: metodos simples de referencia.
- `classical/`: modelos classicos de IA/ML.
- `rc/`: modelos de Reservoir Computing classico.
- `qrc/`: modelos de Quantum Reservoir Computing.

## Protocolo sugerido

Todos os modelos devem usar:

1. o mesmo subconjunto do dataset;
2. o mesmo split temporal;
3. as mesmas metricas principais;
4. a mesma janela de previsao;
5. a mesma definicao de variaveis exogenas.
