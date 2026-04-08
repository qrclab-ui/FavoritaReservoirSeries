from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from common.metrics import compute_metrics


@dataclass(frozen=True)
class ETSResult:
    predictions: pd.Series
    metrics: dict[str, float]


def fit_predict_ets(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    season_length: int = 7,
) -> pd.Series:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    model = ExponentialSmoothing(
        train["y"].to_numpy(),
        trend="add",
        seasonal="add",
        seasonal_periods=season_length,
        initialization_method="estimated",
    )
    fitted = model.fit(optimized=True)
    forecast = fitted.forecast(len(test))
    clipped = np.clip(forecast, a_min=0.0, a_max=None)
    return pd.Series(clipped, name="y_pred")


def run_ets(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    season_length: int = 7,
) -> ETSResult:
    predictions = fit_predict_ets(train, test, season_length=season_length)
    metrics = compute_metrics(test["y"].to_numpy(), predictions.to_numpy())
    return ETSResult(predictions=predictions, metrics=metrics)
