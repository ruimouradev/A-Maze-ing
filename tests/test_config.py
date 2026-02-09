"""Tests for configuration file parsing."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config  # noqa: E402


class TestConfigParsing:
    """Test configuration file parsing."""

    def test_parse_minimal_config(self, tmp_path, monkeypatch):
        """Test parsing config with only mandatory fields."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=20\n"
            "HEIGHT=20\n"
            "ENTRY=0,0\n"
            "EXIT=19,19\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        # Mock user input for 42 stamp prompt (answer 'y' to continue)
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        cfg = load_config(str(config_file))

        assert cfg.width == 20
        assert cfg.height == 20
        assert cfg.entry == (0, 0)
        assert cfg.exit == (19, 19)
        assert cfg.output_file == "maze.txt"
        assert cfg.perfect is True

    def test_parse_full_config(self, tmp_path):
        """Test parsing config with all fields including bonus."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=15\n"
            "HEIGHT=12\n"
            "ENTRY=0,0\n"
            "EXIT=14,11\n"
            "OUTPUT_FILE=output.txt\n"
            "PERFECT=False\n"
            "SEED=12345\n"
            "ALGORITHM=prim\n"
            "DISPLAY=ascii\n"
            "ANIMATE=True\n"
            "STEP_DELAY_MS=50\n"
        )

        cfg = load_config(str(config_file))

        assert cfg.width == 15
        assert cfg.height == 12
        assert cfg.entry == (0, 0)
        assert cfg.exit == (14, 11)
        assert cfg.output_file == "output.txt"
        assert cfg.perfect is False
        assert cfg.seed == 12345
        assert cfg.algorithm == "prim"
        assert cfg.display == "ascii"
        assert cfg.animate is True
        assert cfg.step_delay_ms == 50

    def test_parse_with_comments(self, tmp_path, monkeypatch):
        """Test that comments are ignored."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "# This is a comment\n"
            "WIDTH=20\n"
            "# Another comment\n"
            "HEIGHT=20\n"
            "ENTRY=0,0  # inline comment\n"
            "EXIT=19,19\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        cfg = load_config(str(config_file))

        assert cfg.width == 20
        assert cfg.height == 20

    def test_parse_with_empty_lines(self, tmp_path, monkeypatch):
        """Test that empty lines are ignored."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=20\n"
            "\n"
            "HEIGHT=20\n"
            "\n"
            "\n"
            "ENTRY=0,0\n"
            "EXIT=19,19\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        cfg = load_config(str(config_file))

        assert cfg.width == 20
        assert cfg.height == 20

    def test_parse_boolean_true_variations(self, tmp_path, monkeypatch):
        """Test different ways to specify True boolean."""
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        for true_value in ["True", "true", "TRUE", "1", "yes", "Yes"]:
            config_file = tmp_path / "config.txt"
            config_file.write_text(
                f"WIDTH=10\n"
                f"HEIGHT=8\n"
                f"ENTRY=0,0\n"
                f"EXIT=9,7\n"
                f"OUTPUT_FILE=maze.txt\n"
                f"PERFECT={true_value}\n"
            )

            cfg = load_config(str(config_file))
            assert cfg.perfect is True, f"Failed for value: {true_value}"

    def test_parse_boolean_false_variations(self, tmp_path, monkeypatch):
        """Test different ways to specify False boolean."""
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        for false_value in ["False", "false", "FALSE", "0", "no", "No"]:
            config_file = tmp_path / "config.txt"
            config_file.write_text(
                f"WIDTH=10\n"
                f"HEIGHT=8\n"
                f"ENTRY=0,0\n"
                f"EXIT=9,7\n"
                f"OUTPUT_FILE=maze.txt\n"
                f"PERFECT={false_value}\n"
            )

            cfg = load_config(str(config_file))
            assert cfg.perfect is False, f"Failed for value: {false_value}"

    def test_parse_tuple_coordinates(self, tmp_path, monkeypatch):
        """Test parsing tuple coordinates with spaces."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=10\n"
            "HEIGHT=8\n"
            "ENTRY=0, 0\n"
            "EXIT=9 , 7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        cfg = load_config(str(config_file))

        assert cfg.entry == (0, 0)
        assert cfg.exit == (9, 7)


