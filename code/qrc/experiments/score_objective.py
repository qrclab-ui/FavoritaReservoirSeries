from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from qrc.objective import ObjectiveConfig, build_reference_metrics, compute_qrc_objective


def main() -> None:
    results_dir = Path(__file__).resolve().parent / "results"
    input_path = results_dir / "qrc_qubits_window_focus_summary.csv"
    if not input_path.exists():
        raise FileNotFoundError(f"Expected tuning summary at {input_path}")

    frame = pd.read_csv(input_path)
    objective_config = ObjectiveConfig(reference_strategy="best_non_qrc")
    reference_metrics = build_reference_metrics(strategy=objective_config.reference_strategy)

    rows: list[dict[str, float | int]] = []
    for row in frame.to_dict(orient="records"):
        result = compute_qrc_objective(
            n_qubits=int(row["n_qubits"]),
            window=int(row["window"]),
            metrics=row,
            reference_metrics=reference_metrics,
            config=objective_config,
        )
        enriched = dict(row)
        enriched["objective_score"] = result.score
        enriched["objective_metric_score"] = result.metric_score
        enriched["objective_complexity_penalty"] = result.complexity_penalty
        enriched["objective_complexity_norm"] = result.complexity_norm
        rows.append(enriched)

    scored = pd.DataFrame(rows).sort_values("objective_score", ascending=True).reset_index(drop=True)
    output_csv = results_dir / "qrc_objective_focus_summary.csv"
    scored.to_csv(output_csv, index=False)

    best_row = scored.iloc[0]
    best_payload = {
        "selection_rule": (
            "lowest objective_score where objective_score = geometric mean of normalized "
            "metric ratios times a small complexity penalty"
        ),
        "reference_strategy": objective_config.reference_strategy,
        "reference_metrics": reference_metrics,
        "objective_config": {
            "mae_weight": objective_config.mae_weight,
            "rmse_weight": objective_config.rmse_weight,
            "wape_weight": objective_config.wape_weight,
            "smape_weight": objective_config.smape_weight,
            "complexity_weight": objective_config.complexity_weight,
            "qubit_bounds": list(objective_config.qubit_bounds),
            "window_bounds": list(objective_config.window_bounds),
        },
        "best": {
            "n_qubits": int(best_row["n_qubits"]),
            "window": int(best_row["window"]),
            "objective_score": float(best_row["objective_score"]),
            "mean_mae": float(best_row["mean_mae"]),
            "mean_rmse": float(best_row["mean_rmse"]),
            "mean_wape": float(best_row["mean_wape"]),
            "mean_smape": float(best_row["mean_smape"]),
        },
        "artifact": str(output_csv),
    }
    output_json = results_dir / "qrc_best_objective.json"
    output_json.write_text(json.dumps(best_payload, indent=2))

    print(scored[[
        "n_qubits",
        "window",
        "objective_score",
        "mean_mae",
        "mean_rmse",
        "mean_wape",
        "mean_smape",
    ]].to_string(index=False))
    print("\nBest objective payload:")
    print(json.dumps(best_payload, indent=2))


if __name__ == "__main__":
    main()

