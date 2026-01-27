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

    # ============================================================
    # STEP 1 — BASE HELPERS (OBRIGATÓRIO)
    #
    # Objetivo: nunca quebrar coerência das paredes (passar sempre validator).
    #
    # 1.1 Implementar:
    #   def _in_bounds(self, x: int, y: int) -> bool:
    #       - True se 0 <= x < width e 0 <= y < height
    #
    # 1.2 Implementar:
    #   def _open_wall(self, maze: Maze, x: int, y: int, d: str) -> None:
    #       - Abre a parede no lado d da célula (x,y)
    #       - Abre a parede oposta na célula vizinha
    #       - Usa DIRS[d] para obter bits e dx/dy
    #       - NUNCA abrir para fora do bounds (se vizinho fora, não faz nada)
    #
    # 1.3 Implementar:
    #   def _can_move(self, maze: Maze, x: int, y: int, d: str) -> bool:
    #       - True se não há parede fechada naquele lado e o vizinho existe
    #
    # Fonte (bitmask):
    #   https://www.learncpp.com/cpp-tutorial/bitmasks/
    #
    # Fonte (maze/grafo):
    #   https://en.wikipedia.org/wiki/Maze_generation_algorithm
    # ============================================================

    # TODO STEP 1.1: _in_bounds(...)
    # TODO STEP 1.2: _open_wall(...)
    # TODO STEP 1.3: _can_move(...)

    # ============================================================
    # STEP 2 — VALIDAR PARAMS (OBRIGATÓRIO)
    #
    # Objetivo: falhar cedo com erro claro se config inválido.
    #
    # Implementar:
    #   def _validate_params(self, entry: tuple[int,int], exit: tuple[int,int]) -> None:
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
    #           - se liga a célula fora -> _open_wall e adicionar novas fronteiras
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
    #               - se uma célula é forced-closed, o vizinho tem de ter o wall oposto fechado
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

    def solve(self, maze: Maze, entry: tuple[int, int], exit: tuple[int, int]) -> list[str]:
        """Return shortest path as list of moves like ['N','E',...]."""
        # TODO STEP 7: BFS solver
        return []

    # ============================================================
    # STEP 8 — SOLVER A* (BÓNUS: 2º solver)
    #
    # Implementar:
    #   def solve_astar(self, maze: Maze, entry: tuple[int,int], exit: tuple[int,int]) -> list[str]:
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
