"""Configuration for pytest.

Fixtures:
    cli: run the CLI with the given arguments, returns (exit code, stdout, stderr).
    snapshot: compare an output to ``tests/snapshots/<name>.txt``. Set the
        ``UPDATE_SNAPSHOTS`` environment variable to rewrite the files instead,
        then review the drift with ``git diff tests/snapshots``.

The ``baseline`` marker flags tests whose snapshots embed live source data (card
rulings, translations, TWDA-derived listings and rankings). Such a test drifts
whenever krcg is bumped, so a failure is downgraded to an amber ``xfail``
("eyeball it") instead of a hard failure. Genuine code regressions live in
unmarked tests and fail red.
"""

from collections.abc import Callable
import os
import pathlib

import pytest

from krcg_cli.parser import execute

# argparse (3.14+) colors its output when FORCE_COLOR is set in the environment
os.environ["PYTHON_COLORS"] = "0"

SNAPSHOTS = pathlib.Path(__file__).parent / "snapshots"


@pytest.fixture
def cli(capsys) -> Callable[..., tuple[int, str, str]]:
    """Run the CLI, returning (exit code, stdout, stderr)."""

    def run(*args: str) -> tuple[int, str, str]:
        """Run the CLI with the given arguments."""
        code = execute(list(args))
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return run


@pytest.fixture
def snapshot() -> Callable[[str, str], None]:
    """Compare an output to a snapshot file, or update it."""

    def check(name: str, output: str) -> None:
        """Compare the output to `tests/snapshots/<name>.txt`."""
        path = SNAPSHOTS / f"{name}.txt"
        if os.getenv("UPDATE_SNAPSHOTS"):
            path.write_text(output)
        else:
            assert output == path.read_text(), f"output differs from {path}"

    return check


def pytest_configure(config: pytest.Config) -> None:
    """Register the baseline marker."""
    config.addinivalue_line(
        "markers",
        "baseline: tracks live source data; a failure is amber (data drift), not red.",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Downgrade a baseline failure to an amber xfail."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    if item.get_closest_marker("baseline"):
        report.outcome = "skipped"
        report.wasxfail = "baseline data drift — source data changed, eyeball it"
