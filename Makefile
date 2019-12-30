.phony: setup format typecheck

setup:
	python3.7 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements-dev.txt

format:
	venv/bin/black main.py src/*.py

typecheck:
	venv/bin/mypy --ignore-missing-imports main.py  src/*.py
