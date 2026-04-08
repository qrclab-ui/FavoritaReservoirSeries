from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from rc.model import RCConfig, run_rc


class RCTests(unittest.TestCase):
    def _make_series(self, periods: int = 220) -> pd.DataFrame:
        dates = pd.date_range("2023-01-01", periods=periods, freq="D")
        idx = np.arange(periods)
        weekly = np.sin(2 * np.pi * idx / 7.0)
        promo = (idx % 14 < 2).astype(float)
        y = 150 + 12 * weekly + 18 * promo + 0.2 * idx
        return pd.DataFrame({"ds": dates, "y": y, "onpromotion": promo})

    def test_rc_forecast_length_matches_test(self) -> None:
        frame = self._make_series()
        train = frame.iloc[:-28].reset_index(drop=True)
        test = frame.iloc[-28:].reset_index(drop=True)
        result = run_rc(train, test, config=RCConfig(n_reservoir=40, washout=10))
        self.assertEqual(len(result.predictions), len(test))

    def test_rc_runs_on_simple_series(self) -> None:
        frame = self._make_series(260)
        train = frame.iloc[:-35].reset_index(drop=True)
        test = frame.iloc[-35:].reset_index(drop=True)
        result = run_rc(train, test, config=RCConfig(n_reservoir=60, washout=12))
        self.assertTrue(math.isfinite(result.metrics["rmse"]))
        self.assertLess(result.metrics["rmse"], 35.0)


if __name__ == "__main__":
    unittest.main()
