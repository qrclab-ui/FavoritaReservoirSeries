from __future__ import annotations

import json
import math
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = PROJECT_ROOT / "code"

import sys

if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from common.favorita import FavoritaSeriesConfig, load_store_family_series, temporal_train_test_split
from common.sequential_features import build_scaler_state, scaled_input_vector
from rc.model import EchoStateReservoir, RCConfig, run_rc


PAPERS_ROOT = PROJECT_ROOT / "papers"
RESULTS_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULTS_DIRNAME = f"computational_results_{RESULTS_TIMESTAMP}"


MODEL_SOURCES = {
    "ETS": CODE_ROOT / "baselines" / "ets" / "results",
    "Prophet": CODE_ROOT / "baselines" / "prophet" / "results",
    "Seasonal Naive": CODE_ROOT / "baselines" / "seasonal_naives" / "results",
    "XGBoost": CODE_ROOT / "classical" / "xgboost" / "results",
    "LSTM": CODE_ROOT / "classical" / "lstm" / "results",
    "RC": CODE_ROOT / "rc" / "results",
    "QRC14x7": CODE_ROOT / "qrc" / "results",
}

ARTICLE_DIRS = {
    "01": PAPERS_ROOT / "01_motivacao_e_negocio",
    "02": PAPERS_ROOT / "02_fundamentos_de_rc",
    "03": PAPERS_ROOT / "03_primeiro_modelo_previsao",
    "04": PAPERS_ROOT / "04_memoria_nao_linearidade",
    "05": PAPERS_ROOT / "05_avaliacao_e_boas_praticas",
    "06": PAPERS_ROOT / "06_rc_fisico_e_ponte_para_qrc",
    "07": PAPERS_ROOT / "07_qrc_para_previsao_de_demanda",
}


def _savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def load_model_outputs() -> dict[str, dict[str, object]]:
    outputs: dict[str, dict[str, object]] = {}
    for model_name, result_dir in MODEL_SOURCES.items():
        metrics_path = result_dir / "metrics.json"
        predictions_path = result_dir / "predictions.csv"
        plot_path = result_dir / "forecast_plot.png"
        outputs[model_name] = {
            "metrics": json.loads(metrics_path.read_text()),
            "predictions": pd.read_csv(predictions_path, parse_dates=["ds"]),
            "plot_path": plot_path,
        }
    return outputs


def summarize_seed_runs(seed_runs: pd.DataFrame) -> pd.DataFrame:
    summary = (
        seed_runs.groupby("config")
        .agg(
            n_seeds=("seed", "count"),
            mae_mean=("mae", "mean"),
            mae_std=("mae", "std"),
            mae_median=("mae", "median"),
            mae_min=("mae", "min"),
            mae_max=("mae", "max"),
            rmse_mean=("rmse", "mean"),
            rmse_std=("rmse", "std"),
            wape_mean=("wape", "mean"),
            wape_std=("wape", "std"),
            smape_mean=("smape", "mean"),
            smape_std=("smape", "std"),
        )
        .reset_index()
    )
    return summary


def run_qrc_8x5(train: pd.DataFrame, test: pd.DataFrame) -> dict[str, object]:
    from qrc.model import QRCConfig, run_qrc

    config = QRCConfig(n_qubits=8, window=5, input_scale=1.2, ridge_alpha=1e-1, seed=7)
    result = run_qrc(train, test, config=config)
    predictions = test[["ds", "y"]].copy()
    predictions["y_pred"] = result.predictions.to_numpy()
    return {
        "config": asdict(config),
        "metrics": result.metrics,
        "predictions": predictions,
    }


def benchmark_frame(model_outputs: dict[str, dict[str, object]], qrc_8x5: dict[str, object]) -> pd.DataFrame:
    rows = []
    family_map = {
        "ETS": "baseline estatistico",
        "Prophet": "baseline estatistico",
        "Seasonal Naive": "baseline estatistico",
        "XGBoost": "ML classico",
        "LSTM": "DL classico",
        "RC": "reservoir computing classico",
        "QRC14x7": "reservoir computing quantico",
        "QRC8x5": "reservoir computing quantico",
    }
    for model_name, payload in model_outputs.items():
        metrics = payload["metrics"]
        rows.append(
            {
                "model": model_name,
                "family": family_map[model_name],
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "wape": metrics["wape"],
                "smape": metrics["smape"],
            }
        )
    rows.append(
        {
            "model": "QRC8x5",
            "family": family_map["QRC8x5"],
            "mae": qrc_8x5["metrics"]["mae"],
            "rmse": qrc_8x5["metrics"]["rmse"],
            "wape": qrc_8x5["metrics"]["wape"],
            "smape": qrc_8x5["metrics"]["smape"],
        }
    )
    frame = pd.DataFrame(rows).sort_values(["mae", "rmse"]).reset_index(drop=True)
    return frame


