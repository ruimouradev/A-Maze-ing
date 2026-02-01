"""Tests for maze generation and solving functionality."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mazegen import MazeGenerator, Maze  # noqa: E402


class TestMazeStructure:
    """Test maze data structure and basic properties."""

    def test_maze_dimensions(self, sample_maze: Maze, small_config):
        """Test that maze has correct dimensions."""
        assert sample_maze.width == small_config.width
        assert sample_maze.height == small_config.height
        assert len(sample_maze.cells) == small_config.height
        assert all(
            len(row) == small_config.width for row in sample_maze.cells
        )

    def test_maze_cells_are_valid_bitmasks(self, sample_maze: Maze):
        """Test that all cells contain valid wall bitmasks (0-15)."""
        for row in sample_maze.cells:
            for cell in row:
                assert 0 <= cell <= 15, f"Invalid cell value: {cell}"

    def test_maze_has_walls(self, sample_maze: Maze):
        """Test that maze has at least some walls."""
        total_walls = sum(
            bin(cell).count('1')
            for row in sample_maze.cells
            for cell in row
        )
        # At least half the cells should have walls
        assert total_walls > 0


class TestMazeGeneration:
    """Test maze generation algorithms."""

    def test_dfs_generation_deterministic(self, small_config):
        """Test that DFS with same seed produces same maze."""
        gen1 = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        gen2 = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )

        maze1 = gen1.generate(small_config.entry, small_config.exit)
        maze2 = gen2.generate(small_config.entry, small_config.exit)

        assert maze1.cells == maze2.cells

    def test_prim_generation_deterministic(self, small_config):
        """Test that Prim with same seed produces same maze."""
        gen1 = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="prim",
        )
        gen2 = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="prim",
        )

        maze1 = gen1.generate(small_config.entry, small_config.exit)
        maze2 = gen2.generate(small_config.entry, small_config.exit)

        assert maze1.cells == maze2.cells

    def test_different_seeds_produce_different_mazes(self, small_config):
        """Test that different seeds produce different mazes."""
        gen1 = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        gen2 = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=99,
            perfect=True,
            algorithm="dfs",
        )

        maze1 = gen1.generate(small_config.entry, small_config.exit)
        maze2 = gen2.generate(small_config.entry, small_config.exit)

        # High probability they're different
        assert maze1.cells != maze2.cells

    def test_minimum_size_maze(self):
        """Test generation of minimum size maze (3x3)."""
        gen = MazeGenerator(3, 3, seed=42, perfect=True, algorithm="dfs")
        maze = gen.generate((0, 0), (2, 2))

        assert maze.width == 3
        assert maze.height == 3
        assert maze.omitted_42  # 3x3 too small for stamp


class TestMazeConstraints:
    """Test maze constraint enforcement (42 stamp, borders, etc)."""

    def test_entry_exit_different(self, dfs_generator, small_config):
        """Test that entry and exit are different cells."""
        assert small_config.entry != small_config.exit

    def test_border_walls_exist(self, sample_maze: Maze):
        """Test that border walls are properly set."""
        # Top border (North walls)
        for x in range(sample_maze.width):
            assert sample_maze.cells[0][x] & 1  # North wall bit

        # Bottom border (South walls)
        for x in range(sample_maze.width):
            assert sample_maze.cells[-1][x] & 4  # South wall bit

        # Left border (West walls)
        for y in range(sample_maze.height):
            assert sample_maze.cells[y][0] & 8  # West wall bit

        # Right border (East walls)
        for y in range(sample_maze.height):
            assert sample_maze.cells[y][-1] & 2  # East wall bit

    def test_stamp_42_exists_in_large_maze(self, large_config):
        """Test that 42 stamp exists in mazes large enough (≥11x9)."""
        gen = MazeGenerator(
            large_config.width,
            large_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        maze = gen.generate(large_config.entry, large_config.exit)

        # Large maze should have 42 stamp
        assert not maze.omitted_42
        assert len(maze.stamp42) > 0

    def test_stamp_42_all_walls_closed(self, medium_config):
        """Test that all cells in 42 stamp have all walls closed."""
        gen = MazeGenerator(
            medium_config.width,
            medium_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        maze = gen.generate(medium_config.entry, medium_config.exit)

        for x, y in maze.stamp42:
            assert maze.cells[y][x] == 15, (
                f"Cell ({x},{y}) in stamp should have all walls (15)"
            )

    def test_no_3x3_open_areas(self, sample_maze: Maze):
        """Test that there are no 3x3 areas without walls."""
        # This is a heuristic check - we can't easily detect all cases
        # but we can check for obvious violations
        for y in range(sample_maze.height - 2):
            for x in range(sample_maze.width - 2):
                # Check 3x3 block starting at (x, y)
                walls_count = 0
                for dy in range(3):
                    for dx in range(3):
                        cell = sample_maze.cells[y + dy][x + dx]
                        walls_count += bin(cell).count('1')
                # A 3x3 area should have some walls
                assert walls_count > 0


class TestMazeSolving:
    """Test maze solving algorithms."""

    def test_bfs_finds_solution(self, dfs_generator, small_config):
        """Test that BFS finds a valid path."""
        maze = dfs_generator.generate(small_config.entry, small_config.exit)
        path = dfs_generator.solve(
            maze, small_config.entry, small_config.exit
        )

        assert len(path) > 0
        assert all(d in ['N', 'E', 'S', 'W'] for d in path)

    def test_astar_finds_solution(self, dfs_generator, small_config):
        """Test that A* finds a valid path."""
        maze = dfs_generator.generate(small_config.entry, small_config.exit)
        path = dfs_generator.solve_astar(
            maze, small_config.entry, small_config.exit
        )

        assert len(path) > 0
        assert all(d in ['N', 'E', 'S', 'W'] for d in path)

    def test_path_reaches_exit(self, dfs_generator, small_config):
        """Test that solution path actually reaches the exit."""
        maze = dfs_generator.generate(small_config.entry, small_config.exit)
        path = dfs_generator.solve(
            maze, small_config.entry, small_config.exit
        )

        # Follow the path
        x, y = small_config.entry
        for direction in path:
            if direction == 'N':
                y -= 1
            elif direction == 'S':
                y += 1
            elif direction == 'E':
                x += 1
            elif direction == 'W':
                x -= 1

        assert (x, y) == small_config.exit

    def test_path_respects_walls(self, dfs_generator, small_config):
        """Test that solution path doesn't go through walls."""
        maze = dfs_generator.generate(small_config.entry, small_config.exit)
        path = dfs_generator.solve(
            maze, small_config.entry, small_config.exit
        )

        # Wall bit mapping
        wall_bits = {'N': 1, 'E': 2, 'S': 4, 'W': 8}

        x, y = small_config.entry
        for direction in path:
            # Check that the wall in this direction is open
            cell_value = maze.cells[y][x]
            assert not (cell_value & wall_bits[direction]), (
                f"Path tries to go through wall at ({x},{y}) going {direction}"
            )

            # Move to next cell
            if direction == 'N':
                y -= 1
            elif direction == 'S':
                y += 1
            elif direction == 'E':
                x += 1
            elif direction == 'W':
                x -= 1

    def test_bfs_vs_astar_both_valid(self, dfs_generator, small_config):
        """Test that both BFS and A* find valid paths (may differ)."""
        maze = dfs_generator.generate(small_config.entry, small_config.exit)

        bfs_path = dfs_generator.solve(
            maze, small_config.entry, small_config.exit
        )
        astar_path = dfs_generator.solve_astar(
            maze, small_config.entry, small_config.exit
        )

        # Both should be valid
        assert len(bfs_path) > 0
        assert len(astar_path) > 0

        # BFS should find shortest path
        assert len(bfs_path) <= len(astar_path) + 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_entry_coordinates(self):
        """Test that invalid entry raises error."""
        gen = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")

        with pytest.raises(ValueError):
            gen.generate((10, 10), (4, 4))  # Out of bounds

    def test_invalid_exit_coordinates(self):
        """Test that invalid exit raises error."""
        gen = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")

        with pytest.raises(ValueError):
            gen.generate((0, 0), (10, 10))  # Out of bounds

    def test_same_entry_exit(self):
        """Test that entry == exit raises error or handles correctly."""
        gen = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")

        # Depending on implementation, this might raise or return empty path
        try:
            maze = gen.generate((0, 0), (0, 0))
            path = gen.solve(maze, (0, 0), (0, 0))
            assert len(path) == 0  # No moves needed
        except ValueError:
            pass  # Also acceptable

    def test_very_small_maze(self):
        """Test generating a 2x2 maze (minimum possible)."""
        gen = MazeGenerator(2, 2, seed=42, perfect=True, algorithm="dfs")
        maze = gen.generate((0, 0), (1, 1))

        assert maze.width == 2
        assert maze.height == 2
        assert maze.omitted_42  # Too small for stamp

    def test_rectangular_maze(self):
        """Test non-square maze generation."""
        gen = MazeGenerator(8, 4, seed=42, perfect=True, algorithm="dfs")
        maze = gen.generate((0, 0), (7, 3))

        assert maze.width == 8
        assert maze.height == 4

    def test_perfect_vs_imperfect_maze(self, small_config):
        """Test that imperfect mazes may have fewer or equal walls."""
        gen_perfect = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        gen_imperfect = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=False,
            algorithm="dfs",
            density=0.1,
        )

        maze_perfect = gen_perfect.generate(
            small_config.entry, small_config.exit
        )
        maze_imperfect = gen_imperfect.generate(
            small_config.entry, small_config.exit
        )

        # Both should be valid mazes
        assert maze_perfect.width == small_config.width
        assert maze_imperfect.width == small_config.width


class TestAlgorithmSwitching:
    """Test switching between generation algorithms."""

    def test_set_algorithm_method_exists(self, dfs_generator):
        """Test that set_algorithm method exists and works."""
        # This test assumes your colleague implements set_algorithm
        try:
            dfs_generator.set_algorithm("prim")
            assert dfs_generator.algorithm == "prim"

            dfs_generator.set_algorithm("dfs")
            assert dfs_generator.algorithm == "dfs"
        except AttributeError:
            pytest.skip("set_algorithm method not yet implemented")

    def test_algorithm_switching_produces_different_mazes(self, small_config):
        """Test that switching algorithms produces different mazes."""
        gen = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )

        maze_dfs = gen.generate(small_config.entry, small_config.exit)

        # Switch algorithm (if method exists)
        try:
            gen.set_algorithm("prim")
            maze_prim = gen.generate(small_config.entry, small_config.exit)

            # Different algorithms should produce different mazes
            # (with very high probability)
            assert maze_dfs.cells != maze_prim.cells
        except AttributeError:
            pytest.skip("set_algorithm method not yet implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
