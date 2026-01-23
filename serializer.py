# ============================================================
# File: serializer.py
#
# OWNER:
#   Alexandre (Person B)
#
# ROLE:
#   Write maze to output file in exact required format.
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
#   - You can optionally include extra debug info ONLY if the subject allows it.
#     (Default: do not add anything extra.)
# ============================================================

from __future__ import annotations

from pathlib import Path

from mazegen import Maze


def write_output_file(
    output_path: str,
    maze: Maze,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
) -> None:
    # TODO (Alexandre): implement serializer exactly.
    raise ValueError("Output serializer not implemented (Alexandre - TODO).")