def generate_article_01(output_dir: Path, frame: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> None:
    report_lines = []
    report_lines.append("# Resultados Computacionais do Artigo 1")
    report_lines.append("")
    report_lines.append("Este pacote apresenta evidencias descritivas do recorte de negocio usado em toda a serie.")
    report_lines.append("")

    summary = pd.DataFrame(
        [
            {"metric": "n_total_days", "value": len(frame)},
            {"metric": "train_days", "value": len(train)},
            {"metric": "test_days", "value": len(test)},
            {"metric": "mean_sales", "value": frame["y"].mean()},
            {"metric": "std_sales", "value": frame["y"].std(ddof=0)},
            {"metric": "promotion_rate", "value": frame["onpromotion"].gt(0).mean()},
            {"metric": "zero_sales_rate", "value": frame["y"].eq(0).mean()},
            {"metric": "train_start", "value": train["ds"].min().date().isoformat()},
            {"metric": "test_start", "value": test["ds"].min().date().isoformat()},
            {"metric": "test_end", "value": test["ds"].max().date().isoformat()},
        ]
    )
    summary.to_csv(output_dir / "recorte_summary.csv", index=False)

    plt.figure(figsize=(12, 4.5))
    plt.plot(frame["ds"], frame["y"], color="#1b4965", linewidth=1.2, label="demanda")
    plt.axvspan(test["ds"].min(), test["ds"].max(), color="#f4a261", alpha=0.20, label="janela de teste")
    plt.title("Serie completa do recorte Favorita (store 1, BEVERAGES)")
    plt.xlabel("Data")
    plt.ylabel("Vendas")
    plt.legend()
    plt.grid(alpha=0.25)
    _savefig(output_dir / "series_overview.png")

    weekly = frame.assign(
        dow=frame["ds"].dt.day_name(),
        promo_flag=np.where(frame["onpromotion"] > 0, "com promocao", "sem promocao"),
    )
    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly["dow"] = pd.Categorical(weekly["dow"], categories=ordered_days, ordered=True)
    weekly_profile = weekly.groupby(["dow", "promo_flag"], observed=False)["y"].mean().reset_index()

    pivot = weekly_profile.pivot(index="dow", columns="promo_flag", values="y").fillna(0.0)
    pivot.to_csv(output_dir / "weekly_profile.csv")

    ax = pivot.plot(kind="bar", figsize=(11, 4.5), color=["#577590", "#e76f51"])
    ax.set_title("Demanda media por dia da semana com e sem promocao")
    ax.set_xlabel("Dia da semana")
    ax.set_ylabel("Vendas medias")
    ax.grid(axis="y", alpha=0.25)
    _savefig(output_dir / "weekly_profile.png")

    report_lines.append("Arquivos gerados:")
    report_lines.append("- `recorte_summary.csv`: estatisticas descritivas do recorte.")
    report_lines.append("- `series_overview.png`: serie completa com destaque para a janela de teste.")
    report_lines.append("- `weekly_profile.csv` e `weekly_profile.png`: comparacao da demanda media por dia da semana com e sem promocao.")
    (output_dir / "REPORT.md").write_text("\n".join(report_lines) + "\n")


def generate_article_02(output_dir: Path, train: pd.DataFrame, test: pd.DataFrame) -> None:
    scaler = build_scaler_state(train)
    rc_config = RCConfig()
    reservoir = EchoStateReservoir(input_dim=7, config=rc_config)

    input_rows = []
    states = []
    prev_y = float(train.iloc[0]["y"])
    for idx in range(1, min(len(train), 220)):
        row = train.iloc[idx]
        input_vector = scaled_input_vector(prev_y, row, scaler=scaler)
        state = reservoir.step(input_vector)
        input_rows.append(
            {
                "ds": row["ds"],
                "prev_y_scaled": input_vector[0],
                "promo_scaled": input_vector[1],
                "dow_sin": input_vector[2],
                "dow_cos": input_vector[3],
                "month_sin": input_vector[4],
                "month_cos": input_vector[5],
                "is_weekend": input_vector[6],
            }
        )
        states.append(state[:20])
        prev_y = float(row["y"])

    inputs = pd.DataFrame(input_rows)
    inputs.to_csv(output_dir / "sequential_inputs_sample.csv", index=False)
    state_df = pd.DataFrame(states, columns=[f"state_{i}" for i in range(20)])
    state_df.insert(0, "ds", inputs["ds"])
    state_df.to_csv(output_dir / "rc_state_sample.csv", index=False)

    plt.figure(figsize=(12, 4.8))
    for col, color in [
        ("prev_y_scaled", "#1b4965"),
        ("promo_scaled", "#e76f51"),
        ("dow_sin", "#2a9d8f"),
        ("dow_cos", "#8d99ae"),
    ]:
        plt.plot(inputs["ds"], inputs[col], label=col, linewidth=1.5, color=color)
    plt.title("Exemplo de sinais de entrada sequencial para RC/QRC")
    plt.xlabel("Data")
    plt.ylabel("Valor normalizado")
    plt.legend(ncol=2)
    plt.grid(alpha=0.25)
    _savefig(output_dir / "sequential_inputs_example.png")

    plt.figure(figsize=(12, 5.2))
    plt.imshow(np.asarray(states).T, aspect="auto", cmap="viridis", interpolation="nearest")
    plt.colorbar(label="Ativacao")
    plt.title("Heatmap da evolucao de 20 estados do reservatorio classico")
    plt.xlabel("Passos temporais")
    plt.ylabel("Unidades do reservatorio")
    _savefig(output_dir / "rc_state_heatmap.png")

    preview = pd.DataFrame(
        [
            {"model": "ETS", **json.loads((MODEL_SOURCES["ETS"] / "metrics.json").read_text())},
            {
                "model": "Seasonal Naive",
                **json.loads((MODEL_SOURCES["Seasonal Naive"] / "metrics.json").read_text()),
            },
            {"model": "RC", **json.loads((MODEL_SOURCES["RC"] / "metrics.json").read_text())},
        ]
    )
    preview.to_csv(output_dir / "rc_quality_preview.csv", index=False)

    seed_configurations = [
        ("RC default (sr=0.60, leak=0.15)", RCConfig()),
        ("RC mais contido (sr=0.20, leak=0.15)", RCConfig(spectral_radius=0.2)),
        ("RC mais contido e mais rapido (sr=0.20, leak=0.30)", RCConfig(spectral_radius=0.2, leak_rate=0.3)),
    ]
    seed_rows = []
    for label, base_config in seed_configurations:
        for seed in range(1, 11):
            active_config = RCConfig(**{**asdict(base_config), "seed": seed})
            result = run_rc(train, test, config=active_config)
            seed_rows.append({"config": label, "seed": seed, **result.metrics})
    seed_runs = pd.DataFrame(seed_rows)
    seed_runs.to_csv(output_dir / "rc_seed_stability_runs.csv", index=False)
    seed_summary = summarize_seed_runs(seed_runs)
    seed_summary.to_csv(output_dir / "rc_seed_stability_summary.csv", index=False)

    washout_rows = []
    for washout in [0, 7, 14, 21, 28, 42]:
        result = run_rc(train, test, config=RCConfig(seed=7, washout=washout))
        washout_rows.append({"washout": washout, **result.metrics})
    washout_frame = pd.DataFrame(washout_rows)
    washout_frame.to_csv(output_dir / "rc_washout_sweep.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))

    preview_order = preview.set_index("model").loc[["ETS", "Seasonal Naive", "RC"]].reset_index()
    axes[0].bar(
        preview_order["model"],
        preview_order["mae"],
        color=["#2a9d8f", "#8d99ae", "#e76f51"],
    )
    axes[0].set_title("Posicionamento inicial do RC no recorte")
    axes[0].set_ylabel("MAE")
    axes[0].grid(axis="y", alpha=0.25)

    summary_order = seed_summary.set_index("config").loc[[label for label, _ in seed_configurations]].reset_index()
    for idx, label in enumerate(summary_order["config"]):
        values = seed_runs.loc[seed_runs["config"] == label, "mae"].to_numpy()
        xs = np.linspace(idx - 0.12, idx + 0.12, num=len(values))
        axes[1].scatter(xs, values, color="#1b4965", alpha=0.55, s=24)
    axes[1].errorbar(
        range(len(summary_order)),
        summary_order["mae_mean"],
        yerr=summary_order["mae_std"],
        fmt="o",
        color="#e76f51",
        ecolor="#e76f51",
        elinewidth=2.0,
        capsize=4,
        markersize=6,
    )
    axes[1].axhline(
        float(preview_order.loc[preview_order["model"] == "Seasonal Naive", "mae"].iloc[0]),
        color="#8d99ae",
        linestyle="--",
        linewidth=1.4,
        label="Seasonal Naive",
    )
    axes[1].axhline(
        float(preview_order.loc[preview_order["model"] == "ETS", "mae"].iloc[0]),
        color="#2a9d8f",
        linestyle=":",
        linewidth=1.6,
        label="ETS",
    )
    axes[1].set_xticks(range(len(summary_order)))
    axes[1].set_xticklabels(
        ["default", "sr=0.20", "sr=0.20\nleak=0.30"],
        rotation=0,
    )
    axes[1].set_title("Sensibilidade do MAE a seed e ajuste simples")
    axes[1].set_ylabel("MAE")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend()
    _savefig(output_dir / "rc_quality_snapshot.png")

    report = [
        "# Resultados Computacionais do Artigo 2",
        "",
        "Este pacote combina artefatos internos do reservatorio com uma primeira leitura quantitativa da qualidade experimental do RC.",
        "",
        "Ele cobre quatro frentes:",
        "- os sinais de entrada usados por RC/QRC;",
        "- a evolucao de estados internos do reservatorio classico.",
        "- o posicionamento inicial do RC contra referencias fortes;",
        "- a sensibilidade a seed, `washout` e pequenos ajustes de hiperparametros.",
        "",
        "Arquivos gerados:",
        "- `sequential_inputs_sample.csv` e `sequential_inputs_example.png`.",
        "- `rc_state_sample.csv` e `rc_state_heatmap.png`.",
        "- `rc_quality_preview.csv`: RC, Seasonal Naive e ETS lado a lado.",
        "- `rc_seed_stability_runs.csv` e `rc_seed_stability_summary.csv`: estabilidade em 10 seeds.",
        "- `rc_washout_sweep.csv`: impacto do washout com a configuracao base.",
        "- `rc_quality_snapshot.png`: posicionamento quantitativo e sensibilidade do RC.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(report) + "\n")


def _joined_forecasts(test: pd.DataFrame, payloads: dict[str, pd.DataFrame]) -> pd.DataFrame:
    merged = test[["ds", "y"]].copy()
    for name, pred_frame in payloads.items():
        merged[name] = pred_frame["y_pred"].to_numpy()
    return merged


def generate_article_03(output_dir: Path, test: pd.DataFrame, model_outputs: dict[str, dict[str, object]]) -> None:
    comparison = pd.DataFrame(
        [
            {"model": "Seasonal Naive", **model_outputs["Seasonal Naive"]["metrics"]},
            {"model": "RC", **model_outputs["RC"]["metrics"]},
        ]
    )
    comparison.to_csv(output_dir / "baseline_vs_rc_metrics.csv", index=False)

    joined = _joined_forecasts(
        test,
        {
            "seasonal_naive": model_outputs["Seasonal Naive"]["predictions"],
            "rc": model_outputs["RC"]["predictions"],
        },
    )
    joined.to_csv(output_dir / "baseline_vs_rc_predictions.csv", index=False)

    plt.figure(figsize=(12, 4.8))
    plt.plot(joined["ds"], joined["y"], label="observed", color="#1b4965", linewidth=2.2)
    plt.plot(joined["ds"], joined["seasonal_naive"], label="Seasonal Naive", color="#f4a261", linewidth=1.8)
    plt.plot(joined["ds"], joined["rc"], label="RC", color="#e76f51", linewidth=1.8)
    plt.title("Comparacao direta entre Seasonal Naive e RC")
    plt.xlabel("Data")
    plt.ylabel("Vendas")
    plt.legend()
    plt.grid(alpha=0.25)
    _savefig(output_dir / "baseline_vs_rc_overlay.png")

    for model_name in ["Seasonal Naive", "RC"]:
        shutil.copy2(model_outputs[model_name]["plot_path"], output_dir / f"{model_name.lower().replace(' ', '_')}_forecast_plot.png")

    report = [
        "# Resultados Computacionais do Artigo 3",
        "",
        "Comparacao do primeiro pipeline reproduzivel entre o baseline sazonal e o RC.",
        "",
        "Arquivos gerados:",
        "- `baseline_vs_rc_metrics.csv`: metricas lado a lado.",
        "- `baseline_vs_rc_predictions.csv`: observado e previsoes alinhadas.",
        "- `baseline_vs_rc_overlay.png`: comparacao visual direta.",
        "- copias dos graficos individuais de Seasonal Naive e RC.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(report) + "\n")


def generate_article_04(output_dir: Path, train: pd.DataFrame, test: pd.DataFrame) -> None:
    base = RCConfig()
    sweeps = {
        "n_reservoir": [40, 80, 120, 160],
        "spectral_radius": [0.2, 0.4, 0.6, 0.8, 1.0],
        "leak_rate": [0.05, 0.10, 0.15, 0.30, 0.50],
    }
    colors = {"mae": "#1b4965", "rmse": "#e76f51", "wape": "#2a9d8f", "smape": "#8d99ae"}

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    for ax, (param, values) in zip(axes, sweeps.items()):
        rows = []
        for value in values:
            kwargs = asdict(base)
            kwargs[param] = value
            result = run_rc(train, test, config=RCConfig(**kwargs))
            row = {"parameter": param, "value": value, **result.metrics}
            rows.append(row)
        frame = pd.DataFrame(rows)
        frame.to_csv(output_dir / f"rc_sweep_{param}.csv", index=False)
        for metric in ["mae", "rmse"]:
            ax.plot(frame["value"], frame[metric], marker="o", label=metric.upper(), linewidth=1.8, color=colors[metric])
        ax.set_title(f"Sensibilidade de RC em {param}")
        ax.set_xlabel(param)
        ax.grid(alpha=0.25)
        if param == "n_reservoir":
            ax.set_ylabel("Erro")
    axes[0].legend()
    _savefig(output_dir / "rc_sensitivity_summary.png")

    report = [
        "# Resultados Computacionais do Artigo 4",
        "",
        "Estudo de sensibilidade de hiperparametros do RC em torno da configuracao base.",
        "",
        "Arquivos gerados:",
        "- `rc_sweep_n_reservoir.csv`.",
        "- `rc_sweep_spectral_radius.csv`.",
        "- `rc_sweep_leak_rate.csv`.",
        "- `rc_sensitivity_summary.png`: comparacao visual dos sweeps.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(report) + "\n")


def generate_article_05(output_dir: Path, benchmark: pd.DataFrame, model_outputs: dict[str, dict[str, object]], test: pd.DataFrame) -> None:
    benchmark.to_csv(output_dir / "benchmark_metrics.csv", index=False)
    ranked = benchmark.copy()
    ranked["rank_mae"] = ranked["mae"].rank(method="min")
    ranked["rank_rmse"] = ranked["rmse"].rank(method="min")
    ranked["rank_wape"] = ranked["wape"].rank(method="min")
    ranked["rank_smape"] = ranked["smape"].rank(method="min")
    ranked["avg_rank"] = ranked[["rank_mae", "rank_rmse", "rank_wape", "rank_smape"]].mean(axis=1)
    ranked.to_csv(output_dir / "benchmark_ranked.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    metrics = [("mae", "MAE"), ("rmse", "RMSE"), ("wape", "WAPE"), ("smape", "sMAPE")]
    for ax, (metric, title) in zip(axes.ravel(), metrics):
        order = benchmark.sort_values(metric)
        ax.bar(order["model"], order[metric], color="#1b4965")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", alpha=0.25)
    _savefig(output_dir / "benchmark_metric_bars.png")

    chosen = ["ETS", "Prophet", "XGBoost", "RC", "QRC14x7", "LSTM"]
    fig, axes = plt.subplots(3, 2, figsize=(14, 11))
    for ax, model_name in zip(axes.ravel(), chosen):
        pred = model_outputs[model_name]["predictions"]
        ax.plot(test["ds"], test["y"], color="#1b4965", linewidth=1.8, label="observed")
        ax.plot(pred["ds"], pred["y_pred"], color="#e76f51", linewidth=1.6, label=model_name)
        ax.set_title(model_name)
        ax.grid(alpha=0.25)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2)
    _savefig(output_dir / "benchmark_forecast_grid.png")

    report = [
        "# Resultados Computacionais do Artigo 5",
        "",
        "Benchmark comparativo consolidado para os modelos avaliados na serie.",
        "",
        "Arquivos gerados:",
        "- `benchmark_metrics.csv`.",
        "- `benchmark_ranked.csv`.",
        "- `benchmark_metric_bars.png`.",
        "- `benchmark_forecast_grid.png`.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(report) + "\n")


def generate_article_06(output_dir: Path, test: pd.DataFrame, model_outputs: dict[str, dict[str, object]], qrc_8x5: dict[str, object]) -> None:
    focus_summary = pd.read_csv(CODE_ROOT / "qrc" / "experiments" / "results" / "qrc_qubits_window_focus_summary.csv")
    focus_summary.to_csv(output_dir / "qrc_focus_summary.csv", index=False)
    shutil.copy2(CODE_ROOT / "qrc" / "experiments" / "results" / "qrc_best_objective.json", output_dir / "qrc_best_objective.json")
    shutil.copy2(CODE_ROOT / "qrc" / "experiments" / "results" / "qrc_best_qubits_window_extended.json", output_dir / "qrc_best_qubits_window_extended.json")

    pivot = focus_summary.pivot(index="n_qubits", columns="window", values="avg_rank")
    plt.figure(figsize=(8.5, 5.2))
    plt.imshow(pivot.values, aspect="auto", cmap="magma_r", interpolation="nearest")
    plt.xticks(range(len(pivot.columns)), pivot.columns)
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label="avg_rank")
    plt.xlabel("window")
    plt.ylabel("n_qubits")
    plt.title("Heatmap do tuning focal QRC (avg_rank)")
    _savefig(output_dir / "qrc_tuning_heatmap.png")

    plt.figure(figsize=(12, 4.8))
    plt.plot(test["ds"], test["y"], label="observed", color="#1b4965", linewidth=2.2)
    plt.plot(model_outputs["RC"]["predictions"]["ds"], model_outputs["RC"]["predictions"]["y_pred"], label="RC", color="#2a9d8f", linewidth=1.8)
    plt.plot(model_outputs["QRC14x7"]["predictions"]["ds"], model_outputs["QRC14x7"]["predictions"]["y_pred"], label="QRC 14x7", color="#e76f51", linewidth=1.8)
    plt.plot(qrc_8x5["predictions"]["ds"], qrc_8x5["predictions"]["y_pred"], label="QRC 8x5", color="#f4a261", linewidth=1.5)
    plt.title("RC versus QRC no recorte final da serie")
    plt.xlabel("Data")
    plt.ylabel("Vendas")
    plt.legend()
    plt.grid(alpha=0.25)
    _savefig(output_dir / "rc_vs_qrc_overlay.png")

    report = [
        "# Resultados Computacionais do Artigo 6",
        "",
        "Artefatos que ajudam a construir a ponte entre RC classico e QRC.",
        "",
        "Arquivos gerados:",
        "- `qrc_focus_summary.csv` e JSONs do tuning.",
        "- `qrc_tuning_heatmap.png`.",
        "- `rc_vs_qrc_overlay.png`.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(report) + "\n")


def generate_article_07(output_dir: Path, benchmark: pd.DataFrame, test: pd.DataFrame, model_outputs: dict[str, dict[str, object]], qrc_8x5: dict[str, object]) -> None:
    final_table = benchmark.copy()
    final_table.to_csv(output_dir / "qrc_final_benchmark.csv", index=False)
    qrc_compare = pd.DataFrame(
        [
            {"model": "QRC14x7", **model_outputs["QRC14x7"]["metrics"]},
            {"model": "QRC8x5", **qrc_8x5["metrics"]},
            {"model": "RC", **model_outputs["RC"]["metrics"]},
            {"model": "ETS", **model_outputs["ETS"]["metrics"]},
            {"model": "XGBoost", **model_outputs["XGBoost"]["metrics"]},
        ]
    )
    qrc_compare.to_csv(output_dir / "qrc_focus_comparison.csv", index=False)

    plt.figure(figsize=(10, 4.8))
    plt.plot(test["ds"], test["y"], color="#1b4965", linewidth=2.2, label="observed")
    plt.plot(model_outputs["QRC14x7"]["predictions"]["ds"], model_outputs["QRC14x7"]["predictions"]["y_pred"], color="#e76f51", linewidth=1.8, label="QRC 14x7")
    plt.plot(qrc_8x5["predictions"]["ds"], qrc_8x5["predictions"]["y_pred"], color="#f4a261", linewidth=1.8, label="QRC 8x5")
    plt.title("Comparacao direta entre as duas configuracoes finais de QRC")
    plt.xlabel("Data")
    plt.ylabel("Vendas")
    plt.legend()
    plt.grid(alpha=0.25)
    _savefig(output_dir / "qrc_14x7_vs_8x5.png")

    order = qrc_compare.sort_values("mae")
    plt.figure(figsize=(8, 4.8))
    plt.bar(order["model"], order["mae"], color="#1b4965")
    plt.title("MAE das configuracoes finais de QRC e referencias proximas")
    plt.ylabel("MAE")
    plt.grid(axis="y", alpha=0.25)
    _savefig(output_dir / "qrc_focus_mae_bars.png")

    shutil.copy2(CODE_ROOT / "qrc" / "experiments" / "results" / "qrc_qubits_window_focus_summary.csv", output_dir / "qrc_qubits_window_focus_summary.csv")
    shutil.copy2(CODE_ROOT / "qrc" / "experiments" / "results" / "qrc_best_objective.json", output_dir / "qrc_best_objective.json")
    shutil.copy2(CODE_ROOT / "qrc" / "experiments" / "results" / "qrc_best_qubits_window_extended.json", output_dir / "qrc_best_qubits_window_extended.json")

    report = [
        "# Resultados Computacionais do Artigo 7",
        "",
        "Pacote final de resultados para o estudo didatico de QRC com o Favorita.",
        "",
        "Arquivos gerados:",
        "- `qrc_final_benchmark.csv`.",
        "- `qrc_focus_comparison.csv`.",
        "- `qrc_14x7_vs_8x5.png`.",
        "- `qrc_focus_mae_bars.png`.",
        "- artefatos do tuning e da funcao objetivo do QRC.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(report) + "\n")


def create_output_dir(article_key: str) -> Path:
    path = ARTICLE_DIRS[article_key] / RESULTS_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def main() -> None:
    favorita_config = FavoritaSeriesConfig()
    frame = load_store_family_series(store_nbr=favorita_config.store_nbr, family=favorita_config.family)
    train, test = temporal_train_test_split(frame, test_days=favorita_config.test_days)
    model_outputs = load_model_outputs()
    qrc_8x5 = run_qrc_8x5(train, test)
    benchmark = benchmark_frame(model_outputs, qrc_8x5)

    generate_article_01(create_output_dir("01"), frame, train, test)
    generate_article_02(create_output_dir("02"), train, test)
    generate_article_03(create_output_dir("03"), test, model_outputs)
    generate_article_04(create_output_dir("04"), train, test)
    generate_article_05(create_output_dir("05"), benchmark, model_outputs, test)
    generate_article_06(create_output_dir("06"), test, model_outputs, qrc_8x5)
    generate_article_07(create_output_dir("07"), benchmark, test, model_outputs, qrc_8x5)

    manifest = {
        "timestamp": RESULTS_TIMESTAMP,
        "dirname": RESULTS_DIRNAME,
        "articles": {key: str(ARTICLE_DIRS[key] / RESULTS_DIRNAME) for key in sorted(ARTICLE_DIRS)},
    }
    (PAPERS_ROOT / f"computational_results_manifest_{RESULTS_TIMESTAMP}.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
