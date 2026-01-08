# Use 'uv run' to automatically handle the environment and pathing
RUN := uv run
PYTHON := $(RUN) python
MKDOCS := $(RUN) mkdocs
REQ_FILE := requirements.txt

.PHONY: help sync serve clean add update requirements

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  sync          Install dependencies using uv"
	@echo "  add           Helper script for adding themes"
	@echo "  serve         Run mkdocs serve"
	@echo "  update        Update dependencies using uv"
	@echo "  clean         Remove the virtual environment"
	@echo "  requirements  Updates requirements.txt"

sync:
	@echo "Syncing dependencies..."
	uv sync
	$(MAKE) requirements

add:
	@echo "Invoking add theme script..."
	$(PYTHON) ./add_theme.py

serve:
	$(MKDOCS) serve

update:
	@echo "Updating dependencies..."
	uv lock --upgrade
	uv sync
	$(MAKE) requirements

requirements:
	@echo "Generating $(REQ_FILE) from uv.lock..."
	@uv export --format requirements-txt --no-dev --output-file $(REQ_FILE)
	@echo "Generating dependency tree..."
	@uv tree > tree.txt

clean:
	rm -rf .venv
