clean:
	rm -f `python -c "import tempfile as t; print(t.gettempdir())"`/krcg-vtes.pyc
	rm -f `python -c "import tempfile as t; print(t.gettempdir())"`/krcg-twda.pyc
	rm -rf .pytest_cache
