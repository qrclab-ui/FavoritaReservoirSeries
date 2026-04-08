from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import pandas as pd

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from baselines.ets.model import run_ets


class ETSTests(unittest.TestCase):
    def test_ets_forecast_has_expected_length(self) -> None:
        pattern = [12, 15, 14, 18, 22, 30, 26]
        values = pattern * 8
        train = pd.DataFrame({"y": values[:-14]})
        test = pd.DataFrame({"y": values[-14:]})
        result = run_ets(train, test, season_length=7)
        self.assertEqual(len(result.predictions), len(test))

    def test_ets_handles_simple_seasonal_series(self) -> None:
        pattern = [100, 110, 130, 120, 150, 170, 160]
        values = pattern * 10
        train = pd.DataFrame({"y": values[:-14]})
        test = pd.DataFrame({"y": values[-14:]})
        result = run_ets(train, test, season_length=7)
        self.assertTrue(math.isfinite(result.metrics["rmse"]))
        self.assertLess(result.metrics["rmse"], 20.0)


if __name__ == "__main__":
    unittest.main()
