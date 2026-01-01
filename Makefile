VENV := .venv
ifeq ($(OS),Windows_NT)
    PYTHON := $(VENV)/Scripts/python
    MKDOCS := $(VENV)/Scripts/mkdocs
else
    PYTHON := $(VENV)/bin/python
    MKDOCS := $(VENV)/bin/mkdocs
endif

.PHONY: help setup serve clean add

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  setup   Create venv and run setup.py (only if venv is missing)"
	@echo "  add     Helper script for adding themes"
	@echo "  serve   Run mkdocs serve (auto-runs setup if needed)"
	@echo "  clean   Remove the virtual environment"

setup:
	@echo "Invoking setup script..."
	python3 ./setup.py || python ./setup.py

add:
	@echo "Invoking add theme script..."
	python3 ./add_theme.py || python ./add_theme.py

serve:
	@if [ ! -d "$(VENV)" ]; then $(MAKE) setup; fi
	$(MKDOCS) serve

clean:
	rm -rf $(VENV)
