from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from common.metrics import compute_metrics
from classical.shared import append_future_step, make_lstm_sequences, recursive_lstm_inputs


@dataclass(frozen=True)
class LSTMResult:
    predictions: pd.Series
    metrics: dict[str, float]


class DemandLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 32) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, batch_first=True)
        self.linear = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.lstm(x)
        last_hidden = output[:, -1, :]
        return self.linear(last_hidden).squeeze(-1)


def train_lstm_model(
    train: pd.DataFrame,
    *,
    lookback: int = 28,
    epochs: int = 80,
    batch_size: int = 32,
    lr: float = 1e-2,
) -> tuple[DemandLSTM, object]:
    torch.manual_seed(7)
    np.random.seed(7)

    x_train, y_train, scaler = make_lstm_sequences(train, lookback=lookback)
    dataset = TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = DemandLSTM(input_size=x_train.shape[-1], hidden_size=32)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            optimizer.zero_grad()
            preds = model(xb)
            loss = loss_fn(preds, yb)
            loss.backward()
            optimizer.step()
    return model, scaler


def recursive_lstm_forecast(
    model: DemandLSTM,
    train: pd.DataFrame,
    test: pd.DataFrame,
    scaler,
    *,
    lookback: int = 28,
) -> pd.Series:
    model.eval()
    history, future_rows = recursive_lstm_inputs(train, test, lookback=lookback, scaler=scaler)
    preds: list[float] = []
    with torch.no_grad():
        for row in future_rows:
            window = np.asarray(history[-lookback:], dtype=np.float32)
            x = torch.from_numpy(window[None, :, :])
            pred_scaled = float(model(x).item())
            pred = pred_scaled * scaler.y_std + scaler.y_mean
            pred = max(pred, 0.0)
            preds.append(pred)
            append_future_step(history, row, y_value=pred, scaler=scaler)
    return pd.Series(preds, name="y_pred")


def run_lstm(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    lookback: int = 28,
) -> LSTMResult:
    model, scaler = train_lstm_model(train, lookback=lookback)
    predictions = recursive_lstm_forecast(model, train, test, scaler, lookback=lookback)
    metrics = compute_metrics(test["y"].to_numpy(), predictions.to_numpy())
    return LSTMResult(predictions=predictions, metrics=metrics)
