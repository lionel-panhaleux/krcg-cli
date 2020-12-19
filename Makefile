.PHONY: quality test release update clean

quality:
	black --check krcg tests
	flake8

test: quality
	pytest -vvs

release:
	fullrelease
	pip install -e ".[dev]"

update:
	pip install --upgrade --upgrade-strategy eager -e .[dev]

clean:
	rm -f `python -c "import tempfile as t; print(t.gettempdir())"`/krcg-vtes.pyc
	rm -f `python -c "import tempfile as t; print(t.gettempdir())"`/krcg-twda.pyc
	rm -rf dist
	rm -rf .pytest_cache
