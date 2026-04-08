from __future__ import annotations

import sys
import unittest
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from qrc.objective import ObjectiveConfig, compute_qrc_objective


class QRCObjectiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reference_metrics = {
            "mae": 200.0,
            "rmse": 300.0,
            "wape": 0.10,
            "smape": 0.11,
        }
        self.config = ObjectiveConfig(
            qubit_bounds=(4, 16),
            window_bounds=(3, 13),
            complexity_weight=0.05,
        )

    def test_objective_improves_when_metrics_improve(self) -> None:
        worse = compute_qrc_objective(
            n_qubits=10,
            window=7,
            metrics={"mae": 420.0, "rmse": 520.0, "wape": 0.20, "smape": 0.23},
            reference_metrics=self.reference_metrics,
            config=self.config,
        )
        better = compute_qrc_objective(
            n_qubits=10,
            window=7,
            metrics={"mae": 360.0, "rmse": 470.0, "wape": 0.17, "smape": 0.20},
            reference_metrics=self.reference_metrics,
            config=self.config,
        )
        self.assertLess(better.score, worse.score)

    def test_objective_penalizes_extra_complexity_when_metrics_match(self) -> None:
        compact = compute_qrc_objective(
            n_qubits=6,
            window=5,
            metrics={"mae": 420.0, "rmse": 520.0, "wape": 0.20, "smape": 0.23},
            reference_metrics=self.reference_metrics,
            config=self.config,
        )
        larger = compute_qrc_objective(
            n_qubits=14,
            window=11,
            metrics={"mae": 420.0, "rmse": 520.0, "wape": 0.20, "smape": 0.23},
            reference_metrics=self.reference_metrics,
            config=self.config,
        )
        self.assertLess(compact.score, larger.score)


if __name__ == "__main__":
    unittest.main()

