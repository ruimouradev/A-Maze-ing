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

# Import type hints
from __future__ import annotations
from typing import Optional, Iterator

# Importing library for generating random mazes with the same seed
import random

# Wall bitmask: each bit set to 1 means the corresponding wall is CLOSED.
# e.g. 9 = 1001 means North + West walls are closed.
N, E, S, W = 1, 2, 4, 8

# Direction mapping:
# letter -> (dx, dy, bit_current, bit_neighbor_opposite)
DIRS = {
    "N": (0, -1, N, S),
    "E": (1, 0, E, W),
    "S": (0, 1, S, N),
    "W": (-1, 0, W, E),
}


class Maze:
    """Maze grid storing wall bitmasks for each cell (cells[y][x] in 0..15)."""

    def __init__(self, width: int, height: int, cells: list[list[int]]):
        self.width = width
        self.height = height
        # cells[y][x] will have values between 0 and 15 (wall bitmask)
        self.cells = cells

    def get(self, x: int, y: int) -> int:
        """Return the wall bitmask at coordinates (x, y)."""
        return self.cells[y][x]

    def set(self, x: int, y: int, value: int) -> None:
        """Set the wall bitmask at coordinates (x, y)."""
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
        # Lowercase and trim the algorithm name; default to "dfs" if missing.
        self.algorithm = algorithm.lower().strip() if algorithm else "dfs"
        # Use a local RNG so that the same seed produces the same maze.
        self.rng = random.Random(seed)

    # Checking if the coordinates are inside the maze.
    def _in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is inside the maze grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    # Opening both side walls since the maze starts fully closed
    def _open_wall(self, maze: Maze, x: int, y: int, d: str) -> None:
        """
        Open the wall in direction d from (x, y),
        and open the opposite wall in the neighboring cell.
        """
        dx, dy, bit_current, bit_neighbor_opposite = DIRS[d]

        # Calculate the coordinates of the neighboring cell
        nx = x + dx
        ny = y + dy

        if not self._in_bounds(nx, ny):
            return

        # Open the wall by clearing the corresponding bit (~ means NOT)
        # maze.get returns the current wall bitmask (0..15) for this cell
        maze.set(x, y, maze.get(x, y) & ~bit_current)

        # Open the opposite wall in the neighboring cell
        maze.set(nx, ny, maze.get(nx, ny) & ~bit_neighbor_opposite)

    def _can_move(self, maze: Maze, x: int, y: int, d: str) -> bool:
        """
        Return True if there is no closed wall in direction d from (x, y)
        and the neighbor cell exists (is in bounds).
        """
        dx, dy, bit_current, _ = DIRS[d]
        nx = x + dx
        ny = y + dy

        # Checking if the neighbor exists
        if not self._in_bounds(nx, ny):
            return False

        # Wall bit = 1 means closed (cannot move); bit = 0 means open
        return (maze.get(x, y) & bit_current) == 0

    #
    # Fonte (bitmask):
    #   https://www.learncpp.com/cpp-tutorial/bitmasks/
    #
    # Fonte (maze/grafo):
    #   https://en.wikipedia.org/wiki/Maze_generation_algorithm

    def _validate_params(self,
                         entry: tuple[int, int],
                         exit: tuple[int, int]) -> None:
        """
        Validate entry and exit parameters.
        Raise ValueError with clear messages if invalid.
        """
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and Height must be greater than 0")

        ex, ey = entry
        tx, ty = exit

        if not self._in_bounds(ex, ey):
            raise ValueError(f"Entry out of bounds: {entry}")

        if not self._in_bounds(tx, ty):
            raise ValueError(f"Exit out of bounds: {exit}")

        if entry == exit:
            raise ValueError("Entry and Exit must be different")

    def _generate_dfs(self, maze: Maze, start: tuple[int, int]) -> None:
        """
        Generate a perfect maze using DFS (recursive backtracker)
        starting from start.
        The maze is assumed to start fully closed (all cells = 15).
        """
        # Creating a set to save cells already visited
        visited: set[tuple[int, int]] = set()
        # Creat a list where will by saved the path to allow to go back.
        stack: list[tuple[int, int]] = []

        # Start both with the start coordinates
        visited.add(start)
        stack.append(start)

        while stack:
            x, y = stack[-1]

            unvisited_neighbors: list[tuple[int, int, str]] = []
            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                nx = x + dx
                ny = y + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                    # Candidate neighbor: in bounds and not visited yet
                    unvisited_neighbors.append((nx, ny, d))
            # If dont´s exist we pop (going back)
            if not unvisited_neighbors:
                stack.pop()
                continue

            # Chosing an randow neighord
            nx, ny, d = self.rng.choice(unvisited_neighbors)
            # Opening both walls
            self._open_wall(maze, x, y, d)
            visited.add((nx, ny))
            stack.append((nx, ny))

    #
    # Fonte (DFS maze):
    #   https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap


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


    def solve(self,
              maze: Maze,
              entry: tuple[int, int],
              exit: tuple[int, int]) -> list[str]:
        """Return shortest path as list of moves like ['N','E',...]."""
        # TODO STEP 7: BFS solver
        return []


    # TODO STEP 8: solve_astar(...)

    # BONUS public API
    def iter_steps(self,
                   entry: tuple[int, int],
                   exit: tuple[int, int]) -> Iterator[tuple[Maze, list[str]]]:
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
