# ============================================================
# File: mazegen.py
#
# OWNER:
#   Rui
#
# ROLE:
#   Core maze engine (data model, generation, solving).
#
# RUI MUST (obrigatório):
#   1) Implement Maze data structure (grid + walls)
#   2) Implement wall consistency helpers (open_wall updates both cells)
#   3) Implement DFS maze generation (perfect maze baseline)
#   4) Enforce constraints (borders, "42" pattern, no 3x3 open areas)
#   5) Implement BFS shortest-path solver (returns ['N','E','S','W'])
#
# BONUS(stubs included):
#   6) Add 2nd algorithm (Prim) selectable via config: ALGORITHM=prim
#   7) Add A* solver (2nd resolution algorithm)  <-- to match your "bonus full"
#   8) Add iter_steps() generator for animation support
#
# MUST NOT:
#   - Print to terminal
#   - Read/write files
#   - Handle user input

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterator

import random

# Wall bits (1 means wall CLOSED)
N, E, S, W = 1, 2, 4, 8

# Direction mapping:
# letter -> (dx, dy, bit_current, bit_neighbor_opposite)
DIRS = {
    "N": (0, -1, N, S),
    "E": (1, 0, E, W),
    "S": (0, 1, S, N),
    "W": (-1, 0, W, E),
}


@dataclass
class Maze:
    width: int
    height: int
    cells: list[list[int]]  # cells[y][x] wall mask 0..15 (closed walls)

    def get(self, x: int, y: int) -> int:
        return self.cells[y][x]

    def set(self, x: int, y: int, value: int) -> None:
        self.cells[y][x] = value


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int],
        perfect: bool,
        algorithm: str = "dfs",
    ) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.algorithm = algorithm.lower().strip() if algorithm else "dfs"
        self.rng = random.Random(seed)


    # TODO STEP 1.1: _in_bounds(...)
    # TODO STEP 1.2: _open_wall(...)
    # TODO STEP 1.3: _can_move(...)


    # TODO STEP 2: _validate_params(...)


    # TODO STEP 3: _generate_dfs(...)


    # TODO STEP 4: _generate_prim(...)


    # TODO STEP 5: _stamp_42(...)


    # TODO STEP 6: _has_forbidden_3x3(...)
    # TODO STEP 6: _fix_forbidden_3x3(...)

    # Required public API
    def generate(self, entry: tuple[int, int], exit: tuple[int, int]) -> Maze:
        """Generate and return a Maze."""


        maze = Maze(
            self.width,
            self.height,
            [[15 for _ in range(self.width)] for _ in range(self.height)],
        )

        if self.algorithm in ("dfs", "recursive_backtracker"):
            pass
        elif self.algorithm == "prim":
            pass
        elif self.algorithm == "kruskal":
            # (opcional) bónus extra
            pass
        elif self.algorithm == "wilson":
            # (opcional) bónus extra
            pass
        else:
            # fallback seguro: tratar como dfs
            pass

        return maze


    def solve(self, maze: Maze, entry: tuple[int, int], exit: tuple[int, int]) -> list[str]:
        """Return shortest path as list of moves like ['N','E',...]."""
        # TODO STEP 7: BFS solver
        return []


    # TODO STEP 8: solve_astar(...)

    # BONUS public API
    def iter_steps(self, entry: tuple[int, int], exit: tuple[int, int]) -> Iterator[tuple[Maze, list[str]]]:
        """Yield intermediate (maze, path_so_far) states for animation.

        STEP 9 — ANIMAÇÃO (BÓNUS)
        Objetivo: permitir ao renderer animar geração (ASCII/MLX).

        Implementar:
          - se implementares DFS step-by-step:
              - a cada _open_wall(...) faz yield (maze, [])
          - no fim:
              - calcula final_path (solve)
              - yield (maze, final_path)

        Fonte (generators):
          https://realpython.com/introduction-to-python-generators/
        """
        raise NotImplementedError("iter_steps not implemented (Rui - BONUS).")
