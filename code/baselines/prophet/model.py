from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from common.metrics import compute_metrics


@dataclass(frozen=True)
class ProphetResult:
    predictions: pd.Series
    metrics: dict[str, float]


def fit_predict_prophet(train: pd.DataFrame, test: pd.DataFrame) -> pd.Series:
    from prophet import Prophet

    model = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="additive",
        uncertainty_samples=0,
    )
    model.add_regressor("onpromotion")
    model.fit(train[["ds", "y", "onpromotion"]])
    forecast = model.predict(test[["ds", "onpromotion"]])
    clipped = np.clip(forecast["yhat"].to_numpy(), a_min=0.0, a_max=None)
    return pd.Series(clipped, name="y_pred")


def run_prophet(train: pd.DataFrame, test: pd.DataFrame) -> ProphetResult:
    predictions = fit_predict_prophet(train, test)
    metrics = compute_metrics(test["y"].to_numpy(), predictions.to_numpy())
    return ProphetResult(predictions=predictions, metrics=metrics)
