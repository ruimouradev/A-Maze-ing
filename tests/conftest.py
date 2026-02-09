"""Pytest configuration and shared fixtures for A-Maze-ing tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add parent directory to path so tests can import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config  # noqa: E402
from mazegen import MazeGenerator, Maze  # noqa: E402


@pytest.fixture
def small_config() -> Config:
    """Create a small maze configuration for testing."""
    return Config(
        width=5,
        height=5,
        entry=(0, 0),
        exit=(4, 4),
        output_file="test_output.txt",
        perfect=True,
        seed=42,
        algorithm="dfs",
    )


@pytest.fixture
def medium_config() -> Config:
    """Create a medium maze configuration for testing."""
    return Config(
        width=10,
        height=10,
        entry=(0, 0),
        exit=(9, 9),
        output_file="test_output.txt",
        perfect=True,
        seed=123,
        algorithm="dfs",
    )


@pytest.fixture
def large_config() -> Config:
    """Create a large maze configuration for testing (stamp-safe: ≥11x9)."""
    return Config(
        width=20,
        height=20,
        entry=(0, 0),
        exit=(19, 19),
        output_file="test_output.txt",
        perfect=True,
        seed=456,
        algorithm="dfs",
    )


@pytest.fixture
def dfs_generator(small_config: Config) -> MazeGenerator:
    """Create a DFS maze generator."""
    return MazeGenerator(
        width=small_config.width,
        height=small_config.height,
        seed=small_config.seed,
        perfect=small_config.perfect,
        algorithm="dfs",
    )


@pytest.fixture
def prim_generator(small_config: Config) -> MazeGenerator:
    """Create a Prim maze generator."""
    return MazeGenerator(
        width=small_config.width,
        height=small_config.height,
        seed=small_config.seed,
        perfect=small_config.perfect,
        algorithm="prim",
    )


@pytest.fixture
def sample_maze(dfs_generator: MazeGenerator, small_config: Config) -> Maze:
    """Generate a sample maze for testing."""
    return dfs_generator.generate(small_config.entry, small_config.exit)
