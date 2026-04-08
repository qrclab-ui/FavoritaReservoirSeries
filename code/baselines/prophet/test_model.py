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

from baselines.prophet.model import run_prophet


class ProphetTests(unittest.TestCase):
    def test_prophet_forecast_length_matches_test(self) -> None:
        dates = pd.date_range("2023-01-01", periods=120, freq="D")
        weekly = np.sin(2 * np.pi * np.arange(120) / 7.0)
        promo = (np.arange(120) % 10 == 0).astype(float)
        y = 100 + 10 * weekly + 12 * promo
        frame = pd.DataFrame({"ds": dates, "y": y, "onpromotion": promo})
        train = frame.iloc[:-14].reset_index(drop=True)
        test = frame.iloc[-14:].reset_index(drop=True)
        result = run_prophet(train, test)
        self.assertEqual(len(result.predictions), len(test))

    def test_prophet_runs_on_simple_series(self) -> None:
        dates = pd.date_range("2023-01-01", periods=140, freq="D")
        weekly = np.sin(2 * np.pi * np.arange(140) / 7.0)
        promo = (np.arange(140) % 14 < 2).astype(float)
        y = 200 + 15 * weekly + 20 * promo
        frame = pd.DataFrame({"ds": dates, "y": y, "onpromotion": promo})
        train = frame.iloc[:-21].reset_index(drop=True)
        test = frame.iloc[-21:].reset_index(drop=True)
        result = run_prophet(train, test)
        self.assertTrue(math.isfinite(result.metrics["mae"]))
        self.assertLess(result.metrics["mae"], 25.0)


if __name__ == "__main__":
    unittest.main()
