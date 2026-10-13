#!/usr/bin/env bash
#
# Run the metapredict test suite across multiple Python versions, each in its
# own isolated, uv-managed virtual environment. For every version this script:
#
#   1. creates a fresh virtual environment with the requested Python (uv will
#      download the interpreter automatically if it is not already available),
#   2. installs metapredict + its test dependencies into that environment,
#      which compiles the Cython extension for that Python version, and
#   3. runs the full test suite, reporting a pass/fail summary per version.
#
# Requirements:
#   - uv .......... https://docs.astral.sh/uv/
#   - a C compiler (needed to build the Cython extension)
#
# Usage:
#   devtools/test-python-versions.sh                 # all supported versions
#   devtools/test-python-versions.sh 3.12 3.13       # only the given versions
#
set -euo pipefail

# Resolve the repository root (this script lives in devtools/).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
    echo "error: uv is not installed. See https://docs.astral.sh/uv/ to install it." >&2
    exit 1
fi

# Python versions to test. Override by passing versions as arguments; keep this
# list in sync with the classifiers in pyproject.toml and the CI matrix.
if [ "$#" -gt 0 ]; then
    VERSIONS=("$@")
else
    VERSIONS=("3.9" "3.10" "3.11" "3.12" "3.13" "3.14")
fi

# Isolated environments are created under .venvs/ (git-ignored).
ENV_ROOT="$REPO_ROOT/.venvs"
mkdir -p "$ENV_ROOT"

results=()
overall_status=0

for version in "${VERSIONS[@]}"; do
    printf '\n============================================================\n'
    printf ' Testing metapredict on Python %s\n' "$version"
    printf '============================================================\n'

    venv="$ENV_ROOT/py${version//./}"
    rm -rf "$venv"

    if uv venv --python "$version" "$venv" \
        && uv pip install --python "$venv/bin/python" ".[test]"; then
        # The tests read fixtures via paths relative to the tests directory.
        if ( cd metapredict/tests && "$venv/bin/python" -m pytest -q ); then
            results+=("Python $version: PASS")
        else
            results+=("Python $version: FAIL (tests)")
            overall_status=1
        fi
    else
        results+=("Python $version: FAIL (environment / install)")
        overall_status=1
    fi
done

printf '\n============================================================\n'
printf ' Summary\n'
printf '============================================================\n'
for result in "${results[@]}"; do
    printf '  %s\n' "$result"
done

exit "$overall_status"
