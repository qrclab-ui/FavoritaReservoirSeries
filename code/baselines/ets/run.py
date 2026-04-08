from __future__ import annotations

import json
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from common.favorita import FavoritaSeriesConfig, load_store_family_series, temporal_train_test_split
from common.reporting import save_results
from baselines.ets.model import run_ets


def main() -> None:
    config = FavoritaSeriesConfig()
    frame = load_store_family_series(store_nbr=config.store_nbr, family=config.family)
    train, test = temporal_train_test_split(frame, test_days=config.test_days)
    result = run_ets(train, test, season_length=config.season_length)

    output_dir = Path(__file__).resolve().parent / "results"
    artifacts = save_results(
        model_name="ETS",
        output_dir=output_dir,
        train=train,
        test=test,
        predictions=result.predictions,
        metrics=result.metrics,
    )

    payload = {
        "config": {
            "store_nbr": config.store_nbr,
            "family": config.family,
            "test_days": config.test_days,
            "season_length": config.season_length,
        },
        "metrics": result.metrics,
        "artifacts": {name: str(path) for name, path in artifacts.items()},
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
