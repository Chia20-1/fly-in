PYTHON = .venv/bin/python
MAP ?= maps/easy/01_linear_path.txt

venv:
	python3 -m venv .venv

install: venv
	$(PYTHON) -m pip install pygame pydantic mypy flake8

run:
	@PYGAME_HIDE_SUPPORT_PROMPT=1 $(PYTHON) main.py "$(MAP)"

debug:
	$(PYTHON) -m pdb main.py "$(MAP)"

clean:
	rm -rf .mypy_cache __pycache__

fclean: clean
	rm -rf .venv

lint:
	$(PYTHON) -m flake8 . --exclude=.venv
	$(PYTHON) -m mypy . \
		--exclude '(^|/)\.venv/' \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 . --exclude=.venv
	$(PYTHON) -m mypy . --exclude '(^|/)\.venv/' --strict

.PHONY: venv install run debug clean lint lint-strict