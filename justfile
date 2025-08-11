# Use bash with strict modes for better error handling
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Default recipe - show available commands
default:
    @just --list

# Run linters and format checks
quality:
    @echo "🔍 Running quality checks..."
    uv run ruff check
    uv run ruff format --check
    uv run mypy krcg_cli
    @echo "✅ Quality checks passed!"

# Run tests (includes quality checks)
test: quality
    @echo "🧪 Running tests..."
    uv run pytest -vvs
    @echo "✅ Tests passed!"

# Upgrade all dependencies (including dev dependencies)
update:
    @echo "📦 Updating dependencies..."
    uv sync --upgrade --dev --no-cache
    @echo "✅ Dependencies updated!"

# Clean build and cache artifacts
# Clean build and cache artifacts
clean-build:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf dist
    @echo "✅ Cleaned!"

clean: clean-build
    @echo "🧹 Cleaning cache..."
    rm -rf .pytest_cache .mypy_cache .ruff_cache
    @echo "✅ Cleaned!"

# Ensure we're on master branch and working tree is clean
check:
    @echo "🔍 Checking release prerequisites..."
    @if [[ "$(git branch --show-current)" != "master" ]]; then echo "❌ Not on master branch"; exit 1; fi
    @if [[ -n "$(git status --porcelain)" ]]; then echo "❌ Working directory is dirty"; exit 1; fi
    @echo "✅ Release checks passed!"

# Build the package
build:
    @echo "🔨 Building package..."
    uv build
    @echo "✅ Package built!"

# Bump the version (levle: minor | major)
bump level="minor": check
    #!/usr/bin/env bash
    set -euo pipefail
    uv version --bump "{{ level }}"
    VERSION="$(uv version --short)"
    echo "📝 Committing version ${VERSION}..."
    git add pyproject.toml
    git commit -m "Release ${VERSION}" && git tag "v${VERSION}"
    echo "📤 Pushing to remote..."
    git push origin master --tags

# Publish package to PyPI
publish:
    @echo "📦 Publishing to PyPI..."
    @UV_PUBLISH_TOKEN="$(tr -d '\n' < .pypi_token)" uv publish
    @echo "✅ Release completed!"

# Tag a new version, build it and publish it to PyPI
release: clean-build check test
    @just bump minor
    @just build
    @just publish
