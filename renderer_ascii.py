# ============================================================
# File: renderer_ascii.py
#
# OWNER:
#   Alexandre (Person B)
#
# ROLE:
#   Terminal ASCII visualization and interaction.
#
# ALEXANDRE MUST (obrigatório):
#   1) Render maze walls
#   2) Render entry and exit
#   3) Toggle solution path
#   4) Change wall colors (ANSI)
#   5) Regenerate maze
#
# BONUS:
#   - Toggle animation (cfg.animate)
#   - Change algorithm at runtime (dfs/prim/kruskal/wilson)
#   - Display generation steps using gen.iter_steps(...) when available
#
# Recommended commands:
#   r = regenerate
#   p = toggle path
#   c = cycle colors
#   a = toggle animation
#   g = change algorithm
#   q = quit
# ============================================================

from __future__ import annotations

from dataclasses import dataclass

from config import Config
from mazegen import MazeGenerator


class AsciiRenderer:
    def __init__(self):
        # Flag to show or hide solution path
        self.show_path = True

    def run(self, gen, cfg):
        # Start ASCII rendering loop

        # TODO (Alexandre):
        # - Draw maze
        # - Handle keyboard input

        print("ASCII renderer not implemented yet")
