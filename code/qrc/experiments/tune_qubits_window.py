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

from common.favorita import load_store_family_series, temporal_train_test_split
from qrc.model import QRCConfig, run_qrc


def main() -> None:
    frame = load_store_family_series(store_nbr=1, family="BEVERAGES")
    train, test = temporal_train_test_split(frame, test_days=90)

    broad_qubit_grid = [5, 6, 7, 8, 10, 12, 14, 16]
    broad_window_grid = [3, 5, 7, 9, 11, 13]
    coarse_seed = [7]
    refine_seeds = [3, 7, 11]
    top_k = 8

    def run_grid(qubit_grid: list[int], window_grid: list[int], seeds: list[int]) -> pd.DataFrame:
        rows: list[dict[str, float | int]] = []
        for n_qubits in qubit_grid:
            for window in window_grid:
                for seed in seeds:
                    config = QRCConfig(
                        n_qubits=n_qubits,
                        window=window,
                        input_scale=1.2,
                        ridge_alpha=1e-1,
                        seed=seed,
                    )
                    result = run_qrc(train, test, config=config)
                    rows.append(
                        {
                            "n_qubits": n_qubits,
                            "window": window,
                            "seed": seed,
                            "mae": result.metrics["mae"],
                            "rmse": result.metrics["rmse"],
                            "wape": result.metrics["wape"],
                            "smape": result.metrics["smape"],
                        }
                    )
                    print(
                        f"done n_qubits={n_qubits} window={window} seed={seed} "
                        f"mae={result.metrics['mae']:.3f} rmse={result.metrics['rmse']:.3f}",
                        flush=True,
                    )
        return pd.DataFrame(rows)

    def summarize(runs: pd.DataFrame) -> pd.DataFrame:
        summary = (
            runs.groupby(["n_qubits", "window"], as_index=False)
            .agg(
                mean_mae=("mae", "mean"),
                std_mae=("mae", "std"),
                mean_rmse=("rmse", "mean"),
                std_rmse=("rmse", "std"),
                mean_wape=("wape", "mean"),
                std_wape=("wape", "std"),
                mean_smape=("smape", "mean"),
                std_smape=("smape", "std"),
            )
        )
        for metric in ["mean_mae", "mean_rmse", "mean_wape", "mean_smape"]:
            summary[f"rank_{metric}"] = summary[metric].rank(method="min", ascending=True)
        summary["avg_rank"] = summary[
            ["rank_mean_mae", "rank_mean_rmse", "rank_mean_wape", "rank_mean_smape"]
        ].mean(axis=1)
        return summary.sort_values(
            ["avg_rank", "mean_wape", "mean_rmse", "mean_mae"],
            ascending=[True, True, True, True],
        ).reset_index(drop=True)

    print("Running coarse search...", flush=True)
    coarse_runs = run_grid(broad_qubit_grid, broad_window_grid, coarse_seed)
    coarse_summary = summarize(coarse_runs)
    top_candidates = coarse_summary.head(top_k)[["n_qubits", "window"]]

    print("\nTop coarse candidates:", flush=True)
    print(top_candidates.to_string(index=False), flush=True)

    print("\nRunning refined search on top candidates...", flush=True)
    refined_rows: list[dict[str, float | int]] = []
    for row in top_candidates.to_dict(orient="records"):
        for seed in refine_seeds:
            config = QRCConfig(
                n_qubits=int(row["n_qubits"]),
                window=int(row["window"]),
                input_scale=1.2,
                ridge_alpha=1e-1,
                seed=seed,
            )
            result = run_qrc(train, test, config=config)
            refined_rows.append(
                {
                    "n_qubits": int(row["n_qubits"]),
                    "window": int(row["window"]),
                    "seed": seed,
                    "mae": result.metrics["mae"],
                    "rmse": result.metrics["rmse"],
                    "wape": result.metrics["wape"],
                    "smape": result.metrics["smape"],
                }
            )
            print(
                f"refined n_qubits={row['n_qubits']} window={row['window']} seed={seed} "
                f"mae={result.metrics['mae']:.3f} rmse={result.metrics['rmse']:.3f}",
                flush=True,
            )

    runs = pd.DataFrame(refined_rows)
    summary = summarize(runs)

    output_dir = Path(__file__).resolve().parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    coarse_runs_path = output_dir / "qrc_qubits_window_coarse_runs.csv"
    coarse_summary_path = output_dir / "qrc_qubits_window_coarse_summary.csv"
    runs_path = output_dir / "qrc_qubits_window_refined_runs.csv"
    summary_path = output_dir / "qrc_qubits_window_refined_summary.csv"
    best_path = output_dir / "qrc_best_qubits_window_extended.json"

    coarse_runs.to_csv(coarse_runs_path, index=False)
    coarse_summary.to_csv(coarse_summary_path, index=False)
    runs.to_csv(runs_path, index=False)
    summary.to_csv(summary_path, index=False)

    best_row = summary.iloc[0]
    best_payload = {
        "selection_rule": "lowest average rank across mean MAE, RMSE, WAPE, and sMAPE; tie-break by mean WAPE, then mean RMSE, then mean MAE",
        "broad_qubit_grid": broad_qubit_grid,
        "broad_window_grid": broad_window_grid,
        "coarse_seed": coarse_seed,
        "refine_seeds": refine_seeds,
        "top_k": top_k,
        "best": {
            "n_qubits": int(best_row["n_qubits"]),
            "window": int(best_row["window"]),
            "mean_mae": float(best_row["mean_mae"]),
            "mean_rmse": float(best_row["mean_rmse"]),
            "mean_wape": float(best_row["mean_wape"]),
            "mean_smape": float(best_row["mean_smape"]),
            "avg_rank": float(best_row["avg_rank"]),
        },
        "best_by_rmse": summary.sort_values("mean_rmse", ascending=True).iloc[0][
            ["n_qubits", "window", "mean_rmse", "mean_mae", "mean_wape", "mean_smape"]
        ].to_dict(),
        "best_by_mae": summary.sort_values("mean_mae", ascending=True).iloc[0][
            ["n_qubits", "window", "mean_rmse", "mean_mae", "mean_wape", "mean_smape"]
        ].to_dict(),
        "artifacts": {
            "coarse_runs_csv": str(coarse_runs_path),
            "coarse_summary_csv": str(coarse_summary_path),
            "refined_runs_csv": str(runs_path),
            "refined_summary_csv": str(summary_path),
        },
    }
    best_path.write_text(json.dumps(best_payload, indent=2))

    print("\nTop configurations:")
    print(summary.head(10).to_string(index=False))
    print("\nBest payload:")
    print(json.dumps(best_payload, indent=2))


if __name__ == "__main__":
    main()
