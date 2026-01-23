# A-Maze-ing (Bonus-ready skeleton)

This repository contains a **bonus-ready** structure with clear ownership and TODOs.

## Ownership
- **Rui (Person A):** `mazegen.py` (core engine + algorithms + solver + constraints + bonus hooks)
- **Alexandre (Person B):** `a_maze_ing.py`, `config.py`, `serializer.py`, `renderer_ascii.py`, `Makefile`, `requirements.txt`, docs

## Bonus targets supported by this structure
- Multiple generation algorithms (`ALGORITHM=dfs|prim|kruskal|wilson` stubs)
- Optional step-by-step generation (`iter_steps`) for animation
- ASCII interactions: regenerate, toggle path, change colors, change algorithm, toggle animation
- Safe fallback: if a bonus isn't implemented, program still runs with DFS + static render

## Quick start
```bash
make install
make run
```
