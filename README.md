*This project has been created as part of the 42 curriculum by acaldeir, rusilva-*

# A-Maze-ing: Procedural Maze Generation and Solving

## Description
**A-Maze-ing** is a maze generation and solving system developed as part of the
42 curriculum. The project focuses on procedural maze generation, constraint
enforcement (including the mandatory "42 stamp"), shortest-path solving, and
interactive ASCII visualization.

### Goals
- Generate mazes using procedural algorithms
- Solve mazes using shortest-path algorithms
- Enforce constraints (borders, connectivity, 42 stamp)
- Provide an interactive ASCII visualization

---

## Instructions

### Installation

```bash
# Install dependencies
make install

# Verify installation (run the test suite)
python3 -m pytest tests/ -q
```

### Execution

```bash
# Run the maze generator and solver with interactive visualization
make run

# Run with a specific configuration file
python3 a_maze_ing.py config.txt

# Run tests
python3 -m pytest tests/ -v

# Run tests with coverage
python3 -m pytest tests/ --cov=. --cov-report=html

# Run linting checks (mypy + flake8)
make lint
```

### Configuration File Format

The maze is configured via a KEY=VALUE text file with the following structure:

```
# Mandatory fields (required for all mazes)
WIDTH=20                    # Maze width in cells (must be > 0)
HEIGHT=15                   # Maze height in cells (must be > 0)
ENTRY=0,0                   # Entry point coordinates (x,y)
EXIT=19,14                  # Exit point coordinates (x,y)
OUTPUT_FILE=maze.txt        # Output file path for hexadecimal maze
PERFECT=True                # True for perfect maze (no loops), False for imperfect

# Bonus fields (optional, have sensible defaults)
SEED=42                     # Random seed (default: 42; use empty/None to disable)
ALGORITHM=dfs               # Generation algorithm: dfs|prim
DISPLAY=ascii               # Display mode: ascii
ANIMATE=False               # Legacy toggle (applies to both solver & generator)
ANIMATE_SOLVER=False        # Animate solver (BFS) steps
ANIMATE_GENERATION=False    # Animate generation steps
STEP_DELAY_MS=25            # Milliseconds per animation frame (>= 0)
DENSITY=0.06                # Imperfect maze density [0.0-1.0]

# Comments are supported (lines starting with #)
# Empty lines are ignored
```

**Example Configuration:**
```
WIDTH=25
HEIGHT=20
ENTRY=0,0
EXIT=24,19
OUTPUT_FILE=my_maze.txt
PERFECT=True
SEED=123
ALGORITHM=prim
ANIMATE_SOLVER=True
ANIMATE_GENERATION=True
STEP_DELAY_MS=50
```

### Interactive Commands

Once the maze is displayed, the following commands are available:

| Command | Action |
|---------|--------|
| `r` | Regenerate maze (applies current algorithm and animation settings) |
| `p` | Toggle solution path display |
| `c` | Cycle through wall colors (5 color options) |
| `a` | Toggle solver animation (BFS pathfinding with step-by-step visualization) |
| `A` | Toggle maze generation animation (step-by-step generation display) |
| `g` | Toggle between DFS and Prim generation algorithms |
| `q` | Quit the program |

---

## Maze Generation Algorithms

### Chosen Algorithm: DFS (Depth-First Search) with Constraint Enforcement

**Primary Algorithm:** Randomized Depth-First Search (DFS)  
**Secondary Algorithm:** Prim's Algorithm (available via toggle)

### Why DFS?

DFS was chosen as the primary algorithm for several reasons:

1. **Simplicity & Performance**: DFS is intuitive to implement and runs efficiently O(n) where n is the number of cells
2. **Perfect Maze Generation**: Guarantees a perfect maze (no loops, all cells connected) by default
3. **Deterministic with Seeding**: Easy to produce reproducible mazes using random seeds
4. **Constraint Integration**: Cleanly integrates with post-generation constraint enforcement (42 stamp, border walls)
5. **Visualization**: Works well with step-by-step animation for educational purposes

### Alternative: Prim's Algorithm

Prim's algorithm is included as a runtime toggle option:
- **Pros**: Different visual characteristics, interesting alternative perspective
- **Cons**: Slightly higher memory overhead due to frontier tracking

### Constraint Enforcement

After generation, mazes are validated and enhanced with:

- **Border Enforcement**: All perimeter cells have appropriate walls
- **42 Stamp**: For mazes ≥ 11×9, a decorative "42" pattern is embedded using three size-aware variations:
  - Small: 7×5 pattern (for mazes 11×9 to <28×20)
  - Medium: 8×6 pattern (for mazes 28×20 to <45×30)
  - Large: 11×7 pattern (for very large mazes ≥45×30)
