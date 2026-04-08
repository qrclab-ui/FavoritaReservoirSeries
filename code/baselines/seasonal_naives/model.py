from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from common.metrics import compute_metrics


@dataclass(frozen=True)
class SeasonalNaiveResult:
    predictions: pd.Series
    metrics: dict[str, float]


def seasonal_naive_forecast(train: pd.DataFrame, horizon: int, *, season_length: int = 7) -> pd.Series:
    if season_length <= 0:
        raise ValueError("season_length must be positive")
    if len(train) < season_length:
        raise ValueError("train series must be at least one season long")
    pattern = train["y"].to_numpy()[-season_length:]
    repeats = int(np.ceil(horizon / season_length))
    forecast = np.tile(pattern, repeats)[:horizon]
    return pd.Series(forecast, name="y_pred")


def run_seasonal_naive(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    season_length: int = 7,
) -> SeasonalNaiveResult:
    predictions = seasonal_naive_forecast(train, len(test), season_length=season_length)
    metrics = compute_metrics(test["y"].to_numpy(), predictions.to_numpy())
    return SeasonalNaiveResult(predictions=predictions, metrics=metrics)
