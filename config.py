# ============================================================
# File: config.py
#
# OWNER:
#   Alexandre (Person B)
#
# ROLE:
#   Parse and validate configuration file.
#
# ALEXANDRE MUST (obrigatório):
#   1) Read KEY=VALUE lines
#   2) Ignore comments (#) and empty lines
#   3) Validate required keys
#   4) Convert types (int, bool, tuple)
#   5) Raise clear ValueError messages
#
# BONUS:
#   - SEED (int)
#   - ALGORITHM (str): dfs|prim|kruskal|wilson
#   - DISPLAY (str): ascii
#   - ANIMATE (bool)
#   - STEP_DELAY_MS (int)
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool

    # Bonus
    seed: Optional[int] = None
    algorithm: str = "dfs"
    display: str = "ascii"
    animate: bool = False
    step_delay_ms: int = 25


# Alexandre (B) TODO:
# - Implement helper parsers: parse_int, parse_bool, parse_coord
# - Implement validation:
#   width/height > 0
#   entry/exit in bounds
#   entry != exit
#   output_file not empty
# - Normalize algorithm/display strings (lowercase)


def load_config(path: str) -> Config:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    data: dict[str, str] = {}
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid line (expected KEY=VALUE): {raw}")
        key, value = line.split("=", 1)
        data[key.strip().upper()] = value.strip()

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing mandatory keys: {', '.join(missing)}")

    # TODO: real parsing/validation. Raise now to avoid silent bugs.
    raise ValueError("Config parsing not implemented yet (Alexandre - TODO).")
