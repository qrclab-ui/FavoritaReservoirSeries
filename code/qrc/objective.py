from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


METRIC_KEYS = ("mae", "rmse", "wape", "smape")


@dataclass(frozen=True)
class ObjectiveConfig:
    mae_weight: float = 0.30
    rmse_weight: float = 0.30
    wape_weight: float = 0.20
    smape_weight: float = 0.20
    complexity_weight: float = 0.05
    qubit_bounds: tuple[int, int] = (4, 16)
    window_bounds: tuple[int, int] = (3, 13)
    reference_strategy: str = "best_non_qrc"

    @property
    def metric_weights(self) -> dict[str, float]:
        raw = {
            "mae": self.mae_weight,
            "rmse": self.rmse_weight,
            "wape": self.wape_weight,
            "smape": self.smape_weight,
        }
        total = sum(raw.values())
        if total <= 0:
            raise ValueError("Metric weights must sum to a positive value.")
        return {key: value / total for key, value in raw.items()}


@dataclass(frozen=True)
class ObjectiveResult:
    score: float
    metric_score: float
    complexity_penalty: float
    complexity_norm: float
    reference_metrics: dict[str, float]
    metric_ratios: dict[str, float]


def _results_root() -> Path:
    return Path(__file__).resolve().parents[1]


def benchmark_result_paths() -> dict[str, Path]:
    code_root = _results_root()
    return {
        "ETS": code_root / "baselines" / "ets" / "results" / "metrics.json",
        "Prophet": code_root / "baselines" / "prophet" / "results" / "metrics.json",
        "Seasonal Naive": code_root / "baselines" / "seasonal_naives" / "results" / "metrics.json",
        "XGBoost": code_root / "classical" / "xgboost" / "results" / "metrics.json",
        "LSTM": code_root / "classical" / "lstm" / "results" / "metrics.json",
        "RC": code_root / "rc" / "results" / "metrics.json",
        "QRC": code_root / "qrc" / "results" / "metrics.json",
    }


def load_benchmark_metrics(*, include_qrc: bool = False) -> dict[str, dict[str, float]]:
    panel: dict[str, dict[str, float]] = {}
    for model_name, path in benchmark_result_paths().items():
        if model_name == "QRC" and not include_qrc:
            continue
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        panel[model_name] = {metric: float(payload[metric]) for metric in METRIC_KEYS}
    if not panel:
        raise FileNotFoundError("No benchmark metrics were found to build the objective reference.")
    return panel


def build_reference_metrics(
    *,
    strategy: str = "best_non_qrc",
    panel: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, float]:
    active_panel = dict(panel or load_benchmark_metrics(include_qrc=False))
    if strategy == "best_non_qrc":
        return {
            metric: min(float(model_metrics[metric]) for model_metrics in active_panel.values())
            for metric in METRIC_KEYS
        }
    if strategy == "median_non_qrc":
        return {
            metric: sorted(float(model_metrics[metric]) for model_metrics in active_panel.values())[
                len(active_panel) // 2
            ]
            for metric in METRIC_KEYS
        }
    if strategy == "rc_only":
        if "RC" not in active_panel:
            raise KeyError("RC metrics are not available in the benchmark panel.")
        return {metric: float(active_panel["RC"][metric]) for metric in METRIC_KEYS}
    raise ValueError(f"Unsupported reference strategy: {strategy}")


def _coerce_metrics(metrics: Mapping[str, float]) -> dict[str, float]:
    coerced: dict[str, float] = {}
    for metric in METRIC_KEYS:
        if metric in metrics:
            coerced[metric] = float(metrics[metric])
            continue
        mean_key = f"mean_{metric}"
        if mean_key in metrics:
            coerced[metric] = float(metrics[mean_key])
            continue
        raise KeyError(f"Missing metric '{metric}' in metrics payload.")
    return coerced


def _normalize_complexity(value: int, bounds: tuple[int, int]) -> float:
    low, high = bounds
    if high <= low:
        return 0.0
    clipped = min(max(value, low), high)
    return (clipped - low) / (high - low)


def compute_qrc_objective(
    *,
    n_qubits: int,
    window: int,
    metrics: Mapping[str, float],
    reference_metrics: Mapping[str, float] | None = None,
    config: ObjectiveConfig | None = None,
) -> ObjectiveResult:
    active_config = config or ObjectiveConfig()
    references = _coerce_metrics(
        reference_metrics
        or build_reference_metrics(strategy=active_config.reference_strategy)
    )
    observed = _coerce_metrics(metrics)
    weights = active_config.metric_weights

    metric_ratios = {
        metric: max(observed[metric] / references[metric], 1e-12)
        for metric in METRIC_KEYS
    }
    metric_score = math.exp(
        sum(weights[metric] * math.log(metric_ratios[metric]) for metric in METRIC_KEYS)
    )

    complexity_norm = 0.5 * (
        _normalize_complexity(n_qubits, active_config.qubit_bounds)
        + _normalize_complexity(window, active_config.window_bounds)
    )
    complexity_penalty = 1.0 + active_config.complexity_weight * complexity_norm
    score = metric_score * complexity_penalty

    return ObjectiveResult(
        score=score,
        metric_score=metric_score,
        complexity_penalty=complexity_penalty,
        complexity_norm=complexity_norm,
        reference_metrics=references,
        metric_ratios=metric_ratios,
    )

