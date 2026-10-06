# metapredict: A machine learning-based tool for predicting protein disorder.

[![PyPI version](https://img.shields.io/pypi/v/metapredict.svg)](https://pypi.org/project/metapredict/)
[![Python versions](https://img.shields.io/pypi/pyversions/metapredict.svg)](https://pypi.org/project/metapredict/)
[![License: MIT](https://img.shields.io/pypi/l/metapredict.svg)](https://github.com/idptools/metapredict/blob/master/LICENSE)
[![Platforms](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey.svg)](https://pypi.org/project/metapredict/)
[![CI](https://github.com/idptools/metapredict/actions/workflows/ci.yml/badge.svg)](https://github.com/idptools/metapredict/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/metapredict/badge/?version=latest)](https://metapredict.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://static.pepy.tech/badge/metapredict)](https://pepy.tech/project/metapredict)
[![Last commit](https://img.shields.io/github/last-commit/idptools/metapredict.svg)](https://github.com/idptools/metapredict/commits/)

### Last updated October 2026

## Current default version: V3.1.0
In November 2024, we changed the default version of metapredict from V2 to V3. Small increments (3.0.x) may be made as bug fixes or feature enhancements, and in Oct. we released 3.1.0, which is the current default and introduces a number of small bug fixes and performance enhancements. 

For context, V3 provides major improvements to V2. Metapredict V3 uses a **new network to predict disorder** that, in our benchmarks, is the most accurate version to date. In addition, *V3 is backward compatible with V2* and can be used as a drop-in replacement for V2. Although we've improved the Python API to massively simplify how you use metapredict, we've updated it so that all previously created functions *should still work*. If they don't, please raise an issue, and we will fix it ASAP!

## What are the major changes for metapredict V3?

1. **A new disorder prediction network**: Metapredict V3 uses a new (more accurate) network for disorder prediction. V1 and V2 are still available!
2. **A new pLDDT prediction network**: metapredict used to rely on an external package called [alphaPredict](https://github.com/ryanemenecker/alphaPredict) for pLDDT prediction. This same network is still available in metapredict when using ``meta.predict_pLDDT()`` by setting ``pLDDT_version=1``. However, the default V2 network performs better on all metrics for pLDDT prediction, so we recommend using V2!
3. **Easier batch predictions**: V2 previously required you to use ``predict_disorder_batch()`` to take advantage of the 10-100x improvement in prediction speed on CPUs and GPUs. However, you can now use a single function - ``predict_disorder()`` - on individual sequences, lists of sequences, and dictionaries of sequences, and metapredict will automatically take care of the rest for you, including running batch predictions if you input more than 1 sequence. 
4. **Easier access to DisorderObject**. You can now return the ``DisorderObject`` by setting ``return_domains=True`` when using ``predict_disorder()``.
5. **Batch prediction for all**: Previously, batch predictions were only available for the V2 disorder prediction network of metapredict. Now, you can do batch predictions using all of the disorder prediction networks - V1 (previously called legacy), V2, and V3!
6. **Batch pLDDT predictions**: Batch predictions (and therefore the massive increases in prediction speed) are now available for pLDDT predictions using the `predict_pLDDT()` function. 
7. **More device selection**: Newer versions of Torch (>2.0) support macOS GPU utilization through the Metal Performance Shaders (MPS) framework, so you can now choose to use mps on macOS. 
8. **Clearer device selection**: Metapredict used to fall back to CPU for predictions if it failed to use the GPU for any reason. This was well-intentioned but made troubleshooting GPU usage very tricky. Now if you specify using a specific device and it does not work, metapredict will not automatically fall back to CPU.
9. **Ability to get protein isoforms from UniProt**: We updated metapredict-uniprot to work with the new version of getSequence, which enables you to input a valid UniProt ID including designations for different protein isoforms. If you want to predict a sequence from the CLI using the name of the protein and the organism name (optional but recommended), please use `metapredict-name`, as `metapredict-uniprot` will only work with valid UniProt accession numbers.


## Installation
Metapredict is a Python package published on [PyPI](https://pypi.org/project/metapredict/). It supports Python 3.9–3.14; the instructions below use **Python 3.12**, which we recommend. Choose whichever of the three workflows — pip, conda, or uv — best matches your setup. If Python environments are new to you, we suggest reading up on Python package management and [conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) first.

Each option creates a clean, isolated Python 3.12 environment and then installs metapredict from PyPI.

metapredict needs PyTorch 2.3 or later, NumPy 2.0 or later and scipy 1.13 or later, and pip and uv install these (along with metapredict's other dependencies) automatically. If you install them with conda (Option 2), make sure conda provides at least these versions; otherwise pip will install newer copies from PyPI over them, mixing the two ecosystems (see the segfault warning below). Note that PyPI has no builds of PyTorch 2.3 or later for Intel (x86_64) Macs, so on an Intel Mac pip cannot install the PyTorch that metapredict needs.

#### Option 1 — pip (PyPI)
```bash
# create and activate a Python 3.12 virtual environment
python3.12 -m venv metapredict-env
source metapredict-env/bin/activate         # Windows: metapredict-env\Scripts\activate

# install metapredict from PyPI
pip install metapredict
```

#### Option 2 — conda
```bash
# create a Python 3.12 environment with the scientific dependencies from conda
conda create -n metapredict -c conda-forge -c pytorch python=3.12 numpy scipy pytorch cython matplotlib
conda activate metapredict

# install metapredict from PyPI
pip install metapredict
```
Installing numpy and PyTorch from conda (rather than letting pip pull them) keeps them in the same ecosystem — see the segfault warning below.

#### Option 3 — uv
```bash
# create a Python 3.12 environment (uv will download the interpreter if needed)
uv venv --python 3.12
source .venv/bin/activate                    # Windows: .venv\Scripts\activate

# install metapredict
uv pip install metapredict
```

#### Check the installation
Once installed, run:
```bash
metapredict-predict-disorder --help
```
from the command line; this should yield help info on the `metapredict-predict-disorder` command.

#### WARNING: Segfault when mixing `conda` and `pip` installs (March 2024)
As of at least PyTorch 2.2.2 on macOS, there are binary incompatibilities between `pip` and `conda` versions of PyTorch and numpy. Therefore, it is essential your numpy and PyTorch installs are from the same package manager. metapredict will - by default - pull dependencies from PyPI. However, other packages installed from conda may require conda-dependent numpy installations, which can "brick" a previously-working installation.

#### WARNING: Problems with installing Torch with proper CUDA version (November 2024).
**This is only relevant if you are trying to run metapredict on a CUDA-enabled GPU!**

On Linux, the PyTorch that pip installs from PyPI is built for a specific version of CUDA, and your NVIDIA driver must support that CUDA version. If your driver is older than that, a torch version that *does not have the correct CUDA version* will be installed. PyTorch then cannot use your GPU: `torch.cuda.is_available()` returns `False`, so metapredict quietly runs on the CPU (or raises an error if you asked for `device='cuda'`), and in some setups this can also cause a segfault. To fix this, you need to install torch for a CUDA version your driver supports. For example, to install PyTorch on Linux using pip with a CUDA version of 12.1, you would run:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

To figure out which version of CUDA your driver supports (assuming you have a CUDA-enabled GPU that is set up correctly), you need to run:
```bash
nvidia-smi
```
Which should return information about your GPU and NVIDIA driver version, and at the top the highest CUDA version your driver supports, so choose a PyTorch build for that CUDA version or an older one.

Please see the [PyTorch install instructions](https://pytorch.org/get-started/locally/) for more info. 


### Extended installation info

The current stable version of **metapredict** is available through GitHub or the Python Package Index (PyPI). 

To install from PyPI, run:
```bash
pip install metapredict
```

You can also install the current development version from
```bash
pip install git+https://git@github.com/idptools/metapredict
```
To clone the GitHub repository and gain the ability to modify a local copy of the code, run
```bash
git clone https://github.com/idptools/metapredict.git
cd metapredict
pip install -e .
```
metapredict includes a compiled (Cython) extension that speeds up the IDR domain decomposition. The wheels published on PyPI already include it for Linux (x86_64 and aarch64), macOS (Apple silicon) and Windows (64-bit) on Python 3.9–3.14, so `pip install metapredict` needs no compiler on those platforms. Installing from source (from GitHub, from a local clone with or without `-e`, or on any other platform) compiles the extension during installation, which needs a C compiler: the Xcode Command Line Tools on macOS (`xcode-select --install`), `gcc` on Linux (for example the `build-essential` package), or the Microsoft C++ Build Tools on Windows.

The `-e` flag links the installed version to your local copy of the code, so edits to the Python files take effect immediately. If you change the Cython code (`metapredict/backend/cython/domain_definition.pyx`), re-run `pip install -e .` to recompile it. If metapredict ever warns that it is falling back to a slower pure-Python implementation, its compiled extension could not be loaded; reinstalling metapredict fixes this.

## Documentation
Documentation for metapredict V3 automatically builds from the `/docs` directory in this repository and is hosted at [https://metapredict.readthedocs.io/](https://metapredict.readthedocs.io/). 

In brief, metapredict provides both command-line tools and a set of user-face functions from the metapredict python module. Both sets of tools are fully documented online.

## How can I use metapredict?
Metapredict can be used in five different ways:

1. As a stand-alone command-line tool (installable via pip - the code in this repository).
2. As a Python library for integrating into your favorite bioinformatics pipeline (installable via pip - the code in this repository).
3. As a web-server for examining disorder predictions on individual sequences found at [https://metapredict.net/](https://metapredict.net/).
4. *NEW as of August 2022:* as a Google Colab notebook for batch-predicting disorder scores for larger numbers of sequences: [**LINK HERE**](https://colab.research.google.com/drive/1UOrOxun9i23XDE8lFo_4I89Tw8P3Z1D-?usp=sharing). Performance-wise, batch mode can predict the entire yeast proteome in ~1.5 min using the Colab Notebook and much faster if using a local GPU.
5. *NEW as of May 2023:* as part of the [ALBATROSS paper](https://www.nature.com/articles/s41592-023-02159-5), we provide a colab notebook for predicting IDRs on a proteome-wide scale [**LINK HERE**](https://colab.research.google.com/github/holehouse-lab/ALBATROSS-colab/blob/main/idrome_constructor/idrome_constructor.ipynb).

## How to cite

If you use metapredict for your work, please cite the original metapredict paper and describe which version of metapredict you used (V1, V2, V2-FF, or V3):

Emenecker, R. J., Griffith, D. & Holehouse, A. S. metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophys. J. 120, 4312–4319 (2021). doi:[10.1016/j.bpj.2021.08.039](https://doi.org/10.1016/j.bpj.2021.08.039)

You may additionally cite the preprints describing later updates to metapredict — the [V2 preprint](https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2) and the metapredict "Tree of Life" preprint:

Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict V2: An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure. bioRxiv 2022.06.06.494887 (2022). doi:10.1101/2022.06.06.494887

Lotthammer, J. M., Hernández-García, J., Griffith, D., Weijers, D., Holehouse, A. S. & Emenecker, R. J. Metapredict enables accurate disorder prediction across the Tree of Life. bioRxiv 2024.11.05.622168 (2024). doi:10.1101/2024.11.05.622168


## Changes

For changes, see the `changelog.md` file in this directory or check them out on GitHub [here](https://github.com/idptools/metapredict/blob/master/changelog.md).

## Running tests
There are two ways to run the test suite: a quick run of `pytest` in your local clone while you develop, and **tox**, which tests metapredict in clean, isolated environments exactly as it would be installed. Use tox before a release, or whenever you want to check that metapredict works on a given platform or Python version.

### Quick check in your local clone
The tests run against the code in your local clone, including its compiled Cython extension, so first install metapredict in editable mode (which compiles the extension in place). Then run `pytest` from the `metapredict/tests` directory, because the tests load their input files using paths relative to that directory:
```bash
pip install -e ".[test]"
python devtools/check_cython_extension.py   # optional: confirms the compiled extension loads
cd metapredict/tests
pytest
```

### Testing with tox (macOS and Linux)
Each tox environment builds a wheel of metapredict (compiling the Cython extension), installs it with its test dependencies into a fresh, isolated environment, checks that the compiled extension loads and gives the right answers (`devtools/check_cython_extension.py`), and then runs the whole test suite against that installed copy. Your own Python environment is never touched.

#### What you need
- Python 3.9 or later, with `pip`.
- A C compiler and git to build the Cython extension: on macOS, the Xcode Command Line Tools (xcode-select --install); on Linux, gcc and git (for example, `sudo apt install build-essential git` on Debian/Ubuntu).
- tox itself. The simplest way to install it is with pip, into its own virtual environment so your system Python is left alone:
  ```bash
  python3 -m venv ~/tox-env
  ~/tox-env/bin/pip install tox
  ```
  Then use `~/tox-env/bin/tox` wherever `tox` appears below (or add `~/tox-env/bin` to your `PATH`).

You don't need uv or any particular Python versions installed. The first time it runs, tox installs the `tox-uv` plugin that `tox.ini` asks for, which brings [uv](https://docs.astral.sh/uv/) with it, and uv downloads whichever Python versions (3.9–3.14) the tests need. If you already use uv, `uvx --with tox-uv tox ...` works in place of `tox ...` without installing anything.

#### Running the tests
Run these from the root of the repository. They are the same on macOS and Linux:
```bash
tox -l                          # list the available environments
tox -e py312                    # the test suite on Python 3.12
tox -e py39,py314               # several Python versions
tox -m python                   # every supported Python version (3.9 – 3.14)
tox -e py312 -- -k stream -x    # anything after -- is passed to pytest
```
The first run downloads PyTorch and the other dependencies (cached by uv in `~/.cache/uv`), so it takes a while; after that a full `tox -e py312` run takes about three minutes on an Apple-silicon laptop. tox keeps its environments in `.tox/` at the root of your checkout (ignored by git). If your checkout lives in a synced folder such as Dropbox or iCloud, add `--workdir /tmp/metapredict-tox` to keep them out of it, e.g. `tox --workdir /tmp/metapredict-tox -e py312`.

`tox.ini` also defines sweeps that find the oldest supported PyTorch and scipy versions (`tox -m torch`, `tox -m scipy`); see `devtools/README.md` for those and for the NumPy/Cython build sweeps.

#### On macOS
tox installs PyTorch from PyPI, which only has Apple-silicon builds for the PyTorch versions metapredict supports (2.3 and later), so these instructions are for Apple-silicon Macs. The tests that use the Apple GPU (MPS) run; the CUDA tests are skipped.

#### On Linux
- **Without an NVIDIA GPU:** PyPI's Linux PyTorch includes several GB of CUDA libraries you won't use. Ask for the CPU-only build instead:
  ```bash
  UV_TORCH_BACKEND=cpu tox -m python
  ```
- **With an NVIDIA GPU:** let uv pick the PyTorch CUDA build that matches the machine's NVIDIA driver, and then check that the CUDA tests really ran (they should show `PASSED`, not `SKIPPED`):
  ```bash
  UV_TORCH_BACKEND=auto tox -m python
  UV_TORCH_BACKEND=auto tox -e py312 -- -v -k cuda
  ```
  Without `UV_TORCH_BACKEND=auto`, a PyTorch build that needs a newer driver than the machine has will report no GPU, and the CUDA tests will quietly be skipped. The CUDA tests compare GPU predictions against CPU reference scores to within 1e-3.

#### Linux tests from a Mac (Docker)
The Linux environment runs any of the commands above inside an isolated Linux container, so you can check that metapredict builds and passes its tests on Linux without leaving your Mac. Docker Desktop must be running. Everything after `--` is passed to tox inside the container (the default is `-e py312`):
```bash
tox -e linux                                   # Python 3.12 on Linux
tox -e linux -- -m python                      # every Python version on Linux
tox -e linux -- -e py312 -- -k stream          # tox arguments, then pytest arguments
METAPREDICT_DOCKER_PLATFORM=linux/amd64 tox -e linux   # x86_64 Linux (emulated, so much slower)
```
The same thing without tox on your Mac is `devtools/linux/run_tox_in_docker.sh [tox arguments]`.

Your working tree, including uncommitted changes, is mounted read-only and copied into the container, so nothing is ever written back. The image (`devtools/linux/Dockerfile`: gcc, git, uv and tox) is built the first time, and dependencies are cached in a Docker volume, so only the first run is slow. PyTorch's CPU-only build is used. By default, the container uses your Mac's own architecture (aarch64 on Apple Silicon). Docker on a Mac has no access to a GPU, so CUDA tests can only run on a Linux machine with an NVIDIA GPU (see above). To remove the image and cache afterward, find them with `docker images | grep metapredict-tox` and `docker volume ls | grep metapredict-tox`, then delete them with `docker rmi <image>` and `docker volume rm <volume>`.

#### Reading the results
Each environment prints the PyTorch and scipy versions it is testing with, then `OK: compiled extension gives the expected domains`, then the pytest summary, and finishes with `congratulations :)`. Some skipped tests are expected: the GPU tests in `test_metapredict_CPU_GPU.py` skip whenever that device isn't available (the CUDA tests everywhere except Linux with an NVIDIA GPU, and the MPS tests everywhere except Apple Silicon). If instead you see `FAIL: metapredict could not import its compiled Cython extension`, the extension did not build or load, which usually means no C compiler was found.

GitHub Actions also runs the test suite on Linux, macOS, and Windows for every push and pull request (`.github/workflows/ci.yml`), and builds and checks the release wheels for all three (`.github/workflows/wheels.yml`).

## Acknowledgements

We used a modified version of PARROT, created by Dan Griffith, to generate the network used for metapredict V3. We used the original implementation of PARROT to generate the V1 and V2 networks. See [https://pypi.org/project/idptools-parrot/](https://pypi.org/project/idptools-parrot/) for some very cool machine learning stuff. You can also check out the [PARROT paper](https://elifesciences.org/articles/70576).

In addition to using Dan Griffith's tool to create metapredict, Dan wrote the original code for encode_sequence.py.

We thank the **DeepMind** team for developing AlphaFold2 and EBI/UniProt for making these data so readily available.

We also thank the team at MobiDB for creating the database used to train metapredict V1. Check out their awesome stuff at [https://mobidb.bio.unipd.it](https://mobidb.bio.unipd.it)


## Copyright
Copyright (c) 2020-2026, Holehouse Lab - Washington University School of Medicine
