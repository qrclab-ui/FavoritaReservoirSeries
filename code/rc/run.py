from __future__ import annotations

import json
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.bootstrap import ensure_local_vendor

ensure_local_vendor()

from common.favorita import FavoritaSeriesConfig, load_store_family_series, temporal_train_test_split
from common.reporting import save_results
from rc.model import RCConfig, run_rc


def main() -> None:
    favorita_config = FavoritaSeriesConfig()
    rc_config = RCConfig()
    frame = load_store_family_series(
        store_nbr=favorita_config.store_nbr,
        family=favorita_config.family,
    )
    train, test = temporal_train_test_split(frame, test_days=favorita_config.test_days)
    result = run_rc(train, test, config=rc_config)

    output_dir = Path(__file__).resolve().parent / "results"
    artifacts = save_results(
        model_name="RC",
        output_dir=output_dir,
        train=train,
        test=test,
        predictions=result.predictions,
        metrics=result.metrics,
    )

    payload = {
        "config": {
            "store_nbr": favorita_config.store_nbr,
            "family": favorita_config.family,
            "test_days": favorita_config.test_days,
            "n_reservoir": rc_config.n_reservoir,
            "spectral_radius": rc_config.spectral_radius,
            "leak_rate": rc_config.leak_rate,
            "washout": rc_config.washout,
        },
        "metrics": result.metrics,
        "artifacts": {name: str(path) for name, path in artifacts.items()},
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
