# Development, testing, and deployment tools

This directory contains a collection of tools for running Continuous Integration (CI) tests, 
conda installation, and other development tools not directly related to the coding process.


## Manifest

### Running the test suites

There are four ways to run the tests. All commands are run from the repository
root unless noted.

| What | Command | Use it to |
|------|---------|-----------|
| Run the suite once | `pytest` (from `metapredict/tests/`) | day-to-day development |
| Across Python versions | `uvx --with tox-uv tox` | check 3.9–3.14 compatibility |
| Across runtime-dependency versions | `uvx --with tox-uv tox -m torch` (or `-m scipy`) | find the minimum supported PyTorch / scipy |
| Across NumPy / Cython versions | `devtools/test-build-deps.sh` | find the minimum supported NumPy / Cython |

Everything is driven by [uv](https://docs.astral.sh/uv/), which downloads any
Python interpreter it needs. If `tox` and `tox-uv` are already installed you can
drop the `uvx --with tox-uv` prefix and just run `tox`.

**1. Run the suite once.** The tests load fixtures via paths relative to the
tests directory, so run them from there:

```bash
cd metapredict/tests
pytest -v
```

**2. Across Python versions.** `tox.ini` (repo root, via the `tox-uv` plugin)
runs the suite on every supported Python:

```bash
uvx --with tox-uv tox                 # all Python versions (3.9 – 3.14)
uvx --with tox-uv tox -e py312        # a single Python version
```

(A plain shell-script equivalent is `devtools/test-python-versions.sh`.)

**3. Across runtime-dependency versions.** `tox.ini` defines sweeps on Python
3.11 (the version with the widest wheel coverage) for the runtime dependencies
whose version might matter — PyTorch and scipy. Each pins one
dependency per environment via the `UV_CONSTRAINT` files under
`devtools/version-constraints/` (a plain pin is re-resolved and upgraded when the
wheel installs). Each environment prints the versions it is testing with; take
the lowest green one as the minimum:

```bash
uvx --with tox-uv tox -m torch                # the PyTorch sweep      (py311-torch20 .. 28)
uvx --with tox-uv tox -m scipy                # the scipy sweep        (py311-scipy110 .. 116)
uvx --with tox-uv tox -e py311-torch23        # just one environment
```

Each environment otherwise uses the *current* NumPy, so these find the lowest
version of each dependency that is compatible with NumPy 2.x (for example, older
PyTorch was built against NumPy 1.x and cannot import under NumPy 2.x, and scipy
< 1.13 will not resolve alongside NumPy 2.x — limitations of those packages, not
metapredict).

**4. Across NumPy and Cython versions.** These are *build* dependencies (they
compile the Cython extension), so they cannot go through tox: a build-isolated
tox wheel would compile once against a single NumPy/Cython and reuse it for every
environment, testing nothing. `devtools/test-build-deps.sh` instead builds
metapredict with `--no-build-isolation` in each environment, so the extension is
compiled against exactly the pinned NumPy and Cython:

```bash
devtools/test-build-deps.sh           # sweep both NumPy and Cython
devtools/test-build-deps.sh numpy     # just NumPy
devtools/test-build-deps.sh cython    # just Cython
```

As with the PyTorch sweep, take the lowest green version as the minimum.

**5. On Linux, from a Mac (or anywhere Docker runs).** The `linux` tox environment runs any of the tox commands above inside an isolated Linux container, so you can check that metapredict builds (including compiling the Cython extension with gcc) and passes its tests on Linux before pushing. It needs Docker with the daemon running (e.g. Docker Desktop); nothing else is installed on the host. Everything after `--` is passed to tox inside the container:

```bash
uvx --with tox-uv tox -e linux                        # py312 on Linux (the default)
uvx --with tox-uv tox -e linux -- -m python           # every Python, 3.9 - 3.14
uvx --with tox-uv tox -e linux -- -e py311-torch23    # any other tox environment
uvx --with tox-uv tox -e linux -- -e py312 -- -k stream   # pass pytest arguments too
```

The same thing without tox on the host is `devtools/linux/run_tox_in_docker.sh [tox arguments]`. Your working tree, including uncommitted changes, is mounted read-only and copied into the container, so nothing is written back to it. The first run builds the image (`devtools/linux/Dockerfile`) and downloads the dependencies; these are cached in a Docker volume, so later runs are much faster. PyTorch's CPU-only build is used, to avoid several GB of CUDA libraries.

Containers run on the host's native architecture (aarch64 on Apple silicon). To test x86_64 Linux instead (emulated, so much slower on Apple silicon), set `METAPREDICT_DOCKER_PLATFORM=linux/amd64`.

**What every tox environment checks.** Each environment builds and installs a wheel of metapredict, then checks that the compiled Cython extension loads (`devtools/check_cython_extension.py`) and runs the test suite from the *installed* package. Running from the installed copy matters: from the source tree, pytest would import the uncompiled source instead of the wheel and quietly test the pure-Python fallback.

Continuous integration (GitHub Actions, `.github/workflows/ci.yml`) runs the suite across the supported Python versions on Linux, macOS and Windows on every push, and `.github/workflows/wheels.yml` builds and checks the release wheels for all three.

### Conda Environment:

This directory contains the files to setup the Conda environment for testing purposes

* `conda-envs`: directory containing the YAML file(s) which fully describe Conda Environments, their dependencies, and those dependency provenance's
  * `test_env.yaml`: Simple test environment file with base dependencies. Channels are not specified here and therefore respect global Conda configuration
  
### Additional Scripts:

This directory contains OS agnostic helper scripts which don't fall in any of the previous categories
* `scripts`
  * `create_conda_env.py`: Helper program for spinning up new conda environments based on a starter file with Python Version and Env. Name command-line options


## How to contribute changes
- Clone the repository if you have write access to the main repo, fork the repository if you are a collaborator.
- Make a new branch with `git checkout -b {your branch name}`
- Make changes and test your code
- Ensure that the test environment dependencies (`conda-envs`) line up with the build and deploy dependencies (`conda-recipe/meta.yaml`)
- Push the branch to the repo (either the main or your fork) with `git push -u origin {your branch name}`
  * Note that `origin` is the default name assigned to the remote, yours may be different
- Make a PR on GitHub with your changes
- We'll review the changes and get your code into the repo after lively discussion!


## Checklist for updates
- [ ] Make sure there is an/are issue(s) opened for your specific update
- [ ] Create the PR, referencing the issue
- [ ] Debug the PR as needed until tests pass
- [ ] Tag the final, debugged version 
   *  `git tag -a X.Y.Z [latest pushed commit] && git push --follow-tags`
- [ ] Get the PR merged in

## Versioning
Versioning will be automatically identified from the `git` tags and how many commits ahead this version is. The format 
follows [PEP 440](https://www.python.org/dev/peps/pep-0440/) and has the regular expression of:
```regexp
\d+.\d+.\d+(?\+\d+-[a-z0-9]+)
```
If the version of this commit is the same as a `git` tag, the installed version is the same as the tag, 
e.g. `metapredict-0.1.2`, otherwise it will be appended with `+X` where `X` is the number of commits 
ahead from the last tag, and then `-YYYYYY` where the `Y`'s are replaced with the `git` commit hash.
