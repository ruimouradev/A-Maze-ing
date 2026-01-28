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
#   7) Add A* solver (2nd resolution algorithm)  <-- to match your "bonus full"
#   8) Add iter_steps() generator for animation support
#
# MUST NOT:
#   - Print to terminal
#   - Read/write files
#   - Handle user input
# ============================================================

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
    # ============================================================

    # ============================================================
    # STEP 2 — VALIDAR PARAMS (OBRIGATÓRIO)
    #
    # Objetivo: falhar cedo com erro claro se config inválido.
    #
    # Implementar:
    #   def _validate_params(self, entry: tuple[int,int],
    #                           exit: tuple[int,int]) -> None:
    #       - width/height > 0
    #       - entry in bounds
    #       - exit in bounds
    #       - entry != exit
    #
    # Nota: tu lanças ValueError; o Alexandre é que imprime bonito.
    # ============================================================

    # TODO STEP 2: _validate_params(...)

    # ============================================================
    # STEP 3 — GERAÇÃO DFS (MANDATORY)
    #
    # Objetivo: perfect maze baseline (recursive backtracker / DFS).
    #
    # Onde: criar função privada e chamá-la no generate()
    #
    # Implementar:
    #   def _generate_dfs(self, maze: Maze, start: tuple[int,int]) -> None:
    #       - visited set
    #       - stack
    #       - enquanto stack:
    #           - ver vizinhos não visitados
    #           - escolher aleatoriamente (self.rng.choice)
    #           - _open_wall(...)
    #           - push vizinho e marcar visited
    #           - se sem vizinhos: pop (backtrack)
    #
    # Fonte (DFS maze):
    #   https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap
    # ============================================================

    # TODO STEP 3: _generate_dfs(...)

    # ============================================================
    # STEP 4 — GERAÇÃO PRIM (BÓNUS: 2º algoritmo de geração)
    #
    # Implementar:
    #   def _generate_prim(self, maze: Maze, start: tuple[int,int]) -> None:
    #       - conjunto de células "na árvore"
    #       - lista de arestas/fronteira
    #       - repetir:
    #           - escolher aresta aleatória
    #           - liga-se a célula fora -> _open_wall e add novas fronteiras
    #
    # Fonte (Prim maze):
    #   https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm
    # ============================================================

    # TODO STEP 4: _generate_prim(...)

    # ============================================================
    # STEP 5 — CONSTRAINT: "42" pattern (OBRIGATÓRIO)
    #
    # Objetivo: desenhar "42" com células totalmente fechadas (valor 15).
    #
    # Implementar:
    #   def _stamp_42(self, maze: Maze) -> None:
    #       - escolher posição (normalmente centro)
    #       - aplicar um "molde" (lista de coords) para formar 4 e 2
    #       - para cada célula do molde:
    #           - forçar maze.set(x,y,15)
    #           - garantir coerência com vizinhos:
    #               - se uma célula é forced-closed,
    #                   o vizinho tem de ter o wall oposto fechado
    #       - se maze demasiado pequeno -> raise ValueError("...too small...")
    #
    # Fonte (grelhas / offsets):
    #   https://www.redblobgames.com/grids/intro/
    # ============================================================

    # TODO STEP 5: _stamp_42(...)

    # ============================================================
    # STEP 6 — CONSTRAINT: "no 3x3 open area" (OBRIGATÓRIO)
    #
    # Objetivo: evitar áreas abertas grandes.
    #
    # Implementar (abordagem prática):
    #   def _has_forbidden_3x3(self, maze: Maze) -> bool:
    #       - varrer todas as janelas 3x3
    #       - definir critério "aberto demais" (o vosso)
    #
    #   def _fix_forbidden_3x3(self, maze: Maze) -> None:
    #       - se encontrar violação, fechar UMA passagem (mantendo coerência)
    #
    # Fonte (flood fill / áreas):
    #   https://www.geeksforgeeks.org/flood-fill-algorithm/
    # ============================================================

    # TODO STEP 6: _has_forbidden_3x3(...)
    # TODO STEP 6: _fix_forbidden_3x3(...)

    # -----------------------
    # Required public API
    # -----------------------

    def generate(self, entry: tuple[int, int], exit: tuple[int, int]) -> Maze:
        """Generate and return a Maze."""

        # STEP 2: chamar _validate_params(entry, exit)

        maze = Maze(
            self.width,
            self.height,
            [[15 for _ in range(self.width)] for _ in range(self.height)],
        )

        # STEP 3/4: dispatch por algoritmo
        if self.algorithm in ("dfs", "recursive_backtracker"):
            # STEP 3: self._generate_dfs(maze, start=entry)
            pass
        elif self.algorithm == "prim":
            # STEP 4: self._generate_prim(maze, start=entry)
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

        # STEP 5: self._stamp_42(maze)
        # STEP 6: garantir regra 3x3 (check + fix)
        return maze

    # ============================================================
    # STEP 7 — SOLVER BFS (MANDATORY: caminho mais curto)
    #
    # Implementar BFS em grelha usando paredes:
    #   - queue (deque)
    #   - visited
    #   - prev[(x,y)] = (px,py,dir)
    #   - reconstruir lista ['N','E','S','W']
    #
    # Fonte (BFS em grids):
    #   https://www.redblobgames.com/pathfinding/a-star/introduction.html
    # ============================================================

    def solve(self,
              maze: Maze,
              entry: tuple[int, int],
              exit: tuple[int, int]) -> list[str]:
        """Return shortest path as list of moves like ['N','E',...]."""
        # TODO STEP 7: BFS solver
        return []

    # ============================================================
    # STEP 8 — SOLVER A* (BÓNUS: 2º solver)
    #
    # Implementar:
    #   def solve_astar(self, maze: Maze, entry: tuple[int,int],
    #                       exit: tuple[int,int]) -> list[str]:
    #       - heurística Manhattan
    #       - priority queue (heapq)
    #       - gscore, prev
    #       - reconstruir lista ['N','E','S','W']
    #
    # Depois decidir como selecionar:
    #   - OU adicionam SOLVER=... no config (Alexandre)
    #   - OU deixam A* como função extra chamada manualmente (menos ideal)
    #
    # Fonte (A*):
    #   https://www.redblobgames.com/pathfinding/a-star/introduction.html
    # ============================================================

    # TODO STEP 8: solve_astar(...)

    # -----------------------
    # BONUS public API
    # -----------------------
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
