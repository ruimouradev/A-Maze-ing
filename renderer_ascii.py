# ============================================================
# File: renderer_ascii.py
#
# OWNER:
#   Alexandre
#
# ROLE:
#   Terminal ASCII visualization and interaction.
#
# ALEXANDRE MUST (mandatory): All done
#   1) Render maze walls
#   2) Render entry and exit
#   3) Toggle solution path
#   4) Change wall colors (ANSI)
#   5) Regenerate maze
#
# BONUS: Still to be implemented
#   - Toggle animation (cfg.animate)
#   - Change algorithm at runtime (dfs/prim/kruskal/wilson)
#   - Display generation steps using gen.iter_steps(...) when available
#
# Recommended commands:
#   r = regenerate
#   p = toggle path
#   c = cycle colors
#
#   NOT IMPLEMENTED YET
#   a = toggle animation
#   g = change algorithm
#   q = quit

from __future__ import annotations

import sys
import time
from config import Config
from mazegen import MazeGenerator, Maze
from serializer import write_output_file


class AsciiRenderer:
    def __init__(self) -> None:
        """Initialize renderer with path visibility and wall color palette."""
        self.show_path = True
        self.animate = False  # Toggle animation on/off
        # Wall colors that don't conflict with entry (green) or exit (red)
        self.wall_colors = [
            "\033[0m",   # Default (white)
            "\033[33m",  # Yellow
            "\033[34m",  # Blue
            "\033[36m",  # Cyan
            "\033[35m",  # Magenta
        ]
        self.color_index = 0
        self.wall_color = self.wall_colors[0]
        self.animation_speed = 0.01  # 10ms per frame

    def _draw_maze(
        self,
        maze: Maze,
        cfg: Config,
        path: list[str],
        visited: set[tuple[int, int]] | None = None,
        frontier: set[tuple[int, int]] | None = None,
        current: tuple[int, int] | None = None,
    ) -> None:
        """Render maze grid with walls, entry, exit, and solution path.

        Uses 3×3 ASCII blocks per cell: corners and walls are colored blocks,
        entry/exit/path are colored center characters, floors are spaces.

        Args:
            maze: Maze grid with wall bitmasks (0-15).
            cfg: Configuration with entry/exit coordinates.
            path: Solution path as direction list to convert to coordinates.
        """
        # Define colors
        WALL_COLOR = self.wall_color  # Set by user interaction
        ENTRY_COLOR = "\033[32m"      # Green
        EXIT_COLOR = "\033[31m"       # Red
        PATH_COLOR = "\033[96m"       # Bright cyan for solution path
        STAMP_COLOR = "\033[93m"      # Bright yellow for the 42 stamp
        RESET = "\033[0m"             # reset color to default

        BLOCK = "█"

        # Convert path directions to coordinates
        path_coords = set()
        path_connectors: set[tuple[int, int, str]] = set()
        stamp_coords: set[tuple[int, int]] = getattr(
            maze, "stamp42", set()
        )
        has_stamp = bool(stamp_coords)

        if self.show_path and path:
            x, y = cfg.entry
            path_coords.add((x, y))  # Include entry in path
            for direction in path:
                gx, gy = 2 * x + 1, 2 * y + 1
                if direction == 'N':
                    path_connectors.add((gy - 1, gx, "V"))
                    y -= 1
                elif direction == 'S':
                    path_connectors.add((gy + 1, gx, "V"))
                    y += 1
                elif direction == 'E':
                    path_connectors.add((gy, gx + 1, "H"))
                    x += 1
                elif direction == 'W':
                    path_connectors.add((gy, gx - 1, "H"))
                    x -= 1
                else:
                    # Skip invalid directions
                    continue
                path_coords.add((x, y))
            # Ensure exit is in path_coords
            path_coords.add(cfg.exit)

        wall_chars = {
            "─",
            "│",
            "┌",
            "┐",
            "└",
            "┘",
            "├",
            "┤",
            "┬",
            "┴",
            "┼",
        }

        def _junction_char(
            up: bool, down: bool, left: bool, right: bool
        ) -> str:
            key = (up, down, left, right)
            mapping = {
                (False, False, False, False): " ",
                (True, True, False, False): "│",
                (False, False, True, True): "─",
                (False, True, False, True): "┌",
                (False, True, True, False): "┐",
                (True, False, False, True): "└",
                (True, False, True, False): "┘",
                (True, True, False, True): "├",
                (True, True, True, False): "┤",
                (False, True, True, True): "┬",
                (True, False, True, True): "┴",
                (True, True, True, True): "┼",
            }
            return mapping.get(key, " ")

        rows = len(maze.cells)
        cols = len(maze.cells[0]) if rows > 0 else 0
        grid_h = rows * 2 + 1
        grid_w = cols * 2 + 1
        grid: list[list[str]] = [
            [" " for _ in range(grid_w)] for _ in range(grid_h)
        ]

        for y, row in enumerate(maze.cells):
            for x, cell_value in enumerate(row):
                # 1. Determine cell type and center character
                if (x, y) == cfg.entry:
                    center_char = f"{ENTRY_COLOR}{BLOCK}{RESET}"
                elif (x, y) == cfg.exit:
                    center_char = f"{EXIT_COLOR}{BLOCK}{RESET}"
                elif has_stamp and (x, y) in stamp_coords:
                    center_char = f"{STAMP_COLOR}{BLOCK}{RESET}"
                elif current and (x, y) == current:
                    center_char = "\033[95m█\033[0m"   # roxo = cursor
                elif frontier and (x, y) in frontier:
                    center_char = "\033[94m█\033[0m"   # azul = frontier
                elif visited and (x, y) in visited:
                    center_char = "\033[90m█\033[0m"   # cinza = visited
                elif (x, y) in path_coords:
                    center_char = f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    center_char = " "

                grid[2 * y + 1][2 * x + 1] = center_char

                # 2. Build the walls using bitmasking
                # (cell_value is 0-15: N=1, E=2, S=4, W=8)
                n_wall_exists = bool(cell_value & 1)
                e_wall_exists = bool(cell_value & 2)
                s_wall_exists = bool(cell_value & 4)
                w_wall_exists = bool(cell_value & 8)

                if n_wall_exists:
                    grid[2 * y][2 * x + 1] = "─"
                if s_wall_exists:
                    grid[2 * y + 2][2 * x + 1] = "─"
                if w_wall_exists:
                    grid[2 * y + 1][2 * x] = "│"
                if e_wall_exists:
                    grid[2 * y + 1][2 * x + 2] = "│"

        # 3. Add path connectors so color is continuous between cells
        for gy, gx, orient in path_connectors:
            if 0 <= gy < grid_h and 0 <= gx < grid_w:
                if grid[gy][gx] == " ":
                    grid[gy][gx] = orient

        path_center_grid = {
            (2 * y + 1, 2 * x + 1) for (x, y) in path_coords
        }

        # 4. Resolve junctions for continuous lines
        for gy in range(0, grid_h, 2):
            for gx in range(0, grid_w, 2):
                up = gy > 0 and grid[gy - 1][gx] == "│"
                down = gy < grid_h - 1 and grid[gy + 1][gx] == "│"
                left = gx > 0 and grid[gy][gx - 1] == "─"
                right = gx < grid_w - 1 and grid[gy][gx + 1] == "─"
                grid[gy][gx] = _junction_char(up, down, left, right)

        # 5. Print the grid with colored walls
        right_edge_chars = {"─", "┌", "└", "├", "┬", "┴", "┼"}
        for gy, grid_row in enumerate(grid):
            line = ""
            for gx, ch in enumerate(grid_row):
                if ch in wall_chars:
                    line += f"{WALL_COLOR}{ch}{RESET}"
                elif ch == "H":
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                elif ch == "V":
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    line += ch
                if gx == grid_w - 1:
                    continue
                next_ch = grid_row[gx + 1]
                if ch in right_edge_chars:
                    line += f"{WALL_COLOR}─{RESET}"
                elif ch == "H":
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                elif (gy, gx) in path_center_grid and (
                    next_ch == "H" or (gy, gx + 1) in path_center_grid
                ):
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    line += " "
            print(line)

    def _animate_solver(
        self,
        gen: MazeGenerator,
        cfg: Config,
        maze: Maze,
        solver: str = "bfs",
        yield_every: int = 1,
    ) -> list[str]:
        """Animate solver (BFS / A*) step-by-step.

        We keep maze generation instant, and animate only the solver search.
        """
        final_path: list[str] = []

        if solver == "astar":
            steps_it = gen.solve_astar_steps(
                maze,
                cfg.entry,
                cfg.exit,
                yield_every=yield_every,
            )
        else:
            steps_it = gen.solve_bfs_steps(
                maze,
                cfg.entry,
                cfg.exit,
                yield_every=yield_every,
            )

        # Clear once, then only move cursor to home to reduce flicker.
        print("\033[2J\033[H\033[?25l", end="", flush=True)

        for cur, visited, frontier, step_path in steps_it:
            print("\033[H", end="", flush=True)
            self._draw_maze(
                maze,
                cfg,
                step_path,
                visited=visited,
                frontier=frontier,
                current=cur,
            )

            final_path = step_path
            time.sleep(self.animation_speed)

        print("\033[?25h", end="", flush=True)
        return final_path

    def run(
        self,
        maze: Maze,
        path: list[str],
        gen: MazeGenerator,
        cfg: Config,
    ) -> None:
        """Render maze and handle interactive commands in main event loop.

        Commands:
            (r)egenerate - Create and solve new maze (instant or animated)
            (p)ath - Toggle solution path display
            (c)olor - Cycle wall color
            (a)nimation - Toggle solver animation
            (q)uit - Exit program

        Args:
            maze: Initial maze to display.
            path: Solution path as direction list ['N', 'E', 'S', 'W', ...].
            gen: Maze generator engine for regeneration.
            cfg: Configuration with maze dimensions and entry/exit points.
        """
        current_maze = maze  # Use the maze passed from a_maze_ing.py
        current_path = path  # Solution path to display

        while True:
            # 1. Clear terminal
            # (\033 = esc; [2J = Clear entire screen; [H = Home)
            print("\033[2J\033[H", end="", flush=True)

            # 2. Draw the maze: render walls, entry, and exit
            self._draw_maze(current_maze, cfg, current_path)

            # 3. Handle interaction
            anim_status = " [ANIMATED]" if self.animate else ""
            cmd = input(
                f"\n(r)egenerate, (p)ath, (c)olor, "
                f"(a)nimation{anim_status}, (q)uit: "
            ).lower()

            if cmd == 'q':
                break
            elif cmd == 'p':
                self.show_path = not self.show_path
            elif cmd == 'c':
                # Cycle to next wall color (skip green/red for entry/exit)
                self.color_index = (
                    (self.color_index + 1) % len(self.wall_colors)
                )
                self.wall_color = self.wall_colors[self.color_index]
            elif cmd == 'a':
                # Toggle animation on/off
                self.animate = not self.animate
            elif cmd == 'r':
                # Clear terminal and move cursor to top
                print("\033[2J\033[H", end="", flush=True)
                print("Regenerating maze...", flush=True)

                # Always regenerate instantly (cleaner visuals).
                current_maze = gen.generate(cfg.entry, cfg.exit)

                if self.animate and self.show_path:
                    # Animate solver only if both animation and path
                    # are enabled
                    # Option A: always BFS
                    current_path = self._animate_solver(
                        gen,
                        cfg,
                        current_maze,
                        solver="bfs",
                        yield_every=1,
                    )

                    # Option B: always A*
                    # current_path = self._animate_solver(
                    #     gen,
                    #     cfg,
                    #     current_maze,
                    #     solver="astar",
                    #     yield_every=1,
                    # )
                else:
                    # Solve instantly (no animation).
                    current_path = gen.solve(
                        current_maze,
                        cfg.entry,
                        cfg.exit,
                    )
                # Write the regenerated maze to output file
                try:
                    write_output_file(
                        output_path=cfg.output_file,
                        maze=current_maze,
                        entry=cfg.entry,
                        exit=cfg.exit,
                        path=current_path,
                    )
                except ValueError as e:
                    print(f"\nError writing file: {e}", file=sys.stderr)
