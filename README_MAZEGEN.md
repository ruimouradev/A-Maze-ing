## Reusable Code Architecture

The reusable component required by Chapter VI is the standalone Python module
`mazegen.py`, which is packaged as `mazegen-1.0.0.tar.gz` and located at the
root of the repository. This module can be installed independently via pip:

```bash
pip install ./mazegen-1.0.0.tar.gz
```

### Short Documentation (required by subject)

**Instantiate and use the generator (basic example):**

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=31, height=21, seed=42,
                    perfect=True, algorithm="dfs")
entry = (1, 1)
exit_ = (29, 19)

maze = gen.generate(entry=entry, exit=exit_)
path = gen.solve(maze=maze, entry=entry, exit=exit_)
```

**Pass custom parameters (size, seed, etc.):**

- width, height: maze dimensions (int)
- seed: int or None (None => random)
- perfect: bool (True => perfect maze; False => may create loops)
- algorithm: "dfs" or "prim"
- density: float (used when perfect=False)

**Access the generated structure and a solution:**

- maze.width, maze.height
- maze.cells[y][x]: int bitmask in 0..15
  (Bits: N=1, E=2, S=4, W=8; bit set => wall is CLOSED)
- maze.omitted_42 and maze.stamp42 (if present)
- path is a list of moves like ["N", "E", ...]

### Building the mazegen-* package

All packaging metadata lives in pyproject.toml at the repository root.
The subject accepts a .tar.gz, so an sdist-only build is sufficient:

```bash
python3 -m pip install --upgrade build
python3 -m build --sdist
```

The artifact will appear in dist/ as:
- mazegen-<version>.tar.gz
