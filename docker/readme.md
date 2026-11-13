# metapredict with Docker

Want to run metapredict without setting up a Python environment? Docker lets you do that. A Docker image is a ready-made box with metapredict and everything it needs already inside, so the only thing you have to install yourself is [Docker](https://docs.docker.com/get-started/get-docker/).

This directory holds the Dockerfiles that build the official metapredict images, and this page explains how to use them. If you just want to run metapredict, the first few sections are all you need.

## Quick start

```bash
# download the image (only needed once, or again later to update it)
docker pull holehouselab/metapredict

# go to the directory with your FASTA files, and start a container there
cd /path/to/my/data
docker run -it --rm -v "$(pwd):/mount" holehouselab/metapredict
```

That drops you into a shell inside the container. The directory you started from shows up there as `/mount`, which is also where you land, so metapredict can read your files and anything it writes ends up back on your computer:

```bash
# per-residue disorder scores, saved as disorder_scores.csv
metapredict-predict-disorder my_proteins.fasta

# the IDRs themselves, saved as idrs.fasta
metapredict-predict-idrs my_proteins.fasta

# leave the container when you're done
exit
```

What the `docker run` options do:

* `-it` gives you an interactive terminal.
* `--rm` deletes the container when you exit. Your results are safe: they're in `/mount`, which lives on your computer and not in the container.
* `-v "$(pwd):/mount"` makes your current directory available inside the container as `/mount`. The container can't see anything outside it, and anything saved elsewhere in the container is gone when you exit.

On Windows (PowerShell), write `${PWD}` instead of `$(pwd)`.

All of metapredict's command-line tools are in the image. The [command-line documentation](https://metapredict.readthedocs.io/en/latest/usage/command-line.html) has the full list.

## Running one command without a shell

Put a command after the image name and Docker runs it and then exits. This is the way to go for scripts and pipelines:

```bash
# predict disorder, and choose the name of the output file
docker run --rm -v "$(pwd):/mount" holehouselab/metapredict \
    metapredict-predict-disorder my_proteins.fasta -o disorder_scores.csv

# see the options for a command
docker run --rm holehouselab/metapredict metapredict-predict-idrs --help

# predict disorder for a sequence typed on the command line (nothing to mount)
docker run --rm holehouselab/metapredict \
    metapredict-quick-predict MASNDYTQQATQSYGAYPTQPGQGYSQQSSQPYGQQSYSG

# check which version of metapredict is in the image
docker run --rm holehouselab/metapredict \
    python -c "import metapredict; print(metapredict.__version__)"
```

## Using metapredict from Python

The image's `python` has metapredict installed, so you can run your own scripts. Save this as `idr_boundaries.py` next to your FASTA file:

```python
import metapredict as meta
import protfasta

# read the FASTA file into a {header: sequence} dictionary
sequences = protfasta.read_fasta('my_proteins.fasta')

# predict disorder for every sequence, asking for the IDRs as well as the scores
predictions = meta.predict_disorder(sequences, return_domains=True)

# print where the IDRs are in each protein
for header, prediction in predictions.items():
    print(header.split()[0], prediction.disordered_domain_boundaries)
```

and run it with:

```bash
docker run --rm -v "$(pwd):/mount" holehouselab/metapredict python idr_boundaries.py
```

Or, for an interactive Python session:

```bash
docker run -it --rm -v "$(pwd):/mount" holehouselab/metapredict python
```

If your script needs packages that aren't in the image, see [Adding other Python packages](#adding-other-python-packages).

## Making graphs

A container has no screen, so nothing can pop up in a window. Use the commands that save graphs to files instead:

```bash
# one graph per sequence, saved as PNGs in a new directory called disorder_out
docker run --rm -v "$(pwd):/mount" holehouselab/metapredict \
    metapredict-graph-disorder my_proteins.fasta

# fetch a sequence from UniProt by its accession and save its graph
docker run --rm -v "$(pwd):/mount" holehouselab/metapredict \
    metapredict-uniprot P35637 -o fus_disorder.png
```

`metapredict-quick-graph` can only show a window, so in a container it does nothing.

## Which image should I use?

Different versions of the image have different tags, which go after a colon (`holehouselab/metapredict:dev`). Leaving the tag off gets you `latest`.

| Tag | What's in it | Runs on |
|-----|--------------|---------|
| `latest` | The newest metapredict release on PyPI. Use this unless you have a reason not to. | Intel/AMD and ARM (including Apple silicon) |
| `vX.Y.Z` (e.g. `v3.2.0`) | That exact release, for reproducibility. | Intel/AMD and ARM |
| `dev` | The current development version from [GitHub](https://github.com/idptools/metapredict). | Intel/AMD and ARM |
| `cuda-latest` | The newest release, with the version of PyTorch that can use an NVIDIA GPU. | Intel/AMD Linux |

Everything except `cuda-latest` uses the CPU-only version of PyTorch. That keeps the images small (about 1.3 GB, where the GPU version is several times that), and metapredict is quick on a CPU.

## Using an NVIDIA GPU

Most people won't need this. But if you have a lot of sequences and a Linux machine with an NVIDIA GPU, the `cuda-latest` image can use it. The machine needs the NVIDIA driver and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), and you add `--gpus all` to `docker run`:

```bash
# check the container can see the GPU (this should print True)
docker run --rm --gpus all holehouselab/metapredict:cuda-latest \
    python -c "import torch; print(torch.cuda.is_available())"

# predict on the GPU
docker run --rm --gpus all -v "$(pwd):/mount" holehouselab/metapredict:cuda-latest \
    metapredict-predict-disorder my_proteins.fasta -d cuda
```

metapredict uses a CUDA GPU on its own if it finds one, so `-d cuda` isn't strictly needed. It's worth adding anyway: with it, you get an error if the GPU can't be used, rather than metapredict quietly running on the CPU.

Docker on a Mac can't use the Mac's GPU, so in a container on a Mac metapredict always runs on the CPU.

## Things worth knowing

### Who owns the output files (Linux)

On Linux, a container runs as root unless you say otherwise, so the files it writes into your directory belong to root. Add `--user` to run as yourself instead:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$(pwd):/mount" holehouselab/metapredict \
    metapredict-predict-disorder my_proteins.fasta
```

You don't need this with Docker Desktop on macOS or Windows, where the files are yours either way.

### Apple silicon Macs

`latest` and `dev` each come in an Intel/AMD and an ARM version, and Docker picks the right one for your machine without being asked. If metapredict is crawling in a container on an Apple silicon Mac, you're probably running an Intel/AMD image, which the Mac has to emulate, and that is many times slower. To check which one you have:

```bash
docker image inspect --format '{{.Architecture}}' holehouselab/metapredict
```

`arm64` is the one you want. If it says `amd64`, run `docker pull holehouselab/metapredict` to get the current image. Getting a fast image on a Mac used to need a separate `latest_macos` tag; you don't need that any more.

### Adding other Python packages

To use other packages alongside metapredict, make your own image on top of this one. Put this in a file called `Dockerfile` in an empty directory:

```dockerfile
FROM holehouselab/metapredict
RUN pip install --no-cache-dir biopython
```

then build it from that directory, and use `my-metapredict` wherever you'd have used `holehouselab/metapredict`:

```bash
docker build -t my-metapredict .
```

## Building the images yourself

You don't need to do this to use metapredict, because the images on Docker Hub are built from these same files. If you'd like to anyway, you need a copy of this repository and Docker 23 or newer (the Dockerfiles rely on BuildKit, which has been Docker's standard builder since version 23). Run these from the top-level directory of the repository:

```bash
# the newest release on PyPI
docker build -t metapredict docker/release

# a specific release from PyPI
docker build --build-arg METAPREDICT_VERSION=3.1.1 -t metapredict:v3.1.1 docker/release

# whatever is in your copy of the source code, uncommitted changes included
docker build -f docker/dev/Dockerfile -t metapredict:dev .

# the newest release with the GPU version of PyTorch (Intel/AMD only)
docker build --platform linux/amd64 \
    --build-arg TORCH_INDEX_URL=https://pypi.org/simple \
    -t metapredict:cuda docker/release
```

Then use your image exactly as above, with its name in place of `holehouselab/metapredict`:

```bash
docker run -it --rm -v "$(pwd):/mount" metapredict
```

### What's in this directory

* `release/Dockerfile` installs metapredict from PyPI. It doesn't need anything from the repository, which is why its build only gets handed the `docker/release` directory.
* `dev/Dockerfile` builds metapredict from the source code it sits in, so its build needs the whole repository (the `.` at the end of the command). The version number comes from git, just like a normal install from source, and has `.dirty` on the end if you have uncommitted changes.
* `dev/Dockerfile.dockerignore` keeps things like `.tox` and `build` from being sent to Docker during the dev build.
* `PUBLISHING.md` is the maintainers' guide to updating the images on Docker Hub.
* `DOCKERHUB_OVERVIEW.md` is the text shown on the Docker Hub page, kept here so there's a record of it.

Both Dockerfiles work in two stages. The first installs metapredict into a virtual environment, with a C compiler on hand to build metapredict's Cython extension. The second copies just that environment into a clean image, so the compiler doesn't end up in what you run. The build then checks the extension loads and runs a prediction, so a broken image fails to build rather than failing later when you use it.

### Build options

Pass these with `--build-arg NAME=value`:

| Option | Default | What it does |
|--------|---------|--------------|
| `PYTHON_VERSION` | `3.12` | The version of Python in the image. |
| `METAPREDICT_VERSION` | newest release | The release to install from PyPI (`release/Dockerfile` only). |
| `TORCH_INDEX_URL` | `https://download.pytorch.org/whl/cpu` | Where pip gets PyTorch from. The default is the small CPU-only version. `https://pypi.org/simple` gets you PyTorch's standard version, which on Intel/AMD Linux can use an NVIDIA GPU. If your NVIDIA driver is too old for that one, pick the index for a CUDA version it does support (e.g. `https://download.pytorch.org/whl/cu126`); the installation section of the [main README](../README.md) explains how to find out which. |

One thing to watch: Docker remembers each step of a build and reuses it next time. So if you rebuild `docker/release` after a new metapredict release comes out, you'll get the old one again unless you add `--no-cache`, which makes Docker start from scratch.

## Publishing to Docker Hub (for maintainers)

[PUBLISHING.md](PUBLISHING.md) has the step-by-step instructions for updating the images on Docker Hub: when to update each tag, the commands to do it, how to check it worked, and how to change the text on the Docker Hub page.

## Docker in four questions

**What is Docker?** A tool for packaging a program together with everything it needs to run (here Python, PyTorch, and metapredict itself) so that it runs the same way on any computer with Docker installed.

**What's an image?** The package itself: a snapshot of a small Linux system with metapredict already installed. Images are read-only.

**What's a container?** A running copy of an image. `docker run` starts one, and with `--rm` it's thrown away when it finishes. The image is untouched, so the next container starts fresh.

**What does pulling an image mean?** Downloading it, in this case from [Docker Hub](https://hub.docker.com/r/holehouselab/metapredict). You only need to do it once, and again whenever you want a newer version.

## Help!

If something here doesn't work, please raise an issue on the [metapredict GitHub page](https://github.com/idptools/metapredict/issues).
