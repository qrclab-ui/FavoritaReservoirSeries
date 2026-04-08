from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from classical.lstm.model import run_lstm


class LSTMTests(unittest.TestCase):
    def _make_series(self, periods: int = 180) -> pd.DataFrame:
        dates = pd.date_range("2023-01-01", periods=periods, freq="D")
        idx = np.arange(periods)
        weekly = np.sin(2 * np.pi * idx / 7.0)
        promo = (idx % 21 < 3).astype(float)
        y = 150 + 12 * weekly + 10 * promo + 0.25 * idx
        return pd.DataFrame({"ds": dates, "y": y, "onpromotion": promo})

    def test_lstm_forecast_length_matches_test(self) -> None:
        frame = self._make_series()
        train = frame.iloc[:-21].reset_index(drop=True)
        test = frame.iloc[-21:].reset_index(drop=True)
        result = run_lstm(train, test, lookback=21)
        self.assertEqual(len(result.predictions), len(test))

    def test_lstm_runs_on_simple_series(self) -> None:
        frame = self._make_series(200)
        train = frame.iloc[:-28].reset_index(drop=True)
        test = frame.iloc[-28:].reset_index(drop=True)
        result = run_lstm(train, test, lookback=28)
        self.assertTrue(math.isfinite(result.metrics["mae"]))
        self.assertLess(result.metrics["mae"], 35.0)


if __name__ == "__main__":
    unittest.main()