- **No 3×3 Open Areas**: Constraint preventing open rectangular spaces larger than 2×2
- **Entry/Exit Validation**: Entry and exit points are outside all constraint zones

---

## Solving Algorithms

The system uses BFS (Breadth-First Search) for pathfinding:

### BFS (Breadth-First Search)
- Guaranteed shortest path
- Explores level-by-level
- Default solver for visualization
- Animatable with step-by-step frontier visualization

---

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

### Core Modules

#### 1. **mazegen.py** - Maze Generation Engine
**Highly Reusable**: Multi-algorithm support with pluggable architecture

```python
gen = MazeGenerator(width=20, height=20, seed=42, perfect=True, algorithm="dfs")
maze = gen.generate(entry=(0,0), exit=(19,19))
path = gen.solve(maze, entry=(0,0), exit=(19,19))
```

**Reusable Components:**
- Algorithm switching: `gen.set_algorithm("prim")` → regenerate with different algorithm
- Step-by-step generation: `gen.iter_generation_steps(entry, exit)` → yields intermediate mazes for animation
- Step-by-step solving: `gen.solve_bfs_steps()` → yields solver frontier for visualization
- Constraint validation: Built-in 42 stamp, border, and connectivity checks

**Future Extensibility:**
```python
# Easy to add new algorithms:
# 1. Implement generation logic in _generate_<algorithm>()
# 2. Add algorithm name to self.algorithm validation
# 3. Call gen.set_algorithm("<new_algo>") to switch at runtime
```

#### 2. **config.py** - Configuration Parser
**Reusable**: Generic KEY=VALUE parser with type validation

```python
cfg = load_config("config.txt")
# cfg.width, cfg.height, cfg.entry, cfg.exit, cfg.algorithm, etc.
```

**Reusable Components:**
- Parser helper functions: `_parse_int()`, `_parse_bool()`, `_parse_coord()`, `_parse_density()`
- Validation logic easily adapted for other 42 projects using configuration files
- Type conversion with clear error messages

#### 3. **serializer.py** - Maze Encoding/Output
**Reusable**: Hexadecimal maze format with validation

```python
write_output_file("maze.txt", maze, entry, exit, path)
# Produces 42-compatible hexadecimal maze format
```

**Reusable Components:**
- Maze-to-hex encoding (4-bit wall bitmask per cell)
- Path encoding as direction strings (N/S/E/W)
- Output validator for format verification

#### 4. **renderer_ascii.py** - Terminal Visualization
**Reusable**: Modular animation system with color support

```python
renderer = AsciiRenderer()
renderer.run(maze, path, gen, cfg)
```

**Reusable Components:**
- `_draw_maze()`: Renders maze with walls, entry, exit, path, visited/frontier visualization
- Animation speed control: `self.animation_speed` (adjustable)
- Color cycling system: 5 configurable ANSI colors
- Solver animation with visited/frontier tracking
- Generation animation with step-by-step rendering

---

## Team & Project Management

### Team Structure

| Member | Login | Role | Responsibilities |
|--------|-------|------|------------------|
| Alex | acaldeir | **Configuration, Serialization & Visualization** | Config parsing, validation, file I/O, output encoding, ASCII renderer, integration & testing |
| Rui | rusilva- | **Maze Engine & Solving** | Algorithm implementation, constraint enforcement, pathfinding, integration & testing |

### Project Evolution

#### Initial Planning
- **Phase 1**: Core DFS algorithm with perfect maze generation
- **Phase 2**: Constraint enforcement (borders, entry/exit validation)
- **Phase 3**: Configuration system and I/O
- **Phase 4**: ASCII visualization and interaction
- **Phase 5**: Bonus features (animation, multiple algorithms)

#### What Actually Happened
1. **Phase 1-2**: Completed on schedule with clean algorithm implementation
2. **Phase 3**: Config parser required iteration on boolean parsing and tuple handling; added testing for edge cases
3. **Phase 4**: ASCII renderer evolved significantly—added multi-color support, junction rendering, and animation infrastructure
4. **Phase 5**: Algorithm switching and animation completed; step-by-step solvers added for visualization
5. **Integration Phase**: mazegen implementation pulled in; required type annotation, docstring fixes and API verification

### What Worked Well

✅ **Modular Architecture**: Clean separation of concerns (generation, solving, rendering, config)
✅ **Test Suite**: Comprehensive 52 test coverage including edge cases and constraint validation
✅ **Algorithm Extensibility**: Easy to add new algorithms without modifying core logic
✅ **Animation System**: Flexible step-by-step generation/solving enables educational visualization
✅ **Type Safety**: Strict mypy checking caught potential bugs early
✅ **Interactive Design**: Real-time algorithm and visualization control enhances user experience

