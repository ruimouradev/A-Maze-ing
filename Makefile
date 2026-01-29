# ============================================================
# File: Makefile
#
# OWNER:
#   Alexandre (Person B)
#
# ROLE:
#   Developer commands: install/run/debug/lint/clean
# ============================================================

PY=python3
PIP=pip3

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install -r requirements.txt

run:
	$(PY) a_maze_ing.py config_default.txt

debug:
	$(PY) -m pdb a_maze_ing.py config_default.txt

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache build dist *.egg-info

lint:
	flake8 . --exclude mazegen.py
	mypy a_maze_ing.py renderer_ascii.py config.py serializer.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . --exclude mazegen.py
	mypy a_maze_ing.py renderer_ascii.py config.py serializer.py --strict
