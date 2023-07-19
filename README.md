# metapredict: A machine learning-based tool for predicting protein disorder.
### Last updated July 2023


## Current version: metapredict V2-FF (V2.6)
The current recommended and default version of metapredict is metapredict V2-FF (version 2.6). Small increments (2.6.x) may be made as bug fixes or feature enhancements.

For context, V2-FF provides identical predictions to metapredict V2, but via `predict_disorder_batch()` provides 10-100x improvement in performance on CPUs and GPUs. 

To quantify this yourself, run:


	import metapredict
	metapredict.print_performance(batch=True)
	metapredict.print_performance(batch=False)
	
To compare the number of residues-per-second metapredict V2-FF predicts in batch mode vs. non-batch mode. For CPUs this is typically a 10-20x improvement. If GPUs are available this value can be substantially higher.	

## Installation

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
Documentation for metapredict automatically builds from the `/doc` directory in this repository and is hosted at [https://metapredict.readthedocs.io/](https://metapredict.readthedocs.io/). 

In brief, metapredict provides both command-line tools and a set of user-face functions from the metapredict python module. Both sets of tools are fully documented online.

## How can I use metapredict?
Metapredict can be used in four different ways:

1. As a stand-alone command-line tool (installable via pip - the code in this repository).
2. As a Python library for integrating into your favorite bioinformatics pipeline (installable via pip - the code in this repository).
3. As a web-server for examining disorder predictions on individual sequences found at [https://metapredict.net/](https://metapredict.net/).
4. *NEW as of August 2022:* as a Google Colab notebook for batch-predicting disorder scores for larger numbers of sequences: [**LINK HERE**](https://colab.research.google.com/github/idptools/metapredict/blob/batch_mode/colab/metapredict_colab.ipynb). Performance-wise, batch mode can predict the entire yeast proteome in ~1.5 min.
5. *NEW as of May 2023:* as part of the [ALBATROSS paper](https://www.biorxiv.org/content/10.1101/2023.05.08.539824), we provide a colab notebook for predicting IDRs on a proteome-wide scale [**LINK HERE**](https://colab.research.google.com/github/holehouse-lab/ALBATROSS-colab/blob/main/idrome_constructor/idrome_constructor.ipynb).

## How to cite

If you use metapredict for your work, please cite the metapredict paper: 
 
Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophys. J. 120, 4312–4319 (2021).

Note that in addition to the original paper, there's a V2 preprint; HOWEVER, we ask you only cite the original paper and describe the version being used (V1, V2 or V2-FF).

Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict V2: An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure. bioRxiv 2022.06.06.494887 (2022). doi:10.1101/2022.06.06.494887## Changes

## Changes

For changes see the `changelog.md` file in this directory.

## Acknowledgements

PARROT, created by Dan Griffith, was used to generate the network used for metapredict. See [https://pypi.org/project/idptools-parrot/](https://pypi.org/project/idptools-parrot/) for some very cool machine learning stuff.

In addition to using Dan Griffith's tool for creating metapredict, the original code for `brnn_architecture.py` and `encode_sequence.py` was written by Dan.

We would like to thank the **DeepMind** team for developing AlphaFold and EBI/UniProt for making these data so readily available.

We would also like to thank the team at MobiDB for creating the database that was used to train this predictor. Check out their awesome stuff at [https://mobidb.bio.unipd.it](https://mobidb.bio.unipd.it)

## Copyright
Copyright (c) 2020-2023, Holehouse Lab - Washington University School of Medicine



