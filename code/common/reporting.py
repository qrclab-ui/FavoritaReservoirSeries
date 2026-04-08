from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_results(
    *,
    model_name: str,
    output_dir: Path,
    train: pd.DataFrame,
    test: pd.DataFrame,
    predictions: pd.Series,
    metrics: dict[str, float],
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    pred_frame = test[["ds", "y"]].copy()
    pred_frame["y_pred"] = predictions.to_numpy()
    predictions_path = output_dir / "predictions.csv"
    metrics_path = output_dir / "metrics.json"
    plot_path = output_dir / "forecast_plot.png"

    pred_frame.to_csv(predictions_path, index=False)
    metrics_path.write_text(json.dumps(metrics, indent=2))

    context_train = train.tail(120)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(context_train["ds"], context_train["y"], label="train tail", color="#6C757D")
    ax.plot(test["ds"], test["y"], label="observed", color="#1B4965", linewidth=2.0)
    ax.plot(test["ds"], predictions, label=f"{model_name} forecast", color="#E76F51", linewidth=2.0)
    ax.set_title(f"{model_name} on Favorita (store 1, BEVERAGES)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    return {
        "predictions": predictions_path,
        "metrics": metrics_path,
        "plot": plot_path,
    }
