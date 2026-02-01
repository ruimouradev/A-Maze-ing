#!/usr/bin/env python3
"""
Simple test runner script that can run without pytest installed.
For full test functionality, install pytest: pip install pytest pytest-cov

This script runs basic sanity checks on the maze generator.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mazegen import MazeGenerator, Maze
from config import load_config
from serializer import write_output_file
import tempfile


def test_maze_generation():
    """Test basic maze generation."""
    print("Testing maze generation...")
    
    gen = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")
    maze = gen.generate((0, 0), (4, 4))
    
    assert maze.width == 5
    assert maze.height == 5
    assert len(maze.cells) == 5
    assert all(len(row) == 5 for row in maze.cells)
    print("✓ Maze structure is correct")
    
    # Check all cells have valid bitmasks
    for row in maze.cells:
        for cell in row:
            assert 0 <= cell <= 15
    print("✓ All cells have valid bitmasks (0-15)")


def test_deterministic_generation():
    """Test that same seed produces same maze."""
    print("\nTesting deterministic generation...")
    
    gen1 = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")
    gen2 = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")
    
    maze1 = gen1.generate((0, 0), (4, 4))
    maze2 = gen2.generate((0, 0), (4, 4))
    
    assert maze1.cells == maze2.cells
    print("✓ Same seed produces same maze")


def test_solving():
    """Test maze solving."""
    print("\nTesting maze solving...")
    
    gen = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")
    maze = gen.generate((0, 0), (4, 4))
    path = gen.solve(maze, (0, 0), (4, 4))
    
    assert len(path) > 0
    assert all(d in ['N', 'E', 'S', 'W'] for d in path)
    print(f"✓ BFS found path of length {len(path)}")
    
    # Verify path reaches exit
    x, y = 0, 0
    for direction in path:
        if direction == 'N':
            y -= 1
        elif direction == 'S':
            y += 1
        elif direction == 'E':
            x += 1
        elif direction == 'W':
            x -= 1
    
    assert (x, y) == (4, 4)
    print("✓ Path reaches exit")


def test_serialization():
    """Test file serialization."""
    print("\nTesting file serialization...")
    
    gen = MazeGenerator(5, 5, seed=42, perfect=True, algorithm="dfs")
    maze = gen.generate((0, 0), (4, 4))
    path = gen.solve(maze, (0, 0), (4, 4))
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_file = f.name
    
    try:
        write_output_file(output_file, maze, (0, 0), (4, 4), path)
        
        with open(output_file, 'r') as f:
            lines = f.read().strip().split('\n')
        
        # Check structure
        assert len(lines) >= 9  # 5 rows + blank + entry + exit + path
        
        # Check hex grid
        for i in range(5):
            assert len(lines[i]) == 5
            assert all(c in '0123456789ABCDEF' for c in lines[i])
        
        print("✓ Output file format is correct")
    finally:
        Path(output_file).unlink(missing_ok=True)


def test_config_parsing():
    """Test configuration parsing."""
    print("\nTesting configuration parsing...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("WIDTH=10\n")
        f.write("HEIGHT=8\n")
        f.write("ENTRY=0,0\n")
        f.write("EXIT=9,7\n")
        f.write("OUTPUT_FILE=maze.txt\n")
        f.write("PERFECT=True\n")
        config_file = f.name
    
    try:
        cfg = load_config(config_file)
        
        assert cfg.width == 10
        assert cfg.height == 8
        assert cfg.entry == (0, 0)
        assert cfg.exit == (9, 7)
        assert cfg.perfect is True
        
        print("✓ Configuration parsing works")
    finally:
        Path(config_file).unlink(missing_ok=True)


def test_algorithms():
    """Test different generation algorithms."""
    print("\nTesting different algorithms...")
    
    for algo in ["dfs", "prim"]:
        gen = MazeGenerator(5, 5, seed=42, perfect=True, algorithm=algo)
        maze = gen.generate((0, 0), (4, 4))
        path = gen.solve(maze, (0, 0), (4, 4))
        
        assert maze.width == 5
        assert maze.height == 5
        assert len(path) > 0
        
        print(f"✓ {algo.upper()} algorithm works")


def test_output_validator():
    """Test with official output validator."""
    print("\nTesting with official validator...")
    
    gen = MazeGenerator(8, 8, seed=42, perfect=True, algorithm="dfs")
    maze = gen.generate((0, 0), (7, 7))
    path = gen.solve(maze, (0, 0), (7, 7))
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_file = f.name
    
    try:
        write_output_file(output_file, maze, (0, 0), (7, 7), path)
        
        # Run validator
        import subprocess
        validator_path = Path(__file__).parent / "output_validator.py"
        
        result = subprocess.run(
            [sys.executable, str(validator_path), output_file],
            capture_output=True,
            text=True
        )
        
        if "Wrong encoding" in result.stdout:
            print(f"✗ Validator found errors: {result.stdout}")
            return False
        else:
            print("✓ Output passes official validator")
            return True
            
    finally:
        Path(output_file).unlink(missing_ok=True)


def main():
    """Run all tests."""
    print("=" * 60)
    print("A-Maze-ing Basic Test Suite")
    print("=" * 60)
    
    tests = [
        test_maze_generation,
        test_deterministic_generation,
        test_solving,
        test_serialization,
        test_config_parsing,
        test_algorithms,
        test_output_validator,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All tests passed!")
        print("\nFor comprehensive testing, install pytest:")
        print("  pip install pytest pytest-cov")
        print("  pytest tests/ -v")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
