# Development metapredict image, with metapredict built from this source tree.
#
# This builds the image behind the `dev` tag of holehouselab/metapredict on
# Docker Hub, and is how you put whatever you have checked out (including
# uncommitted changes) into a container. docker/README.md explains how to build
# and use it.
#
# The source is copied in, so the build context must be the repository root.
# From there:
#
#   docker build -f docker/dev/Dockerfile -t metapredict:dev .
#
# docker/dev/Dockerfile.dockerignore keeps build leftovers (.tox, build, dist
# and so on) out of the build context.
#
# Build arguments (all optional):
#
#   PYTHON_VERSION   Python the image runs metapredict with. Default: 3.12.
#   TORCH_INDEX_URL  Package index pip installs PyTorch from. Default: the
#                    CPU-only builds. Set it to https://pypi.org/simple (on
#                    linux/amd64) for the build with CUDA support.

# Declared before the first FROM so that both stages use the same Python: the
# virtual environment made in the first stage only works with the interpreter
# that created it.
ARG PYTHON_VERSION=3.12


# ------------------------------------------------------------------------------
# Stage 1: build metapredict from source into a virtual environment.
# ------------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# A C compiler to build the Cython extension, and git so that versioningit can
# read the package version from the repository's tags. Both stay in this stage,
# so they add nothing to the final image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/metapredict
ENV PATH="/opt/metapredict/bin:${PATH}"

# PyTorch goes in first, from its own index, so that we choose which build is
# used. The default Linux build on PyPI bundles several GB of CUDA libraries,
# which only help if you have an NVIDIA GPU. Installing metapredict afterwards
# finds PyTorch already present and leaves it alone. Doing this before the
# source is copied in also means Docker reuses this layer when only the code
# has changed.
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir torch --index-url "${TORCH_INDEX_URL}"

# The source tree, including .git (needed for the version number).
COPY . /src
RUN pip install --no-cache-dir /src


# ------------------------------------------------------------------------------
# Stage 2: the image people actually run. Only the virtual environment is
# carried over from stage 1.
# ------------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm

LABEL org.opencontainers.image.title="metapredict (development build)" \
      org.opencontainers.image.description="A machine learning-based tool for predicting protein disorder." \
      org.opencontainers.image.source="https://github.com/idptools/metapredict" \
      org.opencontainers.image.documentation="https://metapredict.readthedocs.io" \
      org.opencontainers.image.licenses="MIT"

COPY --from=builder /opt/metapredict /opt/metapredict
ENV PATH="/opt/metapredict/bin:${PATH}"

# matplotlib writes a font cache the first time it is imported, by default under
# the home directory. A container started with `--user` (so that output files
# are owned by you rather than by root) has no writable home directory, so point
# matplotlib at /tmp instead, which every user can write to.
ENV MPLCONFIGDIR=/tmp/matplotlib

# Fail the build here, rather than when someone runs the image, if the install
# is broken: check the compiled Cython extension imports and that a disorder
# prediction runs. The sequence is the first 40 residues of human FUS (UniProt
# P35637).
#
# /tmp is a throwaway (tmpfs) mount for this step only. The checks run as root
# and make matplotlib write its font cache; if that were kept, the image would
# ship a root-owned /tmp/matplotlib that a `--user` container cannot write to.
RUN --mount=type=tmpfs,target=/tmp \
    python -c "import metapredict; print('metapredict', metapredict.__version__)" \
    && python -c "import metapredict.backend.cython.domain_definition" \
    && metapredict-quick-predict MASNDYTQQATQSYGAYPTQPGQGYSQQSSQPYGQQSYSG

# The directory you mount your own files on (see docker/README.md), and where an
# interactive session starts.
WORKDIR /mount

# With no command given, start an interactive shell.
CMD ["/bin/bash"]
