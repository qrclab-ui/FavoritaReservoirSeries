from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SequentialScalerState:
    y_mean: float
    y_std: float
    promo_mean: float
    promo_std: float


def _safe_std(value: float) -> float:
    return value if value > 1e-8 else 1.0


def build_scaler_state(train: pd.DataFrame) -> SequentialScalerState:
    return SequentialScalerState(
        y_mean=float(train["y"].mean()),
        y_std=_safe_std(float(train["y"].std(ddof=0))),
        promo_mean=float(train["onpromotion"].mean()),
        promo_std=_safe_std(float(train["onpromotion"].std(ddof=0))),
    )


def calendar_features(ds: pd.Timestamp) -> dict[str, float]:
    dow = ds.dayofweek
    month = ds.month
    return {
        "dow_sin": float(np.sin(2 * np.pi * dow / 7.0)),
        "dow_cos": float(np.cos(2 * np.pi * dow / 7.0)),
        "month_sin": float(np.sin(2 * np.pi * month / 12.0)),
        "month_cos": float(np.cos(2 * np.pi * month / 12.0)),
        "is_weekend": float(dow >= 5),
    }


def scaled_input_vector(
    prev_y: float,
    row: pd.Series,
    *,
    scaler: SequentialScalerState,
) -> np.ndarray:
    cal = calendar_features(pd.Timestamp(row["ds"]))
    return np.asarray(
        [
            float((prev_y - scaler.y_mean) / scaler.y_std),
            float((float(row["onpromotion"]) - scaler.promo_mean) / scaler.promo_std),
            cal["dow_sin"],
            cal["dow_cos"],
            cal["month_sin"],
            cal["month_cos"],
            cal["is_weekend"],
        ],
        dtype=float,
    )

