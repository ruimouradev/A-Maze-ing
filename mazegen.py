"""
A-Maze-ing — reusable maze generator module

Standalone, reusable module:
- Maze data model (walls bitmask)
- Generation algorithms + constraints
- Solver (shortest path)

Rules:
- No printing
- No file I/O
- No user interaction

Basic usage
-----------
from mazegen import MazeGenerator

gen = MazeGenerator(width=31, height=21, seed=42,
                    perfect=True, algorithm="dfs")
entry = (1, 1)
exit_ = (29, 19)

maze = gen.generate(entry=entry, exit=exit_)
path = gen.solve(maze=maze, entry=entry, exit=exit_)

Parameters
----------
- width, height: maze dimensions (int)
- seed: int or None (None => random)
- perfect: bool (True => perfect maze; False => may create loops)
- algorithm: "dfs" or "prim" (if implemented)
- density: float (used when perfect=False)

Accessing the structure
-----------------------
- maze.width, maze.height
- maze.cells[y][x]: int bitmask in 0..15
  Bits: N=1, E=2, S=4, W=8 (bit set => wall is CLOSED)
- "42" stamp: maze.omitted_42 and maze.stamp42 (if present)

Packaging note
--------------
This file must be packagable as `mazegen-*` (.whl or .tar.gz) and installable
via pip.
"""

# Enable forward type annotations (Python typing feature)
from __future__ import annotations

# Typing helpers: Optional values and Iterator return types
from typing import Optional, Iterator

# Efficient FIFO queue used by BFS
from collections import deque

# Deterministic random generator (allow seed)
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

        # True if the maze is too small to place the mandatory "42" stamp.
        self.omitted_42: bool = False

        # This will store the coordinates of the 42 pattern.
        self.stamp42: set[tuple[int, int]] = set()

    def get(self, x: int, y: int) -> int:
        """Return the wall bitmask at coordinates (x, y)."""
        return self.cells[y][x]

    def set(self, x: int, y: int, value: int) -> None:
        """Set the wall bitmask at coordinates (x, y)."""
        self.cells[y][x] = value


