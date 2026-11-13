# metapredict

[metapredict](https://metapredict.readthedocs.io) is a machine learning-based tool for predicting intrinsic disorder in proteins from their sequence. This image has metapredict installed and ready to go, so you can run it on any machine with Docker, without setting up a Python environment.

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
* `-v "$(pwd):/mount"` makes your current directory available inside the container as `/mount`. The container can't see anything outside it.

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

# run your own Python script that uses metapredict
docker run --rm -v "$(pwd):/mount" holehouselab/metapredict python my_script.py

# check which version of metapredict is in the image
docker run --rm holehouselab/metapredict \
    python -c "import metapredict; print(metapredict.__version__)"
```

## Which tag should I use?

Leaving the tag off gets you `latest`, which is the right choice unless you have a reason to pick another.

| Tag | What's in it | Runs on |
|-----|--------------|---------|
| `latest` | The newest metapredict release on PyPI. | Intel/AMD and ARM (including Apple silicon) |
| `vX.Y.Z` (e.g. `v3.1.1`) | That exact release, for reproducibility. | Intel/AMD and ARM from `v3.1.1` on. Older ones (`v3.0.0`, `v2.65.1`) are Intel/AMD only. |
| `dev` | The current development version from [GitHub](https://github.com/idptools/metapredict). | Intel/AMD and ARM |
| `cuda-latest` | The newest release, with the version of PyTorch that can use an NVIDIA GPU. | Intel/AMD Linux |
| `latest_macos` | An old image that is no longer updated. Use `latest` instead. | ARM |

Everything except `cuda-latest` uses the CPU-only version of PyTorch. That keeps the images small, and metapredict is quick on a CPU.

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

With `-d cuda` you get an error if the GPU can't be used, rather than metapredict quietly running on the CPU.

## Good to know

**Output files owned by root (Linux).** On Linux, a container runs as root unless you say otherwise, so the files it writes belong to root. Add `--user "$(id -u):$(id -g)"` to `docker run` to run as yourself instead. You don't need this with Docker Desktop on macOS or Windows.

**Graphs.** A container has no screen, so nothing can pop up in a window. Use the commands that save graphs to files: `metapredict-graph-disorder my_proteins.fasta` writes one PNG per sequence into a directory called `disorder_out`, and `metapredict-uniprot P35637 -o fus_disorder.png` fetches a sequence from UniProt and saves its graph.

**Slow on an Apple silicon Mac?** You're probably running an old Intel/AMD image, which the Mac has to emulate. Run `docker pull holehouselab/metapredict` to get the current one, which has a native ARM version.

## What changed in November 2026

* `latest` now runs natively on both Intel/AMD and ARM machines, Apple silicon Macs included. The separate `latest_macos` tag isn't needed any more and is no longer updated.
* The standard images now use the CPU-only version of PyTorch, which took the download from about 6.7 GB to about 0.4 GB. If you were using `latest` with an NVIDIA GPU, switch to `cuda-latest`.

## More

The [full guide](https://github.com/idptools/metapredict/tree/master/docker) covers using metapredict from Python inside a container, adding your own packages, and building these images yourself from the Dockerfiles.

If you use metapredict in your work, please [cite it](https://metapredict.readthedocs.io/en/latest/how_to_cite.html).

If you run into any problems, please raise an issue on the [metapredict GitHub page](https://github.com/idptools/metapredict/issues).
