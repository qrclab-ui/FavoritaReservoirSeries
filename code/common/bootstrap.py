from __future__ import annotations

import os
import sys
from pathlib import Path


def code_root() -> Path:
    return Path(__file__).resolve().parents[1]


def project_root() -> Path:
    return code_root().parent


def ensure_local_vendor() -> Path:
    """Append the local vendor directory so project-local deps are importable.

    The vendor path is appended instead of inserted at the front. This keeps the
    interpreter using the already-available core scientific stack from the
    current environment whenever possible, while still making local packages
    such as prophet and statsmodels available.
    """

    vendor_dir = code_root() / ".vendor"
    mpl_config_dir = project_root() / ".mplconfig"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    if vendor_dir.exists() and str(vendor_dir) not in sys.path:
        sys.path.append(str(vendor_dir))
    return vendor_dir


def prioritize_local_vendor() -> Path:
    """Ensure the local vendor path is searched before global site-packages."""

    vendor_dir = ensure_local_vendor()
    if vendor_dir.exists():
        vendor_str = str(vendor_dir)
        if vendor_str in sys.path:
            sys.path.remove(vendor_str)
        sys.path.insert(0, vendor_str)
    return vendor_dir
