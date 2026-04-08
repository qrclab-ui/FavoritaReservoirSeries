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

from common.bootstrap import ensure_local_vendor, prioritize_local_vendor

ensure_local_vendor()
prioritize_local_vendor()

from classical.xgboost.model import run_xgboost


class XGBoostTests(unittest.TestCase):
    def _make_series(self, periods: int = 150) -> pd.DataFrame:
        dates = pd.date_range("2023-01-01", periods=periods, freq="D")
        idx = np.arange(periods)
        y = 100 + 8 * np.sin(2 * np.pi * idx / 7.0) + 0.6 * idx + 15 * (idx % 14 < 2)
        promo = (idx % 14 < 2).astype(float)
        return pd.DataFrame({"ds": dates, "y": y, "onpromotion": promo})

    def test_xgboost_forecast_length_matches_test(self) -> None:
        frame = self._make_series()
        train = frame.iloc[:-21].reset_index(drop=True)
        test = frame.iloc[-21:].reset_index(drop=True)
        result = run_xgboost(train, test)
        self.assertEqual(len(result.predictions), len(test))

    def test_xgboost_runs_on_simple_series(self) -> None:
        frame = self._make_series(180)
        train = frame.iloc[:-28].reset_index(drop=True)
        test = frame.iloc[-28:].reset_index(drop=True)
        result = run_xgboost(train, test)
        self.assertTrue(math.isfinite(result.metrics["rmse"]))
        self.assertLess(result.metrics["rmse"], 25.0)


if __name__ == "__main__":
    unittest.main()
