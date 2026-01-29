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
from collections import deque
import heapq

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

        # This will store the coordinates of the 42 pattern.
        # This is better than assuming "cell == 15" means it belongs to the 42.
        self.stamp42: set[tuple[int, int]] = set()

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
            raise ValueError("Width and height must be greater than 0")

        ex, ey = entry
        tx, ty = exit

        if not self._in_bounds(ex, ey):
            raise ValueError(f"Entry out of bounds: {entry}")

        if not self._in_bounds(tx, ty):
            raise ValueError(f"Exit out of bounds: {exit}")

        if entry == exit:
            raise ValueError("Entry and exit must be different")

    def _generate_dfs(self, maze: Maze, start: tuple[int, int]) -> None:
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
            x, y = stack[-1]

            unvisited_neighbors: list[tuple[int, int, str]] = []
            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                nx = x + dx
                ny = y + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                    # Candidate neighbor: in bounds and not visited yet
                    unvisited_neighbors.append((nx, ny, d))

            # If none exist we pop (going back)
            if not unvisited_neighbors:
                stack.pop()
                continue

            # Choosing a random neighbor
            nx, ny, d = self.rng.choice(unvisited_neighbors)
            # Opening both walls
            self._open_wall(maze, x, y, d)
            visited.add((nx, ny))
            stack.append((nx, ny))

    #
    # Fonte (DFS maze):
    #   https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap

    def _generate_prim(self, maze: Maze, start: tuple[int, int]) -> None:
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
                if self._in_bounds(nx, ny) and (nx, ny) not in in_tree:
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


    def _stamp_42(self, maze: Maze) -> None:
        """
        Stamp the "42" into the maze by forcing some cells to be closed (15).
        Also fixes neighbor walls so no neighbor has an open wall.
        """
        # Pattern is 11x7: "4" (5 cols) + 1 col gap + "2" (5 cols)
        # '.' means "leave as is"; any other char means "force this cell to 15"
        pattern = [
            "#...#.#####",
            "#...#.....#",
            "#...#.....#",
            "#####.#####",
            "....#.#....",
            "....#.#....",
            "....#.#####",
        ]

        pat_h = len(pattern)
        pat_w = len(pattern[0])

        # If the maze is too small to fit the pattern, fail early
        if maze.width < pat_w or maze.height < pat_h:
            raise ValueError("Maze too small for 42 pattern")

        # Center the pattern in the maze
        ox = (maze.width - pat_w) // 2
        oy = (maze.height - pat_h) // 2

        # Save coords of the 42 pattern so Alexandre can color it safely
        maze.stamp42.clear()

        for py in range(pat_h):
            row = pattern[py]
            for px in range(pat_w):
                if row[px] == ".":
                    continue

                x = ox + px
                y = oy + py

                # Save this cell as part of the 42
                maze.stamp42.add((x, y))

                # Force this cell to be fully closed (all walls closed)
                maze.set(x, y, 15)

                # Fix neighbors so nobody has open walls into this closed cell
                for d, (dx, dy, _bit_current,
                        bit_neighbor_opposite) in DIRS.items():
                    nx = x + dx
                    ny = y + dy
                    if not self._in_bounds(nx, ny):
                        continue

                    # Ensure the neighbor has its wall facing (x,y) CLOSED
                    neighbor = maze.get(nx, ny)
                    maze.set(nx, ny, neighbor | bit_neighbor_opposite)


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
        for y0 in range(0, maze.height - 2):
            for x0 in range(0, maze.width - 2):
                all_open = True

                # Check horizontal internal corridors inside the 3x3
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

                # Found a forbidden 3x3: pick a simple internal wall to close.
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

        # Nothing to fix
        return

    # Required public API

    def generate(self, entry: tuple[int, int], exit: tuple[int, int]) -> Maze:
        """Generate and return a Maze."""
        self._validate_params(entry, exit)

        maze = Maze(
            self.width,
            self.height,
            [[15 for _ in range(self.width)] for _ in range(self.height)],
        )

        if self.algorithm in ("dfs", "recursive_backtracker"):
            self._generate_dfs(maze, start=entry)
        elif self.algorithm == "prim":
            self._generate_prim(maze, start=entry)
        else:
            self._generate_dfs(maze, start=entry)

        self._stamp_42(maze)

        for _ in range(self.width * self.height):
            if not self._has_forbidden_3x3(maze):
                break
            self._fix_forbidden_3x3(maze)

        return maze


    def solve(self,
              maze: Maze,
              entry: tuple[int, int],
              exit: tuple[int, int]) -> list[str]:
        """Return shortest path as list of moves like ['N','E',...]."""
        q: deque[tuple[int, int]] = deque()
        visited: set[tuple[int, int]] = set()
        prev: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        q.append(entry)
        visited.add(entry)

        while q:
            x, y = q.popleft()

            if (x, y) == exit:
                break

            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                if not self._can_move(maze, x, y, d):
                    continue

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


    def solve_astar(self,
                    maze: Maze,
                    entry: tuple[int, int],
                    exit: tuple[int, int]) -> list[str]:
        """
        Return a path using A* (Manhattan heuristic) as list
        of moves like ['N','E',...].
        """

        def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # heap item: (fscore, gscore, node)
        open_heap: list[tuple[int, int, tuple[int, int]]] = []
        gscore: dict[tuple[int, int], int] = {entry: 0}
        prev: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        heapq.heappush(open_heap, (manhattan(entry, exit), 0, entry))
        closed: set[tuple[int, int]] = set()

        while open_heap:
            _f, g, (x, y) = heapq.heappop(open_heap)

            if (x, y) in closed:
                continue
            closed.add((x, y))

            if (x, y) == exit:
                break

            for d, (dx, dy, _bit_current, _bit_opp) in DIRS.items():
                if not self._can_move(maze, x, y, d):
                    continue

                nx = x + dx
                ny = y + dy
                nxt = (nx, ny)

                tentative_g = g + 1
                if nxt in gscore and tentative_g >= gscore[nxt]:
                    continue

                gscore[nxt] = tentative_g
                prev[nxt] = ((x, y), d)

                fscore = tentative_g + manhattan(nxt, exit)
                heapq.heappush(open_heap, (fscore, tentative_g, nxt))

        # If no path found
        if entry != exit and exit not in prev:
            return []

        # Reconstruct path
        path: list[str] = []
        cur = exit
        while cur != entry:
            (px, py), d = prev[cur]
            path.append(d)
            cur = (px, py)
        path.reverse()
        return path


    def iter_steps(self,
                   entry: tuple[int, int],
                   exit: tuple[int, int]) -> Iterator[tuple[Maze, list[str]]]:
        """Yield intermediate (maze, path_so_far) states for animation."""
        self._validate_params(entry, exit)

        maze = Maze(
            self.width,
            self.height,
            [[15 for _ in range(self.width)] for _ in range(self.height)],
        )

        # Step-by-step DFS generation
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
                if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                    unvisited_neighbors.append((nx, ny, d))

            if not unvisited_neighbors:
                stack.pop()
                continue

            nx, ny, d = self.rng.choice(unvisited_neighbors)
            self._open_wall(maze, x, y, d)

            # Yield after carving a passage so renderer can animate
            yield (maze, [])

            visited.add((nx, ny))
            stack.append((nx, ny))

        # Apply constraints after generation
        self._stamp_42(maze)

        for _ in range(self.width * self.height):
            if not self._has_forbidden_3x3(maze):
                break
            self._fix_forbidden_3x3(maze)

        # Final solve and yield solution
        final_path = self.solve(maze, entry, exit)
        yield (maze, final_path)
