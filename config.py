# ============================================================
# File: config.py
#
# OWNER:
#   Alexandre
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

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Config:
    """Immutable maze configuration parsed from a KEY=VALUE file.
    Split between Mandatory Fields and Bonus support
    frozen=True: makes the configuration "read-only" once it is created
    """
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


# Alexandre (B) TODO: All done
# ✓ Implement helper parsers: parse_int, parse_bool, parse_coord
# ✓ Implement validation:
# ✓ width/height > 0
# ✓ entry/exit in bounds
# ✓ entry != exit
# ✓ output_file not empty
# ✓ Normalize algorithm/display strings (lowercase)
#   Implement validation for bonuses

def _parse_bool(value: str) -> bool:
    """Converts string values to boolean safely."""
    val = value.lower()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def _parse_coord(value: str) -> tuple[int, int]:
    """Converts 'x,y' string into a tuple of integers."""
    try:
        parts = value.split(",")
        # if you don't get a list of 2 strings raise error
        if len(parts) != 2:
            raise ValueError
        x, y = map(int, parts)  # applies int() to every item in the list
        return (x, y)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid coordinate format (expected x,y): {value}")


def load_config(path: str) -> Config:
    """Load and validate maze configuration from a KEY=VALUE file.

    Args:
        path: Path to configuration file.

    Returns:
        Validated Config object with all parameters.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If file format invalid or validation fails.
    """
    #  Path Validation: It first checks if the file exists
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    data: dict[str, str] = {}
    #  Read file: reads the entire content as a single string
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()  # after split, removes leading/trailing whitespace
        if not line or line.startswith("#"):
            continue  # if empty or "#" skip to next line
        # Strip inline comments (# not in quotes)
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if "=" not in line:
            raise ValueError(f"Invalid line (expected KEY=VALUE): {raw}")
        key, value = line.split("=", 1)  # split the string by the 1st "="
        data[key.strip().upper()] = value.strip()  # stores Key : value in dict

    #  checks the dictionary against a list of required strings
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    missing = [k for k in required if k not in data]  # list of missing keys
    if missing:
        raise ValueError(f"Missing mandatory keys: {', '.join(missing)}")

    # Conversion and Basic Validation
    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])
        if width <= 0 or height <= 0:
            raise ValueError("WIDTH and HEIGHT must be positive integers.")

        # convert entry/exit coordinates from str to int
        entry = _parse_coord(data["ENTRY"])
        exit_coord = _parse_coord(data["EXIT"])

        # Maze Requirement: Entry/Exit inside bounds
        # List of Tuples: The code creates a temporary list containing two
        # items. Each item is a tuple: ("ENTRY", entry) and
        # ("EXIT", exit_coord).
        for name, (x, y) in [("ENTRY", entry), ("EXIT", exit_coord)]:
            #  The for loop iterates the entry and then the exit coordinates
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(
                    f"{name} {x, y} is outside maze bounds ({width}x{height})."
                )

        # Maze Requirement: Entry and exit must be different
        if entry == exit_coord:
            raise ValueError("ENTRY and EXIT coordinates must be different.")

        # Validation: output_file not empty
        output_path = data["OUTPUT_FILE"]
        if not output_path.strip():
            raise ValueError("OUTPUT_FILE parameter cannot be empty.")

        # Check if parent directory exists
        out_p = Path(output_path)
        if not out_p.parent.exists():
            raise ValueError(
                f"Directory for output file does not exist: {out_p.parent}"
            )

        return Config(
            width=width,
            height=height,
            entry=entry,
            exit=exit_coord,
            output_file=data["OUTPUT_FILE"],
            perfect=_parse_bool(data["PERFECT"]),

            # Optional Bonus parsing: errors not checked; only defaults for now
            seed=int(data.get("SEED", 42)),
            algorithm=data.get("ALGORITHM", "dfs").lower(),
            display=data.get("DISPLAY", "ascii").lower(),
            animate=_parse_bool(data.get("ANIMATE", "False")),
            step_delay_ms=int(data.get("STEP_DELAY_MS", 25))
        )

    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")
