from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

import yaml


@lru_cache(maxsize=8)
def load_yaml_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
