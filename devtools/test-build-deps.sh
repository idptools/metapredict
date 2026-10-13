#!/usr/bin/env bash
#
# Sweep NumPy and Cython versions to find the lowest that build and pass.
#
# Unlike PyTorch (a pure runtime dependency, swept via tox.ini), NumPy and Cython
# are *build* dependencies: they compile metapredict's Cython extension. So each
# case installs the pinned NumPy/Cython and then builds metapredict with
# --no-build-isolation, ensuring the extension is compiled against exactly those
# versions (a build-isolated wheel would use a single NumPy/Cython for every env,
# which would defeat the sweep).
#
# Requirements: uv, a C compiler.
#
# Usage:
#   devtools/test-build-deps.sh              # run the numpy and cython sweeps
#   devtools/test-build-deps.sh numpy        # just the numpy sweep
#   devtools/test-build-deps.sh cython       # just the cython sweep
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON="${PYTHON:-3.11}"
ENV_ROOT="$REPO_ROOT/.venvs"
mkdir -p "$ENV_ROOT"

# NumPy sweep starts at 2.0 (NumPy 1.x is not supported); Cython sweep brackets
# the 0.29 -> 3.x transition (NumPy 2.0 support was added in Cython 3.0).
NUMPY_VERSIONS=("2.0.*" "2.1.*" "2.2.*" "2.3.*" "2.4.*")
CYTHON_VERSIONS=("0.29.*" "3.0.*" "3.1.*")

results=()
overall=0

run_case() {
    # $1 = label, $2 = numpy spec, $3 = cython spec
    local label="$1" numpy_spec="$2" cython_spec="$3"
    printf '\n============================================================\n'
    printf ' %s   (numpy==%s, cython==%s)\n' "$label" "$numpy_spec" "$cython_spec"
    printf '============================================================\n'

    local venv="$ENV_ROOT/builddeps-$label"
    rm -rf "$venv"

    # constrain numpy + cython for EVERY uv operation in this environment
    local cfile="$ENV_ROOT/builddeps-$label.constraint.txt"
    { echo "numpy==$numpy_spec"; echo "cython==$cython_spec"; } > "$cfile"
    export UV_CONSTRAINT="$cfile"

    if uv venv --python "$PYTHON" "$venv" \
        && uv pip install --python "$venv/bin/python" numpy cython "setuptools>=77" "versioningit~=2.0" \
        && uv pip install --python "$venv/bin/python" --no-build-isolation ".[test]"; then
        "$venv/bin/python" -c "import numpy, Cython, torch; print(f'  built with numpy {numpy.__version__}, Cython {Cython.__version__}, torch {torch.__version__}')"
        if ( cd metapredict/tests && "$venv/bin/python" -m pytest -q ); then
            results+=("$label: PASS")
        else
            results+=("$label: FAIL (tests)"); overall=1
        fi
    else
        results+=("$label: FAIL (build/install)"); overall=1
    fi
    unset UV_CONSTRAINT
}

what="${1:-all}"

if [ "$what" = "all" ] || [ "$what" = "numpy" ]; then
    for v in "${NUMPY_VERSIONS[@]}"; do
        run_case "numpy-${v%.*}" "$v" "3.1.*"   # vary numpy, hold cython at latest 3.x
    done
fi

if [ "$what" = "all" ] || [ "$what" = "cython" ]; then
    for v in "${CYTHON_VERSIONS[@]}"; do
        run_case "cython-${v%.*}" "2.4.*" "$v"  # vary cython, hold numpy at latest 2.x
    done
fi

printf '\n============================================================\n Summary\n============================================================\n'
for r in "${results[@]}"; do printf '  %s\n' "$r"; done
exit "$overall"
