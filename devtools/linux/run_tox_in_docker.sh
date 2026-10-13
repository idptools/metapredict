#!/usr/bin/env bash
#
# Run metapredict's tox suite inside a Linux container.
#
# This builds metapredict from source on Linux (compiling the Cython extension
# with gcc), installs it into fresh tox environments and runs the full test
# suite against the installed package, so you can check everything works on
# Linux from a Mac (or anywhere Docker runs).
#
# Usage, from anywhere (any arguments are passed straight to tox):
#
#   devtools/linux/run_tox_in_docker.sh                    # tox -e py312
#   devtools/linux/run_tox_in_docker.sh -e py39,py314      # specific Pythons
#   devtools/linux/run_tox_in_docker.sh -m python          # every Python, 3.9 - 3.14
#   devtools/linux/run_tox_in_docker.sh -e py312 -- -k stream   # pass pytest arguments
#
# or through tox on the host:  tox -e linux [-- <tox arguments>]
#
# Containers run on the host's native architecture by default (aarch64 on Apple
# silicon). To test x86_64 Linux instead, which Docker emulates on Apple
# silicon and is therefore much slower, set:
#
#   METAPREDICT_DOCKER_PLATFORM=linux/amd64 devtools/linux/run_tox_in_docker.sh
#
# Your working tree, including uncommitted changes, is mounted read-only and
# copied into the container, so nothing is ever written back to it. Downloaded
# packages and Python interpreters are kept in a Docker volume (one per
# architecture), so only the first run is slow. Delete it with
#   docker volume rm metapredict-tox-uv-store-<arch>
#
# Requires: Docker, with the daemon running (e.g. Docker Desktop).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKERFILE_DIR="${REPO_ROOT}/devtools/linux"

# default tox arguments when none are given
DEFAULT_TOX_ARGS=(-e py312)

PLATFORM="${METAPREDICT_DOCKER_PLATFORM:-}"

if ! docker info > /dev/null 2>&1; then
    echo "error: cannot reach the Docker daemon. Start Docker (e.g. Docker Desktop) and try again." >&2
    exit 1
fi

# Name the image and cache volume after the architecture, because compiled
# packages and Python interpreters can't be shared between architectures.
if [ -n "${PLATFORM}" ]; then
    arch_label="${PLATFORM//\//-}"
    platform_args=(--platform "${PLATFORM}")
else
    arch_label="native-$(uname -m)"
    platform_args=()
fi
IMAGE="metapredict-tox-linux:${arch_label}"
STORE_VOLUME="metapredict-tox-uv-store-${arch_label}"

echo "[run_tox_in_docker] building image ${IMAGE} (cached after the first run)"
docker build ${platform_args[@]+"${platform_args[@]}"} --tag "${IMAGE}" "${DOCKERFILE_DIR}"

if [ "$#" -gt 0 ]; then
    tox_args=("$@")
else
    tox_args=("${DEFAULT_TOX_ARGS[@]}")
fi

echo "[run_tox_in_docker] running: tox ${tox_args[*]}"

# Inside the container: copy the read-only source into /work, leaving out
# anything built on the host (in particular a macOS-compiled extension, which
# would be useless on Linux), then run tox with its working directory outside
# the copied tree.
docker run --rm ${platform_args[@]+"${platform_args[@]}"} \
    --volume "${REPO_ROOT}:/src:ro" \
    --volume "${STORE_VOLUME}:/uv-store" \
    "${IMAGE}" \
    bash -c '
        set -euo pipefail
        tar -C /src \
            --exclude=./.tox \
            --exclude=./build \
            --exclude=./dist \
            --exclude="./*.egg-info" \
            --exclude=./docs/_build \
            --exclude=./metapredict/tests/output \
            --exclude=./.claude \
            --exclude=__pycache__ \
            --exclude="*.so" \
            --exclude="*.pyd" \
            --exclude=./metapredict/backend/cython/domain_definition.c \
            -cf - . | tar -C /work -xf -
        echo "[container] $(uname -sm), testing a copy of the working tree"
        exec tox --workdir /tmp/tox "$@"
    ' run-tox "${tox_args[@]}"
