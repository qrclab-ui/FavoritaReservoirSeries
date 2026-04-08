from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from baselines.seasonal_naives.model import run_seasonal_naive, seasonal_naive_forecast


class SeasonalNaiveTests(unittest.TestCase):
    def test_weekly_pattern_is_repeated(self) -> None:
        pattern = [10, 20, 30, 40, 50, 60, 70]
        train = pd.DataFrame({"y": pattern * 3})
        forecast = seasonal_naive_forecast(train, horizon=10, season_length=7)
        self.assertEqual(forecast.tolist(), (pattern + pattern[:3]))

    def test_metrics_are_zero_for_perfect_repeat(self) -> None:
        pattern = [10, 20, 30, 40, 50, 60, 70]
        train = pd.DataFrame({"y": pattern * 4})
        test = pd.DataFrame({"y": pattern * 2})
        result = run_seasonal_naive(train, test, season_length=7)
        self.assertAlmostEqual(result.metrics["mae"], 0.0)
        self.assertAlmostEqual(result.metrics["rmse"], 0.0)
        self.assertAlmostEqual(result.metrics["wape"], 0.0)


if __name__ == "__main__":
    unittest.main()
