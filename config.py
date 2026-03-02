# ============================================================
# File: config.py
#
# ROLE:
#   Parse and validate configuration file.
#
#   1) Read KEY=VALUE lines
#   2) Ignore comments (#) and empty lines
#   3) Validate required keys
#   4) Convert types (int, bool, tuple)
#   5) Raise clear ValueError messages
#

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Config:
    """Immutable maze configuration parsed from a KEY=VALUE file.

    The dataclass is frozen to prevent runtime mutation once validated.
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
    animate_solver: bool = False
    animate_generation: bool = False
    step_delay_ms: int = 25
    density: float = 0.06


def _parse_bool(value: str) -> bool:
    """Convert string values to boolean safely."""
    val = value.lower()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def _parse_density(value: str) -> float:
    """Convert string value to float and validate 0.0 <= x <= 1.0."""
    try:
        density = float(value)
        if not (0.0 <= density <= 1.0):
            msg = f"Density must be between 0.0 and 1.0, got {density}"
            raise ValueError(msg)
        return density
    except (ValueError, TypeError):
        msg = f"Invalid density value (expected float 0.0-1.0): {value}"
        raise ValueError(msg)


def _parse_optional_int(value: Optional[str]) -> Optional[int]:
    """Convert string values to optional int (None if empty/None)."""
    if value is None:
        return None
    text = value.strip()
    if not text or text.lower() == "none":
        return None
    try:
        return int(text)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid integer value: {value}")


def _parse_coord(value: str) -> tuple[int, int]:
    """Convert an 'x,y' string into a tuple of integers."""
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
    # Path validation: ensure the file exists
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    data: dict[str, str] = {}
    # Read file: strip comments and empty lines, then parse KEY=VALUE
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()  # after split, removes leading/trailing whitespace
        if not line or line.startswith("#"):
            continue  # if empty or "#" skip to next line
        # Strip inline comments (# not in quotes)
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if "=" not in line:
            raise ValueError(f"Invalid line (expected KEY=VALUE): {raw}")
        key, value = line.split("=", 1)
        data[key.strip().upper()] = value.strip()

    # Check required fields
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    missing = [k for k in required if k not in data]  # list of missing keys
    if missing:
        raise ValueError(f"Missing mandatory keys: {', '.join(missing)}")

    # Conversion and basic validation
    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])
        if width <= 0 or height <= 0:
            raise ValueError("WIDTH and HEIGHT must be positive integers.")

        # Check if maze is too small for 42 stamp
        if width < 11 or height < 9:
            print("Warning: Maze too small for 42 pattern")
            response = input(
                "Do you want to continue without 42 pattern? (y/n): "
            )
            if response.lower() != 'y':
                raise ValueError("Maze too small for 42 pattern")

        # Convert entry/exit coordinates from str to int
        entry = _parse_coord(data["ENTRY"])
        exit_coord = _parse_coord(data["EXIT"])

        # Maze requirement: entry/exit inside bounds
        for name, (x, y) in [("ENTRY", entry), ("EXIT", exit_coord)]:
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(
                    f"{name} {x, y} is outside maze bounds ({width}x{height})."
                )

        # Maze requirement: entry and exit must be different
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

        seed_raw = data.get("SEED")
        seed = _parse_optional_int(seed_raw)
        if seed is None and seed_raw is None:
            seed = 42
        algorithm = data.get("ALGORITHM", "dfs").lower()
        allowed_algorithms = {"dfs", "prim", "kruskal", "wilson"}
        if algorithm not in allowed_algorithms:
            raise ValueError(
                "ALGORITHM must be one of: dfs, prim, kruskal, wilson"
            )

        display = data.get("DISPLAY", "ascii").lower()
        if display not in {"ascii"}:
            raise ValueError("DISPLAY must be 'ascii'")

        animate_default = _parse_bool(data.get("ANIMATE", "False"))
        animate_solver = _parse_bool(
            data.get("ANIMATE_SOLVER", str(animate_default))
        )
        animate_generation = _parse_bool(
            data.get("ANIMATE_GENERATION", str(animate_default))
        )

        step_delay_ms = int(data.get("STEP_DELAY_MS", 25))
        if step_delay_ms < 0:
            raise ValueError("STEP_DELAY_MS must be >= 0")

        return Config(
            width=width,
            height=height,
            entry=entry,
            exit=exit_coord,
            output_file=data["OUTPUT_FILE"],
            perfect=_parse_bool(data["PERFECT"]),

            # Optional bonus parsed
            seed=seed,
            algorithm=algorithm,
            display=display,
            animate=animate_default,
            animate_solver=animate_solver,
            animate_generation=animate_generation,
            step_delay_ms=step_delay_ms,
            density=_parse_density(data.get("DENSITY", "0.06")),
        )

    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")
