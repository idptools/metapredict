# metapredict: A machine learning-based tool for predicting protein disorder.

### Last updated November 2024

## Current version: metapredict V3
The current recommended and default version of metapredict is metapredict V3 (version 3.0). Small increments (3.0.x) may be made as bug fixes or feature enhancements.

For context, V3 provides major improvements to V2. Metapredict V3 uses a **new network to predict disorder** that in our benchmarks is the most accurate version of metapredict to date. In addition, *metapredict V3 is backwards compatible with V2* and can be used as a drop-in replacement for V2. Although the Python API has been improved to massively simplify how you can use metapredict, we have **for the time being** updated it such that all previously created functions *should still work*. If they do not, please raise an issue and we will fix the problem ASAP!
  
## What are the major changes for V3?

1. **A new disorder prediction network**: Metapredict V3 uses a new (more accurate) network for disorder prediction. V1 and V2 are still available!
2. **A new pLDDT prediction network**: metapredict used to rely on an external package called [alphaPredict](https://github.com/ryanemenecker/alphaPredict) for pLDDT prediction. This same network is still available in metapredict when using ``meta.predict_pLDDT()`` by setting ``version='V1'``. However, the default V2 network is by all metrics better for pLDDT prediction, so we recommend using the default!
3. **Easier batch predictions**: V2 previously required you to use ``predict_disorder_batch()`` to take advantage of the 10-100x improvement in prediction speed on CPUs and GPUs. However, you can now use a single function - ``predict_disorder()`` - on individual sequences, lists of sequences, and dictionaries of sequences, and metapredict will automatically take care of the rest for you while automatically doing batch predictions if more than 1 sequence is present. 
4. **Easier access to DisorderObject**. You can now return the ``DisorderObject`` by setting ``return_domains=True`` when using ``predict_disorder()``.
5. **Batch prediction for all**: Previously, batch predictions were only available for the V2 disorder prediction network of metapredict. Now, you can do batch predictions using all of the disorder prediction networks - v1 (previously called legacy), v2, and v3!
6. **Batch pLDDT predictions**: Batch predictions (and therefore the massive increases in prediction speed) are now available for pLDDT predictions using the `predict_pLDDT()` function. 
7. **More robust device selection**: Newer versions of Torch (>2.0) support MacOS GPU utilization through the Metal Performance Shaders (MPS) framework, so you can now choose to use *mps* on MacOS. In addition, if you try to specify using a CUDA-enabled GPU and it does not work, metapredict will not automatically fall back to CPU. 
8. We updated metapredict-uniprot to work with the new version of [getSequence](https://github.com/ryanemenecker/getSequence). This allows for getting different protein isoforms if specified.


## Installation
Metapredict is a software package written in Python. It can be installed from [PyPI](https://pypi.org/project/metapredict/) (the Python Package Index) using the tool `pip`. We always recommend managing your Python environment with conda. If these ideas are foreign to you, we recommend reading up a bit on Python package management and [conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) before continuing.

#### TL/DR: Recommended install commands are:
In most situations, the following two commands will ensure all the necessary dependencies are installed and work correctly:
```bash
# ensure dependencies are from the same ecosystem (conda)
conda install -c conda-forge -c pytorch python=3.11 numpy pytorch scipy cython matplotlib

# install from PyPI
pip install metapredict
```

To check the installation has worked run:
```bash
	metapredict-predict-disorder --help	
```
from the command line; this should yield help info on the `metapredict-predict-disorder` command.

#### WARNING: Segfault when mixing `conda` and `pip` installs (March 2024)
As of at least PyTorch 2.2.2 on macOS, there are binary incompatibilities between `pip` and `conda` versions of PyTorch and numpy. Therefore, it is essential your numpy and PyTorch installs are from the same package manager. metapredict will - by default - pull dependencies from PyPI. However, other packages installed from conda may require conda-dependent numpy installations, which can "brick" a previously-working installation.

#### WARNING: Problems with installing Torch with propert CUDA version (November 2024).
**This is only relevent if you are trying to run metapredict on a CUDA-enabled GPU!**

If you are on an older version of CUDA, a torch version that *does not have the correct CUDA version* will be installed. This can cause a segfault when running metapredict. To fix this, you need to install torch for your specific CUDA version. For example, to install PyTorch on Linux using pip with a CUDA version of 12.1, you would run:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
  
To figure out which version of CUDA you currently have (assuming you have a CUDA-enabled GPU that is set up correctly), you need to run:
```bash
nvidia-smi
```
Which should return information about your GPU, NVIDIA driver version, and your CUDA version at the top.

Please see the [PyTorch install instructions](https://pytorch.org/get-started/locally/) for more info. 
  

### Extended installation info

The current stable version of **metapredict** is available through GitHub or the Python Package Index (PyPI). 

To install from PyPI, run:

	pip install metapredict

You can also install the current development version from

	pip install git+https://git@github.com/idptools/metapredict

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

	git clone https://github.com/idptools/metapredict.git
	cd metapredict
	pip install -e .
	
Note you will need the -e flag to ensure the `cython` code compiles correctly, but this also means the installed version is linked to the local version of the code.	

This will install **metapredict** locally. If you modify the source code in the local repository, be sure to re-install with `pip`.

## Documentation
Documentation for metapredict V2 automatically builds from the `/doc` directory in this repository and is hosted at [https://metapredict.readthedocs.io/](https://metapredict.readthedocs.io/). 

In brief, metapredict provides both command-line tools and a set of user-face functions from the metapredict python module. Both sets of tools are fully documented online.

## How can I use metapredict?
Metapredict can be used in four different ways:

1. As a stand-alone command-line tool (installable via pip - the code in this repository).
2. As a Python library for integrating into your favorite bioinformatics pipeline (installable via pip - the code in this repository).
3. As a web-server for examining disorder predictions on individual sequences found at [https://metapredict.net/](https://metapredict.net/).
4. *NEW as of August 2022:* as a Google Colab notebook for batch-predicting disorder scores for larger numbers of sequences: [**LINK HERE**](https://colab.research.google.com/github/idptools/metapredict/blob/master/colab/metapredict_colab.ipynb). Performance-wise, batch mode can predict the entire yeast proteome in ~1.5 min.
5. *NEW as of May 2023:* as part of the [ALBATROSS paper](https://www.biorxiv.org/content/10.1101/2023.05.08.539824), we provide a colab notebook for predicting IDRs on a proteome-wide scale [**LINK HERE**](https://colab.research.google.com/github/holehouse-lab/ALBATROSS-colab/blob/main/idrome_constructor/idrome_constructor.ipynb).

## How to cite

If you use metapredict for your work, please cite the metapredict paper: 
 
Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophys. J. 120, 4312–4319 (2021).

Note that in addition to the original paper, there's a V2 preprint; HOWEVER, we ask you only cite the original paper and describe the version being used (V1, V2, V2-FF, or V3).

We are hoping to get a paper out for V3 in the near future (if we already have, then we just forgot to delete this sentence)...

Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict V2: An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure. bioRxiv 2022.06.06.494887 (2022). doi:10.1101/2022.06.06.494887

## Changes

For changes see the `changelog.md` file in this directory.

## Running tests
Note that to run tests you must compile the cython code in place. We suggest doing this by running the following set of commands:

pip uninstall metapredict; rm -rf build dist *.egg-info; python -m build; pip install .*

## Acknowledgements

PARROT, created by Dan Griffith, was used to generate the network used for metapredict. See [https://pypi.org/project/idptools-parrot/](https://pypi.org/project/idptools-parrot/) for some very cool machine learning stuff.

In addition to using Dan Griffith's tool for creating metapredict, the original code for `encode_sequence.py` was written by Dan.

We would like to thank the **DeepMind** team for developing AlphaFold2 and EBI/UniProt for making these data so readily available.

We would also like to thank the team at MobiDB for creating the database that was used to train metapredict V1. Check out their awesome stuff at [https://mobidb.bio.unipd.it](https://mobidb.bio.unipd.it)

### Running metapredict for CAID competition predictions
  
We include the ability to easily run predictions of .fasta formatted files and returns a 'CAID compliant' formatted file per sequence that is in the fasta file.

#### CAID formatted predictions from Python

To get CAID formatted predictions in Python, use the `predict_disorder_caid()` function. This function takes in the path to a .fasta formatted file of sequences and returns a 'CAID compliant' formatted file per sequence that is in the fasta file. The files generated are in .caid format where each sequence header is a line then the following lines for that sequence are tab separated and contain:
 1. The amino acid number
 2. The amino acid letter
 3. The metapredict disorder score
 4. The binarized metapredict score where 1=disordered and 0=not disordered.
  

To use this function, first import metapredict

```python:
import metapredict as meta
```

The function takes in three arguments: 
 1. `input_fasta` - the path to the .fasta file
 2. `output_path` - the path of where to save each CAID formatted prediction file. This should be a directory. Each sequence in the .fasta file will generate a file in this directory where the name of the file will be the sequence header and the file extension will be .caid.
 3. `version` - the version of metapredict to use.

The disorder cutoff values are handled automatically (0.42 for V1 and 0.5 for V2/V3).

**Examples**

**V1, AKA metapredict legacy**
 
```python: 
path_to_fasta='/Users/thisUser/Desktop/myCaidSeqs.fasta'
``` 

```python: 
meta.predict_disorder_caid(path_to_fasta, '/Users/thisUser/Desktop/CaidPredictions/metapredictV1', version='v1')
```
  
**V2**
  
```python: 
path_to_fasta='/Users/thisUser/Desktop/myCaidSeqs.fasta'
``` 

```python: 
meta.predict_disorder_caid(path_to_fasta, '/Users/thisUser/Desktop/CaidPredictions/metapredictV2, 'version='v2')
```
  
**V3, (new default, do not need to specify)**
  
```python: 
path_to_fasta='/Users/thisUser/Desktop/myCaidSeqs.fasta'
``` 

```python: 
meta.predict_disorder_caid(path_to_fasta, '/Users/thisUser/Desktop/CaidPredictions/metapredictV3, 'version='v3')
```

#### CAID formatted predictions from the command-line
  
To run metapredict for the CAID competition and get CAID-formatted files out, see the following examples:
  
 
```bash
metapredict-caid /Users/thisUser/Desktop/myCaidSeqs.fasta /Users/thisUser/Desktop/CaidPredictions/metapredictV1 v1
```
  
**V2:**
 
```bash
metapredict-caid /Users/thisUser/Desktop/myCaidSeqs.fasta /Users/thisUser/Desktop/CaidPredictions/metapredictV2 v2
```
  
**V3**
 
```bash
metapredict-caid /Users/thisUser/Desktop/myCaidSeqs.fasta /Users/thisUser/Desktop/CaidPredictions/metapredictV3 v3
```


## Copyright
Copyright (c) 2020-2024, Holehouse Lab - Washington University School of Medicine



