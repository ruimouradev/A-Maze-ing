# ============================================================
# File: mazegen.py
#
# OWNER:
#   Rui (Person A)
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
#   7) (Optional) Add Kruskal / Wilson as extra algorithms
#   8) Add iter_steps() generator for animation support
#
# MUST NOT:
#   - Print to terminal
#   - Read/write files
#   - Handle user input
# ============================================================

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

    # -----------------------
    # Required public API
    # -----------------------
    def generate(self, entry: tuple[int, int], exit: tuple[int, int]) -> Maze:
        """Generate and return a Maze."""
        # TODO (Rui): implement param validation (bounds, entry!=exit, etc.)

        maze = Maze(self.width, self.height, 
                    [[15 for _ in range(self.width)] for _ in range(
                        self.height)])

        # Dispatch by algorithm (bonus-ready)
        if self.algorithm in ("dfs", "recursive_backtracker"):
            # TODO (Rui): implement DFS generation
            pass
        elif self.algorithm == "prim":
            # TODO (Rui BONUS): implement Prim generation
            pass
        elif self.algorithm == "kruskal":
            # TODO (Rui BONUS optional): implement Kruskal generation
            pass
        elif self.algorithm == "wilson":
            # TODO (Rui BONUS optional): implement Wilson generation
            pass
        else:
            # Safe fallback
            # TODO (Rui): treat unknown algorithm as dfs
            pass

        # TODO (Rui): enforce constraints (borders, 42, no 3x3)
        return maze

    def solve(self, maze: Maze, entry: tuple[int, int],
              exit: tuple[int, int]) -> list[str]:
        """Return shortest path as list of moves like ['N','E',...]."""
        # TODO (Rui): implement BFS solver
        return []

    # -----------------------
    # BONUS public API
    # -----------------------
    def iter_steps(self, entry: tuple[int, int],
                   exit: tuple[int, int]) -> Iterator[tuple[Maze, list[str]]]:
        """Yield intermediate (maze, path_so_far) states for animation.

        BONUS contract:
          - If you implement this, renderer can animate generation.
          - If not implemented, renderer should fall back to static generate().
        """
        # TODO (Rui BONUS): yield steps during generation
        # Example design:
        #   maze = init
        #   for each carve step:
        #       yield (maze, partial_path_or_empty)
        #   final_path = solve(maze, entry, exit)
        #   yield (maze, final_path)
        raise NotImplementedError("iter_steps not implemented (Rui - BONUS).")
