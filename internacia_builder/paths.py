from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    """Repository root (parent of internacia_builder/)."""
    return Path(__file__).resolve().parent.parent


def blocktypes_source_path(root: Path | None = None) -> Path:
    """Authoritative blocktypes taxonomy YAML (not generated)."""
    root = root or project_root()
    return root / "data" / "blocktypes" / "blocktypes.yaml"


def datasets_dir() -> Path:
    """Consumer/test artifacts; CI can exercise its staged build explicitly."""
    configured = os.environ.get("INTERNACIA_DATASETS_DIR")
    return Path(configured).resolve() if configured else project_root() / "data" / "datasets"
