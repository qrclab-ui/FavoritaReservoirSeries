# Resultados Computacionais do Artigo 2

Este pacote combina artefatos internos do reservatorio com uma primeira leitura quantitativa da qualidade experimental do RC.

Ele cobre quatro frentes:
- os sinais de entrada usados por RC/QRC;
- a evolucao de estados internos do reservatorio classico;
- o posicionamento inicial do RC contra referencias fortes;
- a sensibilidade a seed, `washout` e pequenos ajustes de hiperparametros.

Arquivos gerados:
- `sequential_inputs_sample.csv` e `sequential_inputs_example.png`.
- `rc_state_sample.csv` e `rc_state_heatmap.png`.
- `rc_quality_preview.csv`: RC, Seasonal Naive e ETS lado a lado.
- `rc_seed_stability_runs.csv` e `rc_seed_stability_summary.csv`: estabilidade em 10 seeds.
- `rc_washout_sweep.csv`: impacto do washout com a configuracao base.
