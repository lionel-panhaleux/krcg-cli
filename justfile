set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Default recipe - show available commands
default:
    @just --list

# Run all quality checks and tests
all: quality test

# Run linters and format checks
quality:
    @echo "🔍 Running quality checks..."
    uv run ruff check
    uv run ruff format --check
    uv run ty check krcg_cli
    @echo "✅ Quality checks passed!"

# Run tests (includes quality checks)
test: quality
    @echo "🧪 Running tests..."
    uv run pytest -vvs
    @echo "✅ Tests passed!"

# Upgrade all dependencies (including dev dependencies)
update:
    @echo "📦 Updating dependencies..."
    uv sync --upgrade --group dev
    @echo "✅ Dependencies updated!"

# Clean build artifacts
clean-build:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf build dist
    @echo "✅ Cleaned!"

# Clean build and cache artifacts
clean: clean-build
    @echo "🧹 Cleaning cache..."
    rm -rf .pytest_cache .ruff_cache
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

# Bump the version (level: minor | major)
bump level="minor": check
    #!/usr/bin/env bash
    set -euo pipefail
    uv version --bump "{{ level }}"
    VERSION="$(uv version --short)"
    echo "📝 Committing version ${VERSION}..."
    git add pyproject.toml uv.lock
    git commit -m "Release ${VERSION}" && git tag "v${VERSION}"
    echo "📤 Pushing to remote..."
    git push origin master --tags

# Publish package to PyPI
publish:
    @echo "📦 Publishing to PyPI..."
    @UV_PUBLISH_TOKEN="$(tr -d '\n' < ~/.pypi_token)" uv publish
    @echo "✅ Release completed!"

# Release a new version (level: minor | major)
release level="minor": clean-build check test
    @just bump {{ level }}
    @just build
    @just publish
