from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from common.metrics import compute_metrics
from classical.shared import make_tabular_supervised, recursive_tabular_forecast, tabular_feature_names


@dataclass(frozen=True)
class XGBoostResult:
    predictions: pd.Series
    metrics: dict[str, float]


def build_xgb_regressor():
    from xgboost import XGBRegressor

    return XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=7,
        n_jobs=1,
    )


def run_xgboost(train: pd.DataFrame, test: pd.DataFrame) -> XGBoostResult:
    x_train, y_train = make_tabular_supervised(train)
    x_train = x_train[tabular_feature_names()]
    model = build_xgb_regressor()
    model.fit(x_train, y_train)
    predictions = recursive_tabular_forecast(model, train, test)
    metrics = compute_metrics(test["y"].to_numpy(), predictions.to_numpy())
    return XGBoostResult(predictions=predictions, metrics=metrics)
