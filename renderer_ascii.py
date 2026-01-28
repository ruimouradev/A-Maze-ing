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

from config import Config
from mazegen import MazeGenerator, Maze


class AsciiRenderer:
    def __init__(self) -> None:
        """Initialize renderer with path visibility and wall color palette."""
        self.show_path = True
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

    def _draw_maze(
        self, maze: Maze, cfg: Config, path: list[str]
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
        RESET = "\033[0m"             # reset color to default

        BLOCK = "█"

        # Convert path directions to coordinates
        path_coords = set()
        if self.show_path and path:
            x, y = cfg.entry
            path_coords.add((x, y))  # Include entry in path
            for direction in path:
                if direction == 'N':
                    y -= 1
                elif direction == 'S':
                    y += 1
                elif direction == 'E':
                    x += 1
                elif direction == 'W':
                    x -= 1
                else:
                    # Skip invalid directions
                    continue
                path_coords.add((x, y))

        # loops through all lines of the maze, one at a time
        for y, row in enumerate(maze.cells):
            line_top = ""
            line_mid = ""
            line_bot = ""

            # loop that processes 1 line (prints 3 x 3 blocks)
            for x, cell_value in enumerate(row):
                # 1. Determine Center Color (Entry vs Exit vs Path)
                if (x, y) == cfg.entry:
                    center_char = f"{ENTRY_COLOR}{BLOCK}{RESET}"
                elif (x, y) == cfg.exit:
                    center_char = f"{EXIT_COLOR}{BLOCK}{RESET}"
                elif (x, y) in path_coords:
                    # Show path cell in bright cyan
                    center_char = f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    center_char = " "  # Space for floor

                # 2. Build the walls using bitmasking
                # (cell_value is 0-15: N=1, E=2, S=4, W=8)
                # Check bit 0 for north wall (1=exists, 0=no wall)
                n_wall = (
                    f"{WALL_COLOR}{BLOCK*3}{RESET}"
                    if cell_value & 1 else "   "
                )
                # Check bit 1 for east wall (1=exists, 0=no wall)
                e_wall = (
                    f"{WALL_COLOR}{BLOCK}{RESET}"
                    if cell_value & 2 else " "
                )
                # Check bit 2 for south wall (1=exists, 0=no wall)
                s_wall = (
                    f"{WALL_COLOR}{BLOCK*3}{RESET}"
                    if cell_value & 4 else "   "
                )
                # Check bit 3 for west wall (1=exists, 0=no wall)
                w_wall = (
                    f"{WALL_COLOR}{BLOCK}{RESET}"
                    if cell_value & 8 else " "
                )
                corner = f"{WALL_COLOR}{BLOCK}{RESET}"

                # 3. Construct 3x3 Block
                line_top += f"{corner}{n_wall}{corner}"
                line_mid += f"{w_wall} {center_char} {e_wall}"
                line_bot += f"{corner}{s_wall}{corner}"

            print(line_top)
            print(line_mid)
            print(line_bot)

    def run(
        self,
        maze: Maze,
        path: list[str],
        gen: MazeGenerator,
        cfg: Config,
    ) -> None:
        """Render maze and handle interactive commands in main event loop.

        Commands:
            (r)egenerate - Create and solve new maze
            (p)ath - Toggle solution path display
            (c)olor - Cycle wall color
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
            # 1. Clear terminal (s\033 = esc; [H = Home; \033[J = Erase)
            print("\033[H\033[J", end="")

            # 2. Draw the maze: render walls, entry, and exit
            self._draw_maze(current_maze, cfg, current_path)

            # 3. Handle interaction
            cmd = input(
                "\n(r)egenerate, (p)ath, (c)olor, (q)uit: "
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
            elif cmd == 'r':
                # Use the generator engine to create a NEW maze
                current_maze = gen.generate(cfg.entry, cfg.exit)
                # Solve the new maze and update path
                current_path = gen.solve(
                    current_maze, cfg.entry, cfg.exit
                )
            # Add other logic for animation and algorithm changes