### What Could Be Improved

⚠️ **Configuration Validation**: Could add schema validation framework (e.g., Pydantic) for more robust parsing
⚠️ **Performance**: Large mazes (>100×100) could benefit from parallel constraint checking
⚠️ **Display Formats**: Only ASCII currently supported; JSON/image export would be valuable
⚠️ **Documentation**: Algorithm complexity analysis and performance benchmarks would help users choose between DFS/Prim
⚠️ **GUI Alternative**: Terminal UI is functional but a graphical interface would improve accessibility

### Tools & Technologies Used

| Tool | Purpose | Usage |
|------|---------|-------|
| **pytest** | Unit testing framework | 52 comprehensive tests with fixtures |
| **pytest-cov** | Code coverage analysis | Coverage reporting and metrics |
| **mypy** | Static type checking | Strict mode type safety verification |
| **flake8** | Code style linting | PEP 8 compliance (79-char lines) |
| **git** | Version control | Branch management, PR reviews |
| **Make** | Build automation | `make install`, `make run`, `make test`, `make lint` |
| **Dataclasses** | Immutable config objects | Frozen `Config` for type-safe configuration |
| **ANSI Colors** | Terminal rendering | 5-color palette for wall visualization |
| **Monkeypatch** | Test I/O mocking | Simulated user input for automated tests |

---

## Advanced Features

### 1. Multiple Generation Algorithms
- **DFS (Default)**: Fast, intuitive, good visualization
- **Prim**: Alternative algorithm accessible via `g` command
- **Runtime Switching**: Change algorithms mid-execution without program restart

### 2. Animation System
- **Generation Animation**: Watch maze cells carve out step-by-step with `A` toggle
- **Solver Animation**: See pathfinding frontier expand in real-time with `a` toggle
- **Configurable Speed**: Adjust `STEP_DELAY_MS` in config (default: 25ms per frame)

### 3. Dynamic Color Cycling
- **5 Wall Colors**: Cycle through default, yellow, blue, cyan, and magenta with `c` command
- **Semantic Coloring**: Entry (green), exit (red), path (bright cyan), stamp (bright yellow)
- **ANSI Support**: Full 256-color compatibility for enhanced terminal environments

### 4. Path Visualization
- **Solution Overlay**: Display shortest path from entry to exit
- **Toggle Visibility**: Hide/show path with `p` command
- **Direction Encoding**: Path stored as direction sequence (N/S/E/W)

### 5. Path Solving
- **BFS (Default)**: Guaranteed shortest path; good for animation
- **Step-by-Step Visualization**: Watch visited/frontier cells expand during solving

### 6. Constraint Features
- **42 Stamp Embedding**: Decorative pattern embedded in large mazes (≥11×9)
- **Perfect vs. Imperfect Mazes**: Toggle between loopless and multi-solution mazes
- **Deterministic Generation**: Use `SEED` parameter for reproducible mazes

---

## Testing

Run the comprehensive test suite:

```bash
# All tests
python3 -m pytest tests/ -v

# Specific test class
python3 -m pytest tests/test_mazegen.py::TestMazeGeneration -v

# With coverage report
python3 -m pytest tests/ --cov=. --cov-report=html
```

**Test Coverage:**
- 52 tests passing, 0 skipped
- Configuration parsing (18 tests)
- Maze generation & constraints (24 tests)  
- Pathfinding & solving (12 tests)
- Serialization & output validation (8 tests)

---

## References & Resources

### Maze Generation Algorithms
- [Maze Generation Algorithms (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-First Search Maze](https://en.wikipedia.org/wiki/Depth-first_search)
- [Prim's Algorithm](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [Red Blob Games - Maze Generation](https://www.redblobgames.com/grids/intro/)

### Pathfinding Algorithms
- [Breadth-First Search (BFS)](https://en.wikipedia.org/wiki/Breadth-first_search)

### Technical Documentation
- [Python Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [pytest Documentation](https://docs.pytest.org/)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)

### Code Style & Quality
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [mypy Static Type Checker](https://www.mypy-lang.org/)
- [flake8 Linter](https://flake8.pycqa.org/)

### AI Usage

**AI** was used for the following tasks and components:

   - Documentation and README structuring
   - Code style and readability improvements (e.g. PEP 8 compliance)
   - Reviewing type annotations and static analysis feedback
   - Suggesting testing strategies and edge-case coverage.
   - Gaining a deeper understanding of concepts and examples.

All core project logic — maze generation algorithms, constraint enforcement
(including the 42 stamp), pathfinding, rendering logic, and overall architecture —
was designed, implemented, and validated by the team.
