# Updating the metapredict images on Docker Hub

This is for whoever looks after [holehouselab/metapredict](https://hub.docker.com/r/holehouselab/metapredict) on Docker Hub. If you just want to *use* metapredict with Docker, you want [readme.md](readme.md) instead.

## What's on Docker Hub, and when to update it

| Tag | What it is | When to update it |
|-----|------------|-------------------|
| `latest` | The newest release on PyPI, with CPU-only PyTorch. Built from `release/Dockerfile`. | After every release to PyPI. |
| `vX.Y.Z` (e.g. `v3.2.0`) | One specific release. It's the same image as `latest` on the day it's made. | Once, when that release comes out. After that, leave it alone. |
| `cuda-latest` | The newest release, with the GPU version of PyTorch. Built from `release/Dockerfile` with one extra option. | After every release to PyPI. |
| `dev` | Whatever is on `master`. Built from `dev/Dockerfile`. | Whenever `master` has changes you'd like people to be able to try. |

The thing to remember is where each one gets metapredict from:

* The **stable** images (`latest`, `vX.Y.Z` and `cuda-latest`) install metapredict from PyPI. So you can only update them once the release is actually on PyPI, and they don't care what's on your machine.
* The **dev** image is built from the source code on your machine. So it has nothing to do with PyPI and you can update it any time, but what you have checked out is exactly what gets published.

Version tags get left alone because people use them to get the same thing every time. Rebuilding one later would quietly swap in newer versions of PyTorch and metapredict's other dependencies.

## One-off setup

You need to do this once per machine.

Use a Mac with Docker Desktop if you can. Most of the images are built for two kinds of processor (Intel/AMD and ARM), which means emulating whichever one your machine isn't. Docker Desktop does that out of the box. On Linux you'd have to set emulation up first; Docker's [multi-platform documentation](https://docs.docker.com/build/building/multi-platform/) explains how.

```bash
# log in with an account that's allowed to push to holehouselab
docker login

# make a builder that can build for more than one kind of processor
# (Docker's standard builder usually can't)
docker buildx create --name metapredict-builder --driver docker-container
```

**Run every command in this guide from the top-level directory of the repository** (the one with `pyproject.toml` in it). The paths in the commands only make sense from there.

## Updating the stable images after a release

### 1. Make sure the release is on PyPI

The new version needs to be listed on [PyPI](https://pypi.org/project/metapredict/) before you start. If it isn't, the build fails, because there's nothing for it to install.

### 2. Build and push `latest` and the version tag

```bash
# the release you just put on PyPI
VERSION=3.2.0

docker buildx build --builder metapredict-builder --no-cache \
    --platform linux/amd64,linux/arm64 \
    --build-arg METAPREDICT_VERSION=$VERSION \
    -t holehouselab/metapredict:latest \
    -t holehouselab/metapredict:v$VERSION \
    --push docker/release
```

On an Apple Silicon Mac, the build takes about five minutes, and then the upload takes as long as it takes to upload roughly 1 GB.

What the options do:

* `--no-cache` makes Docker download everything afresh, so the image gets the newest PyTorch and other dependencies and not whatever was left over from last time.
* `--platform linux/amd64,linux/arm64` builds an Intel/AMD version and an ARM version. Docker Hub keeps both under the one tag and gives each person the right one for their machine.
* `--build-arg METAPREDICT_VERSION=$VERSION` installs exactly that release, and not just whatever happens to be newest.
* Each `-t` is a tag. Here both tags point at the same image.
* `--push` uploads the result straight to Docker Hub. It doesn't show up in `docker images` on your machine.

Be aware that `latest` changes for everybody as soon as this finishes.

### 3. Check it worked

```bash
# should list linux/amd64 and linux/arm64
docker buildx imagetools inspect holehouselab/metapredict:latest

# should print the version you just released
docker pull holehouselab/metapredict:v$VERSION
docker run --rm holehouselab/metapredict:v$VERSION \
    python -c "import metapredict; print(metapredict.__version__)"
```

The first command also lists two `unknown/unknown` entries. Those are records of how the image was built, which Docker attaches on its own, and aren't a problem.

### 4. Build and push `cuda-latest`

This is the same release from the same Dockerfile, just with the version of PyTorch that can use an NVIDIA GPU. Do this one on an Intel/AMD Linux machine. It's only built for that kind of processor, so there's nothing to emulate and the special builder isn't needed. It's also several GB, and if the machine has an NVIDIA GPU you can check the image works before anybody else gets it.

```bash
VERSION=3.2.0

# build it
docker build --no-cache \
    --build-arg METAPREDICT_VERSION=$VERSION \
    --build-arg TORCH_INDEX_URL=https://pypi.org/simple \
    -t holehouselab/metapredict:cuda-latest docker/release

# check it can see the GPU (this should print True)
docker run --rm --gpus all holehouselab/metapredict:cuda-latest \
    python -c "import torch; print(torch.cuda.is_available())"

# upload it
docker login
docker push holehouselab/metapredict:cuda-latest
```

As of November 2026 `cuda-latest` hasn't been published yet, so the first time through, treat this step as untested and don't skip the GPU check.

### Rebuilding `latest` without a new release

Normally you don't. The one reason to is to pick up a fix in something metapredict depends on, like PyTorch. In that case run the command from step 2 again with the same `VERSION`, but leave out the `-t holehouselab/metapredict:v$VERSION` line so the version tag stays as it was.

## Updating `dev`

Update `dev` when changes have gone into `master` that you'd like people to be able to try before the next release. There's no schedule and nothing needs to be on PyPI. If `master` hasn't moved since the last time, there's nothing to do.

### 1. Get a clean, up-to-date `master`

The image is built from the files on your machine, not from GitHub. Uncommitted changes and stray files get published along with everything else, so check there aren't any:

```bash
git checkout master
git pull

# this should print nothing. If it lists anything, commit it or get rid of it first
git status --short

# this is the version the image will report
git describe --tags --long --dirty
```

`git describe` prints something like `v3.2.0-4-gabc1234`, which means 4 commits after the `v3.2.0` tag, and the image will report its version as `3.2.0+4.gabc1234`. If it ends in `-dirty`, you have uncommitted changes, so stop and sort those out.

### 2. Build and push

```bash
docker buildx build --builder metapredict-builder \
    --platform linux/amd64,linux/arm64 \
    -f docker/dev/Dockerfile \
    -t holehouselab/metapredict:dev \
    --push .
```

There's no `--no-cache` here, which keeps it quick: Docker reuses the PyTorch it installed last time and only rebuilds metapredict. Add `--no-cache` if you want the newest PyTorch as well.

### 3. Check it worked

```bash
# should list linux/amd64 and linux/arm64
docker buildx imagetools inspect holehouselab/metapredict:dev

# should print the version from `git describe` above
docker pull holehouselab/metapredict:dev
docker run --rm holehouselab/metapredict:dev \
    python -c "import metapredict; print(metapredict.__version__)"
```

## Updating the text on the Docker Hub page

Pushing an image doesn't touch the description on the [Docker Hub page](https://hub.docker.com/r/holehouselab/metapredict). That text is edited by hand on the website. To keep a record of it, it lives in this directory as [dockerhub_update.md](dockerhub_update.md): change that file, commit it, then paste it in.

1. Sign in to [Docker Hub](https://hub.docker.com).
2. Go to **My Hub**, then **Repositories**, and pick `holehouselab/metapredict`.
3. Under **Repository overview**, click **Edit**.
4. On the **Write** tab, delete what's there and paste in the whole of `dockerhub_update.md`. On a Mac, `pbcopy < docker/dockerhub_update.md` puts it on the clipboard.
5. Have a look at the **Preview** tab, then click **Update**.

The page text needs changing when the tags change (a new one appears, or an old one stops being updated) or when the way you run the image changes. A routine release doesn't need it.

The one-line description at the top of the page (100 characters at most) is separate. To change that, click the pencil icon under it on the same page.

## Checklist for a release

- [ ] The release is on PyPI
- [ ] `latest` and `vX.Y.Z` are pushed and checked
- [ ] `cuda-latest` is pushed and checked
- [ ] `dev` is pushed, if `master` has moved on since it was last built
- [ ] The text on the Docker Hub page still matches the tags that exist

## When things go wrong

* **`unable to prepare context: path "docker/release" not found`**. You're not in the top-level directory of the repository. `cd` there and run it again.
* **`Multiple platforms feature is currently not supported for docker driver`**. The command is missing `--builder metapredict-builder`, or the builder was never made on this machine (see [One-off setup](#one-off-setup)).
* **The push gets refused.** You're not logged in, or the account you're logged in with can't push to `holehouselab`. Run `docker login`.
* **Docker runs out of disk space.** Every build leaves a cache behind, and it adds up. `docker buildx prune --builder metapredict-builder` clears the cache for the builder used here, and `docker builder prune` clears the one for ordinary builds. Both ask before deleting anything.
* **It's taking ages.** Half of each two-processor build is emulated, which is slow. That's normal.
* **The `dev` image reports a version ending in `.dirty`.** There were uncommitted changes when you built it. Commit them and build it again.