class TestConfigValidation:
    """Test configuration validation."""

    def test_missing_required_field(self, tmp_path):
        """Test that missing required field raises error."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=10\n"
            "HEIGHT=8\n"
            # Missing ENTRY
            "EXIT=9,7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        with pytest.raises(ValueError, match="ENTRY"):
            load_config(str(config_file))

    def test_invalid_width(self, tmp_path):
        """Test that invalid width raises error."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=-5\n"
            "HEIGHT=8\n"
            "ENTRY=0,0\n"
            "EXIT=9,7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        with pytest.raises(ValueError):
            load_config(str(config_file))

    def test_invalid_height(self, tmp_path):
        """Test that invalid height raises error."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=10\n"
            "HEIGHT=0\n"
            "ENTRY=0,0\n"
            "EXIT=9,7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        with pytest.raises(ValueError):
            load_config(str(config_file))

    def test_invalid_entry_format(self, tmp_path, monkeypatch):
        """Test that invalid entry format raises error."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=20\n"
            "HEIGHT=20\n"
            "ENTRY=invalid\n"
            "EXIT=19,19\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        with pytest.raises(ValueError):
            load_config(str(config_file))

    def test_negative_seed(self, tmp_path, monkeypatch):
        """Test that negative seed is handled (may or may not raise)."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=10\n"
            "HEIGHT=8\n"
            "ENTRY=0,0\n"
            "EXIT=9,7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
            "SEED=-42\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        # Some implementations accept negative seeds, others don't
        try:
            cfg = load_config(str(config_file))
            # If accepted, seed should be stored
            assert cfg.seed == -42
        except ValueError:
            pass  # Also acceptable to reject


class TestConfigDefaults:
    """Test configuration default values."""

    def test_default_bonus_fields(self, tmp_path, monkeypatch):
        """Test that bonus fields have correct defaults."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=10\n"
            "HEIGHT=8\n"
            "ENTRY=0,0\n"
            "EXIT=9,7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        cfg = load_config(str(config_file))

        # With small maze and 'y' input, seed is set to 42 for stamp pattern
        assert cfg.seed == 42
        assert cfg.algorithm == "dfs"
        assert cfg.display == "ascii"
        assert cfg.animate is False
        assert cfg.step_delay_ms == 25

    def test_override_defaults(self, tmp_path, monkeypatch):
        """Test that provided values override defaults."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=10\n"
            "HEIGHT=8\n"
            "ENTRY=0,0\n"
            "EXIT=9,7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
            "ALGORITHM=prim\n"
            "ANIMATE=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        cfg = load_config(str(config_file))

        assert cfg.algorithm == "prim"
        assert cfg.animate is True


class TestConfigEdgeCases:
    """Test edge cases in configuration."""

    def test_whitespace_handling(self, tmp_path, monkeypatch):
        """Test that extra whitespace is handled."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "  WIDTH  =  10  \n"
            "HEIGHT=8\n"
            "ENTRY = 0 , 0\n"
            "EXIT=9,7  \n"
            "OUTPUT_FILE =  maze.txt  \n"
            "PERFECT=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        cfg = load_config(str(config_file))

        assert cfg.width == 10
        assert cfg.entry == (0, 0)
        assert cfg.output_file == "maze.txt"

    def test_case_insensitive_keys(self, tmp_path, monkeypatch):
        """Test if keys are case-insensitive (implementation dependent)."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "width=10\n"
            "height=8\n"
            "entry=0,0\n"
            "exit=9,7\n"
            "output_file=maze.txt\n"
            "perfect=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        # This may or may not work depending on implementation
        try:
            cfg = load_config(str(config_file))
            assert cfg.width == 10
        except (ValueError, KeyError):
            pass  # Case-sensitive is also acceptable

    def test_duplicate_keys(self, tmp_path, monkeypatch):
        """Test behavior with duplicate keys (last one wins)."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=10\n"
            "WIDTH=15\n"
            "HEIGHT=8\n"
            "ENTRY=0,0\n"
            "EXIT=14,7\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        cfg = load_config(str(config_file))

        # Last value should win
        assert cfg.width == 15

    def test_very_large_dimensions(self, tmp_path):
        """Test configuration with very large maze dimensions."""
        config_file = tmp_path / "config.txt"
        config_file.write_text(
            "WIDTH=1000\n"
            "HEIGHT=1000\n"
            "ENTRY=0,0\n"
            "EXIT=999,999\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        cfg = load_config(str(config_file))

        assert cfg.width == 1000
        assert cfg.height == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
