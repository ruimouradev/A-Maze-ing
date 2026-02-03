"""Tests for maze serialization (reading/writing files)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mazegen import Maze  # noqa: E402
from serializer import write_output_file  # noqa: E402


class TestOutputFileFormat:
    """Test output file format compliance."""

    def test_write_basic_maze(self, sample_maze: Maze, small_config, tmp_path):
        """Test writing a basic maze to file."""
        output_file = tmp_path / "test_maze.txt"

        # Generate a path
        from mazegen import MazeGenerator
        gen = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        path = gen.solve(sample_maze, small_config.entry, small_config.exit)

        write_output_file(
            str(output_file),
            sample_maze,
            small_config.entry,
            small_config.exit,
            path,
        )

        assert output_file.exists()

    def test_output_format_structure(
        self, sample_maze: Maze, small_config, tmp_path
    ):
        """Test that output file has correct structure."""
        output_file = tmp_path / "test_maze.txt"

        from mazegen import MazeGenerator
        gen = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        path = gen.solve(sample_maze, small_config.entry, small_config.exit)

        write_output_file(
            str(output_file),
            sample_maze,
            small_config.entry,
            small_config.exit,
            path,
        )

        lines = output_file.read_text().strip().split('\n')

        # Should have: height lines + blank + entry + exit + path
        assert len(lines) >= small_config.height + 4

        # First lines should be hex grid
        for i in range(small_config.height):
            line = lines[i]
            assert len(line) == small_config.width
            assert all(c in '0123456789ABCDEF' for c in line)

        # Blank line after grid
        assert lines[small_config.height] == ''

        # Entry line
        entry_line = lines[small_config.height + 1]
        assert ',' in entry_line
        ex, ey = entry_line.split(',')
        assert int(ex) == small_config.entry[0]
        assert int(ey) == small_config.entry[1]

        # Exit line
        exit_line = lines[small_config.height + 2]
        assert ',' in exit_line
        exx, exy = exit_line.split(',')
        assert int(exx) == small_config.exit[0]
        assert int(exy) == small_config.exit[1]

        # Path line
        path_line = lines[small_config.height + 3]
        assert all(c in 'NESW' for c in path_line)

    def test_hex_encoding_correct(
        self, sample_maze: Maze, small_config, tmp_path
    ):
        """Test that cells are encoded as uppercase hex."""
        output_file = tmp_path / "test_maze.txt"

        from mazegen import MazeGenerator
        gen = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        path = gen.solve(sample_maze, small_config.entry, small_config.exit)

        write_output_file(
            str(output_file),
            sample_maze,
            small_config.entry,
            small_config.exit,
            path,
        )

        lines = output_file.read_text().strip().split('\n')

        # Verify each cell matches the maze
        for y in range(small_config.height):
            line = lines[y]
            for x in range(small_config.width):
                hex_char = line[x]
                expected_value = sample_maze.cells[y][x]
                actual_value = int(hex_char, 16)
                assert actual_value == expected_value, (
                    f"Cell ({x},{y}): expected {expected_value}, "
                    f"got {actual_value}"
                )

    def test_path_format(self, sample_maze: Maze, small_config, tmp_path):
        """Test that path is written as direction string."""
        output_file = tmp_path / "test_maze.txt"

        from mazegen import MazeGenerator
        gen = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        path = gen.solve(sample_maze, small_config.entry, small_config.exit)

        write_output_file(
            str(output_file),
            sample_maze,
            small_config.entry,
            small_config.exit,
            path,
        )

        lines = output_file.read_text().strip().split('\n')
        path_line = lines[small_config.height + 3]

        # Path should match input
        assert path_line == ''.join(path)


class TestOutputValidation:
    """Test using the provided output_validator.py."""

    def test_output_passes_validator(
        self, sample_maze: Maze, small_config, tmp_path
    ):
        """Test that generated output passes the official validator."""
        output_file = tmp_path / "test_maze.txt"

        from mazegen import MazeGenerator
        gen = MazeGenerator(
            small_config.width,
            small_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )
        path = gen.solve(sample_maze, small_config.entry, small_config.exit)

        write_output_file(
            str(output_file),
            sample_maze,
            small_config.entry,
            small_config.exit,
            path,
        )

        # Run the validator
        validator_path = Path(__file__).parent / "output_validator.py"

        result = subprocess.run(
            [sys.executable, str(validator_path), str(output_file)],
            capture_output=True,
            text=True,
        )

        # Validator prints errors if found, otherwise silent
        assert "Wrong encoding" not in result.stdout, (
            f"Validator found errors: {result.stdout}"
        )


class TestWallConsistency:
    """Test that neighboring cells have consistent wall encoding."""

    def test_north_south_walls_consistent(self, sample_maze: Maze):
        """Test that North-South walls are consistent between neighbors."""
        for y in range(sample_maze.height - 1):
            for x in range(sample_maze.width):
                current_cell = sample_maze.cells[y][x]
                south_neighbor = sample_maze.cells[y + 1][x]

                # Current cell's South wall should match
                # neighbor's North wall
                current_south = (current_cell >> 2) & 1
                neighbor_north = south_neighbor & 1

                assert current_south == neighbor_north, (
                    f"Wall mismatch at ({x},{y}): "
                    f"current South={current_south}, "
                    f"neighbor North={neighbor_north}"
                )

    def test_east_west_walls_consistent(self, sample_maze: Maze):
        """Test that East-West walls are consistent between neighbors."""
        for y in range(sample_maze.height):
            for x in range(sample_maze.width - 1):
                current_cell = sample_maze.cells[y][x]
                east_neighbor = sample_maze.cells[y][x + 1]

                # Current cell's East wall should match
                # neighbor's West wall
                current_east = (current_cell >> 1) & 1
                neighbor_west = (east_neighbor >> 3) & 1

                assert current_east == neighbor_west, (
                    f"Wall mismatch at ({x},{y}): "
                    f"current East={current_east}, "
                    f"neighbor West={neighbor_west}"
                )


class TestEdgeCases:
    """Test edge cases in serialization."""

    def test_empty_path(self, sample_maze: Maze, small_config, tmp_path):
        """Test writing maze with empty path."""
        output_file = tmp_path / "test_maze.txt"

        write_output_file(
            str(output_file),
            sample_maze,
            small_config.entry,
            small_config.exit,
            [],  # Empty path
        )

        lines = output_file.read_text().strip().split('\n')
        # Empty path should result in empty last line or just the exit
        # The file structure is: grid rows + blank line + entry + exit + path
        if len(lines) > small_config.height + 3:
            path_line = lines[small_config.height + 3]
            assert path_line == ""

    def test_long_path(self, medium_config, tmp_path):
        """Test writing maze with long path."""
        from mazegen import MazeGenerator

        gen = MazeGenerator(
            medium_config.width,
            medium_config.height,
            seed=42,
            perfect=True,
            algorithm="dfs",
        )

        maze = gen.generate(medium_config.entry, medium_config.exit)
        path = gen.solve(maze, medium_config.entry, medium_config.exit)

        output_file = tmp_path / "test_maze.txt"
        write_output_file(
            str(output_file),
            maze,
            medium_config.entry,
            medium_config.exit,
            path,
        )

        lines = output_file.read_text().strip().split('\n')
        path_line = lines[medium_config.height + 3]

        # Path should be continuous
        assert len(path_line) == len(path)
        assert all(c in 'NESW' for c in path_line)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
