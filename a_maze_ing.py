# ============================================================
# File: a_maze_ing.py
#
# OWNER:
#   Alexandre
#
# ROLE:
#   Entry point and program orchestration.
#
# ALEXANDRE MUST (obrigatório):
#   1) Parse CLI args (sys.argv) -> config path
#   2) Call load_config()
#   3) Instantiate MazeGenerator
#   4) Call generate() and solve()
#   5) Call write_output_file()
#   6) Launch ASCII renderer loop
#
# BONUS hooks:
#   - Support cfg.animate: if True, prefer gen.iter_steps(...) for animation
#   - Support changing algorithm at runtime via renderer commands
#
# MUST NOT:
#   - Implement algorithms
#   - Modify maze internals directly

from __future__ import annotations  # Enable forward type hints

import sys  # Used to read command-line arguments and exit codes

from config import load_config          # Reads and validates config file
from mazegen import MazeGenerator       # Core maze engine (Rui)
from serializer import write_output_file  # Writes maze to output file
from renderer_ascii import AsciiRenderer  # Terminal ASCII UI


def main(argv: list[str]) -> int:
    """Orchestrate maze generation, solving, and rendering.

    Workflow:
        1. Parse and validate config file
        2. Create maze generator with config parameters
        3. Generate and solve maze
        4. Write solution to output file
        5. Launch interactive ASCII renderer

    Args:
        argv: Command-line arguments; argv[0]=script name,
            argv[1]=config file path.

    Returns:
        Exit code: 0 (success), 1 (config/write error), 2 (usage error).
    """

    # Validate CLI usage: exactly one argument expected
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 2

    try:
        # Load configuration from provided file path
        cfg = load_config(argv[1])

    except (FileNotFoundError, ValueError) as e:
        # Print to stderr as per 42 standards
        print(f"Error: {e}", file=sys.stderr)
        return 1  # Exit with a non-zero status

    # Create maze generator using config parameters
    gen = MazeGenerator(
        width=cfg.width,
        height=cfg.height,
        seed=cfg.seed,
        perfect=cfg.perfect,
        algorithm=cfg.algorithm,
    )

    # Generate maze structure
    maze = gen.generate(entry=cfg.entry, exit=cfg.exit)

    # Solve maze to obtain shortest path
    path = gen.solve(maze, cfg.entry, cfg.exit)

    # Write maze + solution to output file
    try:
        write_output_file(
            output_path=cfg.output_file,
            maze=maze,
            entry=cfg.entry,
            exit=cfg.exit,
            path=path,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Launch ASCII renderer (static or animated)
    AsciiRenderer().run(gen=gen, cfg=cfg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