class MazeGenerator:
    """Maze generator engine (generation + constraints + solver)."""
    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int],
        perfect: bool,
        algorithm: str = "dfs",
        density: float = 0.06,
    ) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        # Lowercase and trim the algorithm name; default to "dfs" if missing.
        self.algorithm = algorithm.lower().strip() if algorithm else "dfs"
        # Use a local RNG so that the same seed produces the same maze.
        self.rng = random.Random(seed)

        # Density is used only when perfect=False (to create loops).
        self.density = density

    # Allow to change the algorithm without creating an MazeGenerator
    def set_algorithm(self, algorithm: str) -> None:
        """Set the maze generation algorithm at runtime."""
        self.algorithm = algorithm.lower().strip() if algorithm else "dfs"

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

    # Check if we can move in that direction
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

    # Check if entry and exit values are possible (inside maze and different)
    def _validate_params(
        self,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        """
        Validate entry and exit parameters.
        Raise ValueError with clear messages if invalid.
        """
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be greater than 0")

        ex, ey = entry
        tx, ty = exit

        if not self._in_bounds(ex, ey):
            raise ValueError(f"Entry out of bounds: {entry}")

        if not self._in_bounds(tx, ty):
            raise ValueError(f"Exit out of bounds: {exit}")

        if entry == exit:
            raise ValueError("Entry and exit must be different")

    # DFS algorithm (recursive backtracker)
    def _generate_dfs(
        self,
        maze: Maze,
        start: tuple[int, int],
        blocked: set[tuple[int, int]],
    ) -> None:
        """
        Generate a perfect maze using DFS (recursive backtracker)
        starting from start.
        The maze is assumed to start fully closed (all cells = 15).
        """
        # Creating a set to save cells already visited
        visited: set[tuple[int, int]] = set()
        # Create a list where will be saved the path to allow going back
        stack: list[tuple[int, int]] = []

        # Start both with the start coordinates
        visited.add(start)
        stack.append(start)

        while stack:
            # Looking for current cell = stack top
            x, y = stack[-1]

            unvisited_neighbors: list[tuple[int, int, str]] = []
            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                nx = x + dx
                ny = y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in visited:
                    continue
                if (nx, ny) in blocked:
                    continue
                # Candidate neighbor: in bounds and not visited yet
                unvisited_neighbors.append((nx, ny, d))

            # If none exist we have to pop (going back)
            if not unvisited_neighbors:
                stack.pop()
                continue

            # Choosing a random neighbor
            nx, ny, d = self.rng.choice(unvisited_neighbors)
            # Opening both walls
            self._open_wall(maze, x, y, d)
            visited.add((nx, ny))
            stack.append((nx, ny))

    # Prim algorith
    def _generate_prim(
        self,
        maze: Maze,
        start: tuple[int, int],
        blocked: set[tuple[int, int]],
    ) -> None:
        """
        Generate a maze using Prim's algorithm (randomized)
        starting from start.
        The maze is assumed to start fully closed (all cells = 15).
        """
        in_tree: set[tuple[int, int]] = set()
        frontier: list[tuple[int, int, int, int, str]] = []
        # frontier elements: (x, y, nx, ny, d) meaning:
        # from cell (x,y), neighbor (nx,ny) in direction d
        # in_tree is the set of cells that are part of the maze
        # frontier is the list of possible connections

        def add_frontier(x: int, y: int) -> None:
            """Add edges from (x,y) to all neighbors not yet in the tree."""
            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in in_tree:
                    continue
                if (nx, ny) in blocked:
                    continue
                frontier.append((x, y, nx, ny, d))

        sx, sy = start
        in_tree.add((sx, sy))
        add_frontier(sx, sy)

        while frontier:
            # Choose a random frontier edge
            i = self.rng.randrange(len(frontier))
            x, y, nx, ny, d = frontier.pop(i)

            # If the neighbor is already in the tree, skip
            if (nx, ny) in in_tree:
                continue

            # Carve the passage and add the new cell to the tree
            self._open_wall(maze, x, y, d)
            in_tree.add((nx, ny))
            add_frontier(nx, ny)

    # "42" pattern
    def _get_42_coords(self, maze: Maze) -> set[tuple[int, int]]:
        """Return coordinates of a centered '42' pattern (size-aware)."""
        # Using multiple patterns so the "42" can be smaller on small mazes.

        pat_small = [
            "#.#.###",
            "#.#...#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]  # 7x5

        pat_med = [
            "#..#.####",
            "#..#....#",
            "####.####",
            "...#.#...",
            "...#.####",
            ".......#.",
        ]  # 8x6

        pat_big = [
            "#...#.#####",
            "#...#.....#",
            "#...#.....#",
            "#####.#####",
            "....#.#....",
            "....#.#....",
            "....#.#####",
        ]  # 11x7

        # Pick the pattern based on maze size (visual balance).
        if maze.width < 28 or maze.height < 20:
            pattern = pat_small
        elif maze.width < 45 or maze.height < 30:
            pattern = pat_med
        else:
            pattern = pat_big

        base_h = len(pattern)
        base_w = len(pattern[0])

        # Keep a margin so the maze still has room around the stamp.
        margin = 2
        avail_w = maze.width - (2 * margin)
        avail_h = maze.height - (2 * margin)

        if avail_w < base_w or avail_h < base_h:
            raise ValueError("Maze too small for 42 pattern")

        # Scale only for very large mazes, otherwise it becomes too big.
        max_scale = min(avail_w // base_w, avail_h // base_h)
        scale = 1
        if maze.width >= 90 and maze.height >= 60:
            scale = min(2, max_scale)

        stamp_w = base_w * scale
        stamp_h = base_h * scale

        # Center the chosen pattern in the maze.
        ox = (maze.width - stamp_w) // 2
        oy = (maze.height - stamp_h) // 2

        coords: set[tuple[int, int]] = set()

        for py in range(base_h):
            row = pattern[py]
            for px in range(base_w):
                if row[px] == ".":
                    continue
                x0 = ox + (px * scale)
                y0 = oy + (py * scale)
                for sy in range(scale):
                    for sx in range(scale):
                        coords.add((x0 + sx, y0 + sy))

        return coords

    def _stamp_42(self, maze: Maze, coords: set[tuple[int, int]]) -> None:
        """
        Stamp the "42" into the maze by forcing some cells to be closed (15).
        """
        # Save coords of the 42 pattern so can color it safely
        maze.stamp42.clear()
        maze.stamp42.update(coords)

        # Force the 42 cells to be fully closed (all walls closed)
        for x, y in coords:
            maze.set(x, y, 15)

    # Closing wall both sides
    def _close_wall(self, maze: Maze, x: int, y: int, d: str) -> None:
        """
        Close the wall in direction d from (x, y),
        and close the opposite wall in the neighboring cell.
        """
        dx, dy, bit_current, bit_neighbor_opposite = DIRS[d]
        nx = x + dx
        ny = y + dy

        if not self._in_bounds(nx, ny):
            return

        # Set bit to 1 -> wall closed on both sides
        maze.set(x, y, maze.get(x, y) | bit_current)
        maze.set(nx, ny, maze.get(nx, ny) | bit_neighbor_opposite)

    def _has_forbidden_3x3(self, maze: Maze) -> bool:
        """
        Return True if there exists a 3x3 window that is "too open"
        according to our criterion.
        """
        # -2 we are incrementing 2 lines in 3x3 area
        for y0 in range(0, maze.height - 2):
            for x0 in range(0, maze.width - 2):
                all_open = True

                # Check horizontal internal corridors inside the 3x3
                # 3 lines with and connections
                for y in range(y0, y0 + 3):
                    for x in range(x0, x0 + 2):
                        if not self._can_move(maze, x, y, "E"):
                            all_open = False
                            break
                    if not all_open:
                        break

                if not all_open:
                    continue

                # Check vertical internal corridors inside the 3x3
                for x in range(x0, x0 + 3):
                    for y in range(y0, y0 + 2):
                        if not self._can_move(maze, x, y, "S"):
                            all_open = False
                            break
                    if not all_open:
                        break

                if all_open:
                    return True

        return False

    def _fix_forbidden_3x3(self, maze: Maze) -> None:
        """
        Fix the first forbidden 3x3 found by closing ONE internal passage.
        """
        for y0 in range(0, maze.height - 2):
            for x0 in range(0, maze.width - 2):
                all_open = True

                for y in range(y0, y0 + 3):
                    for x in range(x0, x0 + 2):
                        if not self._can_move(maze, x, y, "E"):
                            all_open = False
                            break
                    if not all_open:
                        break

                if not all_open:
                    continue

                for x in range(x0, x0 + 3):
                    for y in range(y0, y0 + 2):
                        if not self._can_move(maze, x, y, "S"):
                            all_open = False
                            break
                    if not all_open:
                        break

                if not all_open:
                    continue

                # Found a forbidden 3x3
                # We try center->right first, else center->down,
                # else any internal open wall.
                cx, cy = x0 + 1, y0 + 1

                if self._can_move(maze, cx, cy, "E"):
                    self._close_wall(maze, cx, cy, "E")
                    return

                if self._can_move(maze, cx, cy, "S"):
                    self._close_wall(maze, cx, cy, "S")
                    return

                # Fallback: close any internal open edge inside that 3x3
                for y in range(y0, y0 + 3):
                    for x in range(x0, x0 + 2):
                        if self._can_move(maze, x, y, "E"):
                            self._close_wall(maze, x, y, "E")
                            return

                for x in range(x0, x0 + 3):
                    for y in range(y0, y0 + 2):
                        if self._can_move(maze, x, y, "S"):
                            self._close_wall(maze, x, y, "S")
                            return

        # Everything fixed on this 3x3 area
        return

    # Creating non-perfect maze
    def _add_loops(
        self,
        maze: Maze,
        blocked: set[tuple[int, int]],
        density: float,
    ) -> None:
        """
        Open extra walls randomly to create loops (non-perfect maze).

        density is relative to the number of cells.
        Example: 0.06 means about 6% of cells try to open one extra wall.
        """
        if density <= 0.0:
            return

        attempts = int(self.width * self.height * density)
        if attempts < 1:
            return

        dirs = list(DIRS.keys())
        # Trying to open rando
        for _ in range(attempts):
            x = self.rng.randrange(self.width)
            y = self.rng.randrange(self.height)

            if (x, y) in blocked:
                continue

            d = self.rng.choice(dirs)
            dx, dy, _bit_current, _bit_opp = DIRS[d]
            nx = x + dx
            ny = y + dy

            if not self._in_bounds(nx, ny):
                continue
            if (nx, ny) in blocked:
                continue

            # Only open if currently closed
            if self._can_move(maze, x, y, d):
                continue

            self._open_wall(maze, x, y, d)

            # Keep the 3x3 rule safe: if forbidden, revert this opening.
            if self._has_forbidden_3x3(maze):
                self._close_wall(maze, x, y, d)

    def generate(self, entry: tuple[int, int], exit: tuple[int, int]) -> Maze:
        """Generate and return a Maze."""
        self._validate_params(entry, exit)

        maze = Maze(
            self.width,
            self.height,
            [[15 for _ in range(self.width)] for _ in range(self.height)],
        )

        # Define the 42 coords before generation.
        # Checking if the size allows the 42 or not.
        maze.omitted_42 = False
        try:
            blocked = self._get_42_coords(maze)
        except ValueError:
            blocked = set()
            maze.omitted_42 = True

        if entry in blocked:
            raise ValueError("Entry is inside the 42 pattern")
        if exit in blocked:
            raise ValueError("Exit is inside the 42 pattern")

        # dispatch by algorithm
        if self.algorithm in ("dfs", "recursive_backtracker"):
            self._generate_dfs(maze, start=entry, blocked=blocked)
        elif self.algorithm == "prim":
            self._generate_prim(maze, start=entry, blocked=blocked)
        else:
            self._generate_dfs(maze, start=entry, blocked=blocked)

        # If perfect is False, open extra walls to create loops.
        if not self.perfect:
            self._add_loops(maze, blocked=blocked, density=self.density)

        # stamp (store coords + force the 42 cells to 15)
        self._stamp_42(maze, blocked)

        # keep fixing until there are no forbidden windows (safe limit)
        for _ in range(self.width * self.height):
            if not self._has_forbidden_3x3(maze):
                break
            self._fix_forbidden_3x3(maze)

        return maze

    # SOLVER BFS
    def solve(
        self,
        maze: Maze,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> list[str]:
        """Return shortest path as list of moves like ['N','E',...]."""
        # Stores the cells to be explored
        q: deque[tuple[int, int]] = deque()
        # Set the already visited to avoid revisite
        visited: set[tuple[int, int]] = set()
        # Mapping each cell (previous cell, direcction)
        prev: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        q.append(entry)
        visited.add(entry)

        while q:
            x, y = q.popleft()

            if (x, y) == exit:
                break

            # Exploring the 4 directions
            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                if not self._can_move(maze, x, y, d):
                    continue

                # Calculating neighbor coordinates
                nx = x + dx
                ny = y + dy
                nxt = (nx, ny)

                if nxt in visited:
                    continue

                visited.add(nxt)
                prev[nxt] = ((x, y), d)
                q.append(nxt)

        # If exit not reached, no path
        if exit not in visited:
            return []

        # Reconstruct path exit -> entry
        path: list[str] = []
        cur = exit
        while cur != entry:
            (px, py), d = prev[cur]
            path.append(d)
            cur = (px, py)

        path.reverse()
        return path

    # Solver step-by-step animation support (BFS)
    def _reconstruct_path(
        self,
        prev: dict[tuple[int, int], tuple[tuple[int, int], str]],
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> list[str]:
        """Reconstruct path from prev dict, from exit back to entry."""
        if entry == exit:
            return []
        if exit not in prev:
            return []
        path: list[str] = []
        cur = exit
        while cur != entry:
            (px, py), d = prev[cur]
            path.append(d)
            cur = (px, py)
        path.reverse()
        return path

    def solve_bfs_steps(
        self,
        maze: Maze,
        entry: tuple[int, int],
        exit: tuple[int, int],
        yield_every: int = 1,
    ) -> Iterator[
        tuple[
            tuple[int, int],
            set[tuple[int, int]],
            set[tuple[int, int]],
            list[str],
        ]
    ]:
        """
        BFS solver that yields intermediate states for animation.

        yield_every controls how often we yield frames:
          - 1 yields every expansion (smooth but slower)
          - 5/10 yields fewer frames (faster)
        """
        q: deque[tuple[int, int]] = deque()
        visited: set[tuple[int, int]] = set()
        prev: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        q.append(entry)
        visited.add(entry)

        steps = 0

        # Initial frame
        yield (entry, set(visited), set(q), [])

        while q:
            cur = q.popleft()
            cx, cy = cur

            if cur == exit:
                break

            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                if not self._can_move(maze, cx, cy, d):
                    continue

                nx = cx + dx
                ny = cy + dy
                nxt = (nx, ny)

                if nxt in visited:
                    continue

                visited.add(nxt)
                prev[nxt] = (cur, d)
                q.append(nxt)

            steps += 1
            if yield_every > 0 and (steps % yield_every) == 0:
                yield (cur, set(visited), set(q), [])

        final_path = self._reconstruct_path(prev, entry, exit)

        # Final frame (path is available now)
        yield (exit, set(visited), set(q), final_path)

    def solve_steps(
        self,
        maze: Maze,
        entry: tuple[int, int],
        exit: tuple[int, int],
        solver: str = "bfs",
        yield_every: int = 1,
    ) -> Iterator[
        tuple[
            tuple[int, int],
            set[tuple[int, int]],
            set[tuple[int, int]],
            list[str],
        ]
    ]:
        """
        Small dispatcher so the renderer can animate the chosen solver.

        solver:
          - 'bfs'  (mandatory)
        """
        _ = solver
        return self.solve_bfs_steps(maze, entry, exit, yield_every=yield_every)

    # Generation steps
    def _iter_dfs_generation_steps(
        self,
        maze: Maze,
        entry: tuple[int, int],
        blocked: set[tuple[int, int]],
    ) -> Iterator[tuple[Maze, list[str]]]:
        """Yield intermediate (maze, []) states during DFS generation."""
        visited: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = []

        visited.add(entry)
        stack.append(entry)

        while stack:
            x, y = stack[-1]

            unvisited_neighbors: list[tuple[int, int, str]] = []
            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                nx = x + dx
                ny = y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in visited:
                    continue
                if (nx, ny) in blocked:
                    continue
                unvisited_neighbors.append((nx, ny, d))

            if not unvisited_neighbors:
                stack.pop()
                continue

            nx, ny, d = self.rng.choice(unvisited_neighbors)
            self._open_wall(maze, x, y, d)

            # Yield after carving a passage
            yield (maze, [])

            visited.add((nx, ny))
            stack.append((nx, ny))

    def _iter_prim_generation_steps(
        self,
        maze: Maze,
        entry: tuple[int, int],
        blocked: set[tuple[int, int]],
    ) -> Iterator[tuple[Maze, list[str]]]:
        """Yield intermediate (maze, []) states during Prim generation."""
        in_tree: set[tuple[int, int]] = set()
        frontier: list[tuple[int, int, int, int, str]] = []

        def add_frontier(x: int, y: int) -> None:
            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in in_tree:
                    continue
                if (nx, ny) in blocked:
                    continue
                frontier.append((x, y, nx, ny, d))

        sx, sy = entry
        in_tree.add((sx, sy))
        add_frontier(sx, sy)

        while frontier:
            i = self.rng.randrange(len(frontier))
            x, y, nx, ny, d = frontier.pop(i)

            if (nx, ny) in in_tree:
                continue

            self._open_wall(maze, x, y, d)

            # Yield after carving a passage
            yield (maze, [])

            in_tree.add((nx, ny))
            add_frontier(nx, ny)

    def iter_generation_steps(
        self,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> Iterator[tuple[Maze, list[str]]]:
        """Yield intermediate (maze, path_so_far) states during generation."""
        self._validate_params(entry, exit)

        maze = Maze(
            self.width,
            self.height,
            [[15 for _ in range(self.width)] for _ in range(self.height)],
        )

        maze.omitted_42 = False
        try:
            blocked = self._get_42_coords(maze)
        except ValueError:
            blocked = set()
            maze.omitted_42 = True

        if entry in blocked:
            raise ValueError("Entry is inside the 42 pattern")
        if exit in blocked:
            raise ValueError("Exit is inside the 42 pattern")

        # Step-by-step generation (algorithm-aware)
        algo = self.algorithm.lower().strip() if self.algorithm else "dfs"

        if algo in ("dfs", "recursive_backtracker"):
            yield from self._iter_dfs_generation_steps(
                maze, entry=entry, blocked=blocked
            )
        elif algo == "prim":
            yield from self._iter_prim_generation_steps(
                maze, entry=entry, blocked=blocked
            )
        else:
            # Fallback: behave like DFS
            yield from self._iter_dfs_generation_steps(
                maze, entry=entry, blocked=blocked
            )

        # Optional loops for non-perfect maze
        if not self.perfect:
            self._add_loops(maze, blocked=blocked, density=self.density)
            yield (maze, [])

        # Apply constraints
        self._stamp_42(maze, blocked)

        for _ in range(self.width * self.height):
            if not self._has_forbidden_3x3(maze):
                break
            self._fix_forbidden_3x3(maze)

        final_path = self.solve(maze, entry, exit)

        # Final frame with solution
        yield (maze, final_path)
