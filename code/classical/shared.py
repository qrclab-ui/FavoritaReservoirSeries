from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


LAG_STEPS = (1, 7, 14, 28)
ROLLING_WINDOWS = (7, 14, 28)


@dataclass(frozen=True)
class ScalerState:
    y_mean: float
    y_std: float
    promo_mean: float
    promo_std: float


def _safe_std(value: float) -> float:
    return value if value > 1e-8 else 1.0


def build_scaler_state(train: pd.DataFrame) -> ScalerState:
    return ScalerState(
        y_mean=float(train["y"].mean()),
        y_std=_safe_std(float(train["y"].std(ddof=0))),
        promo_mean=float(train["onpromotion"].mean()),
        promo_std=_safe_std(float(train["onpromotion"].std(ddof=0))),
    )


def _calendar_features(ds: pd.Timestamp) -> dict[str, float]:
    dow = ds.dayofweek
    month = ds.month
    return {
        "dow_sin": float(np.sin(2 * np.pi * dow / 7.0)),
        "dow_cos": float(np.cos(2 * np.pi * dow / 7.0)),
        "month_sin": float(np.sin(2 * np.pi * month / 12.0)),
        "month_cos": float(np.cos(2 * np.pi * month / 12.0)),
        "is_weekend": float(dow >= 5),
    }


def tabular_feature_names() -> list[str]:
    names = [f"lag_{step}" for step in LAG_STEPS]
    names += [f"rolling_mean_{window}" for window in ROLLING_WINDOWS]
    names += ["onpromotion", "dow_sin", "dow_cos", "month_sin", "month_cos", "is_weekend"]
    return names


def tabular_feature_row(history: list[float], row: pd.Series) -> dict[str, float]:
    if len(history) < max(LAG_STEPS):
        raise ValueError("history is shorter than the largest configured lag")

    features = {f"lag_{step}": float(history[-step]) for step in LAG_STEPS}
    for window in ROLLING_WINDOWS:
        features[f"rolling_mean_{window}"] = float(np.mean(history[-window:]))
    features["onpromotion"] = float(row["onpromotion"])
    features.update(_calendar_features(pd.Timestamp(row["ds"])))
    return features


def make_tabular_supervised(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    history = train["y"].tolist()
    records: list[dict[str, float]] = []
    targets: list[float] = []
    for idx in range(max(LAG_STEPS), len(train)):
        row = train.iloc[idx]
        features = tabular_feature_row(history[:idx], row)
        records.append(features)
        targets.append(float(row["y"]))
    return pd.DataFrame.from_records(records), pd.Series(targets, name="y")


def recursive_tabular_forecast(model, train: pd.DataFrame, test: pd.DataFrame) -> pd.Series:
    history = train["y"].tolist()
    preds: list[float] = []
    names = tabular_feature_names()
    for idx in range(len(test)):
        row = test.iloc[idx]
        features = tabular_feature_row(history, row)
        frame = pd.DataFrame([[features[name] for name in names]], columns=names)
        pred = float(model.predict(frame)[0])
        pred = max(pred, 0.0)
        preds.append(pred)
        history.append(pred)
    return pd.Series(preds, name="y_pred")


def sequence_feature_columns(frame: pd.DataFrame, scaler: ScalerState) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["y_scaled"] = (enriched["y"] - scaler.y_mean) / scaler.y_std
    enriched["promo_scaled"] = (enriched["onpromotion"] - scaler.promo_mean) / scaler.promo_std
    calendar = enriched["ds"].apply(_calendar_features).apply(pd.Series)
    enriched = pd.concat([enriched, calendar], axis=1)
    return enriched[["y_scaled", "promo_scaled", "dow_sin", "dow_cos", "month_sin", "month_cos", "is_weekend"]]


def make_lstm_sequences(train: pd.DataFrame, *, lookback: int) -> tuple[np.ndarray, np.ndarray, ScalerState]:
    scaler = build_scaler_state(train)
    features = sequence_feature_columns(train, scaler).to_numpy(dtype=np.float32)
    targets = ((train["y"] - scaler.y_mean) / scaler.y_std).to_numpy(dtype=np.float32)

    xs: list[np.ndarray] = []
    ys: list[float] = []
    for idx in range(lookback, len(train)):
        xs.append(features[idx - lookback : idx])
        ys.append(float(targets[idx]))
    return np.stack(xs), np.asarray(ys, dtype=np.float32), scaler


def recursive_lstm_inputs(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    lookback: int,
    scaler: ScalerState,
) -> tuple[list[list[float]], list[pd.Series]]:
    history = sequence_feature_columns(train, scaler).to_numpy(dtype=np.float32).tolist()
    future_rows = [test.iloc[idx] for idx in range(len(test))]
    if len(history) < lookback:
        raise ValueError("lookback is larger than the training history")
    return history, future_rows


def append_future_step(
    history: list[list[float]],
    row: pd.Series,
    *,
    y_value: float,
    scaler: ScalerState,
) -> None:
    cal = _calendar_features(pd.Timestamp(row["ds"]))
    history.append(
        [
            float((y_value - scaler.y_mean) / scaler.y_std),
            float((float(row["onpromotion"]) - scaler.promo_mean) / scaler.promo_std),
            cal["dow_sin"],
            cal["dow_cos"],
            cal["month_sin"],
            cal["month_cos"],
            cal["is_weekend"],
        ]
    )
