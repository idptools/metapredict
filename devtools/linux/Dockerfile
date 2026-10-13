# Linux image for running metapredict's tox suite in an isolated container.
# Used by devtools/linux/run_tox_in_docker.sh (or `tox -e linux` on the host).
#
# The image only holds the tooling. The metapredict source is copied in fresh
# each time the container starts, so the image never needs rebuilding when the
# code changes.

FROM python:3.12-slim-bookworm

# A C compiler to build the Cython extension, and git so that versioningit can
# read the package version from the repository's tags.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git \
    && rm -rf /var/lib/apt/lists/*

# uv (pinned for reproducibility) creates the test environments and downloads
# whichever Python interpreters tox asks for.
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /usr/local/bin/

# tox plus the tox-uv plugin, installed as an isolated uv tool.
RUN uv tool install --python 3.12 "tox>=4.11" --with "tox-uv>=1.11"
ENV PATH="/root/.local/bin:${PATH}"

# Keep uv's package cache and downloaded interpreters on a mounted volume
# (/uv-store) so they persist between runs. Installs copy rather than hard-link,
# because the cache volume and the container's filesystem are different mounts.
ENV UV_CACHE_DIR=/uv-store/cache \
    UV_PYTHON_INSTALL_DIR=/uv-store/python \
    UV_LINK_MODE=copy

# Install PyTorch's CPU-only build. The default Linux wheels from PyPI pull in
# several GB of CUDA libraries that these tests never use.
ENV UV_TORCH_BACKEND=cpu

# The repository's .git directory is copied in as root, so tell git to trust it.
RUN git config --global --add safe.directory '*'

WORKDIR /work
