from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from common.metrics import compute_metrics
from common.sequential_features import build_scaler_state, scaled_input_vector


@dataclass(frozen=True)
class RCConfig:
    n_reservoir: int = 80
    spectral_radius: float = 0.6
    leak_rate: float = 0.15
    input_scale: float = 0.8
    bias_scale: float = 0.1
    washout: int = 14
    ridge_alpha: float = 1e-3
    seed: int = 7


@dataclass(frozen=True)
class RCResult:
    predictions: pd.Series
    metrics: dict[str, float]


class EchoStateReservoir:
    def __init__(self, input_dim: int, config: RCConfig) -> None:
        rng = np.random.default_rng(config.seed)
        self.config = config
        self.state = np.zeros(config.n_reservoir, dtype=float)
        self.input_weights = rng.uniform(
            -config.input_scale,
            config.input_scale,
            size=(config.n_reservoir, input_dim),
        )
        recurrent = rng.uniform(-1.0, 1.0, size=(config.n_reservoir, config.n_reservoir))
        eigvals = np.linalg.eigvals(recurrent)
        radius = float(np.max(np.abs(eigvals)))
        self.recurrent_weights = recurrent * (config.spectral_radius / radius)
        self.bias = rng.uniform(-config.bias_scale, config.bias_scale, size=config.n_reservoir)

    def step(self, input_vector: np.ndarray) -> np.ndarray:
        pre_activation = (
            self.recurrent_weights @ self.state
            + self.input_weights @ input_vector
            + self.bias
        )
        new_state = np.tanh(pre_activation)
        self.state = (1.0 - self.config.leak_rate) * self.state + self.config.leak_rate * new_state
        return self.state.copy()


def _feature_vector(state: np.ndarray, input_vector: np.ndarray) -> np.ndarray:
    return np.concatenate([[1.0], input_vector, state])


def fit_rc_readout(train: pd.DataFrame, *, config: RCConfig) -> tuple[EchoStateReservoir, Ridge, object]:
    scaler = build_scaler_state(train)
    reservoir = EchoStateReservoir(input_dim=7, config=config)
    feature_rows: list[np.ndarray] = []
    targets: list[float] = []

    prev_y = float(train.iloc[0]["y"])
    for idx in range(1, len(train)):
        row = train.iloc[idx]
        input_vector = scaled_input_vector(prev_y, row, scaler=scaler)
        state = reservoir.step(input_vector)
        if idx >= config.washout:
            feature_rows.append(_feature_vector(state, input_vector))
            targets.append(float(row["y"]))
        prev_y = float(row["y"])

    readout = Ridge(alpha=config.ridge_alpha)
    readout.fit(np.vstack(feature_rows), np.asarray(targets))
    return reservoir, readout, scaler


def forecast_rc(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    config: RCConfig,
) -> pd.Series:
    reservoir, readout, scaler = fit_rc_readout(train, config=config)
    preds: list[float] = []
    prev_y = float(train.iloc[-1]["y"])
    for idx in range(len(test)):
        row = test.iloc[idx]
        input_vector = scaled_input_vector(prev_y, row, scaler=scaler)
        state = reservoir.step(input_vector)
        pred = float(readout.predict(_feature_vector(state, input_vector)[None, :])[0])
        pred = max(pred, 0.0)
        preds.append(pred)
        prev_y = pred
    return pd.Series(preds, name="y_pred")


def run_rc(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    config: RCConfig | None = None,
) -> RCResult:
    active_config = config or RCConfig()
    predictions = forecast_rc(train, test, config=active_config)
    metrics = compute_metrics(test["y"].to_numpy(), predictions.to_numpy())
    return RCResult(predictions=predictions, metrics=metrics)
