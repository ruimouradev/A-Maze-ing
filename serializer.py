# ============================================================
# File: serializer.py
#
# OWNER:
#   Alexandre (Person B)
#
# ROLE:
#   Serialize maze output in the exact subject format.
#
# ALEXANDRE MUST:
#   1) Convert wall masks (0..15) to ONE hex digit per cell
#   2) Write grid row by row (one line per row)
#   3) Write blank line
#   4) Write entry as 'x,y'
#   5) Write exit as 'x,y'
#   6) Write solution path as a string like 'NNEESW'
#
# BONUS:
#   - Optional debug info only if the subject allows (default: none).
# ============================================================

from __future__ import annotations
from mazegen import Maze


def write_output_file(
    output_path: str,
    maze: Maze,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
) -> None:
    """Write maze grid and solution to file in 42 subject format.

    Format:
        - Hex grid: one row per line, each cell as uppercase hex digit (0-F)
        - Blank line separator
        - Entry point as 'x,y'
        - Exit point as 'x,y'
        - Solution path as direction string (e.g., 'NNEESW')

    Args:
        output_path: Path to output file (parent dir must exist).
        maze: Maze object containing cells grid with wall bitmasks (0-15).
        entry: Entry point coordinates as (x, y).
        exit: Exit point coordinates as (x, y).
        path: List of direction strings ['N', 'E', 'S', 'W'] forming solution.

    Raises:
        ValueError: If file write fails (I/O or OS error).
    """
    try:
        with open(output_path, 'w', encoding="utf-8") as f:
            # 1) Write the hex grid: one hex digit per cell, one row per line
            for row in maze.cells:
                hex_line = "".join(f"{cell:X}" for cell in row)
                f.write(hex_line + "\n")

            # 2) Write the mandatory blank line
            f.write("\n")

            # 3) Write entry point as x,y
            f.write(f"{entry[0]},{entry[1]}\n")

            # 4) Write exit point as x,y
            f.write(f"{exit[0]},{exit[1]}\n")

            # 5) Write shortest path string
            f.write("".join(path) + "\n")

    except (IOError, OSError) as e:
        raise ValueError(f"Could not write output file: {e}")
