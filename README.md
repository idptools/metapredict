# metapredict: A machine learning-based tool for predicting protein disorder.
### Last updated May 2023


## Current version: metapredict V2-FF (V2.6)
The current recommended and default version of metapredict is metapredict V2-FF (version 2.6). Small increments (2.6.x) may be made as bug fixes or feature enhancements.

For context, V2-FF provides identical predictions to metapredict V2, but via `predict_disorder_batch()` provides 10-1000x improvement in performance on CPUs and GPUs. 

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

## Acknowledgements

PARROT, created by Dan Griffith, was used to generate the network used for metapredict. See [https://pypi.org/project/idptools-parrot/](https://pypi.org/project/idptools-parrot/) for some very cool machine learning stuff.

In addition to using Dan Griffith's tool for creating metapredict, the original code for `brnn_architecture.py` and `encode_sequence.py` was written by Dan.

We would like to thank the **DeepMind** team for developing AlphaFold and EBI/UniProt for making these data so readily available.

We would also like to thank the team at MobiDB for creating the database that was used to train this predictor. Check out their awesome stuff at [https://mobidb.bio.unipd.it](https://mobidb.bio.unipd.it)

## Changelog
This section is a log of recent changes with metapredict. My hope is that as I change things, this section can help you figure out why a change was made and if it will break any of your current workflows. The first major changes were made for the 0.56 release, so tracking will start there. Reasons are not provided for bug fixes for because the reason can assumed to be fixing the bug...

#### V2.6 (metapredict V2-FF) (May 2023)
Changes:

* V2.6 represents an update of metapredict to a version we refer to as metapredict V2-FF. V2-F22 provides a dramatic improvement in prediction performance when `batch_mode()` is used. On CPUs, this provides a 5-20x improvement in performance. On GPUs, this enables proteome-wide prediction in seconds. 

* Removed explicit multicore support and replaced with implicit parallelization in via `batch_predict()`.

* `batch_predict()` is now called in non-legacy predict for `predict_disorder_fasta()`, and can also be called via a `predict_disorder_batch()` which can take either a list or dictionary of sequences. 

* From command-line tools, `metapredict-predict-idrs`, and `metapredict-predict-disorder` will also use batch mode if legacy=False (default), which as well as being much faster now provide a status bar.

* Note that this update adds `tqdm` as a dependency for metapredict


#### V2.5 (March 2023)
Changes:

* Added the first multicore support to metapredict. Currently limited to metapredict-predict-disorder functionality.


#### V2.4.3
Changes:

* Updated the default names for `metapredict-predict-idrs` so that the FASTA output file is now called `idrs.fasta` instead of the inappropriate `shephard_idrs.tsv`.
* Added link to the new batch-mode Google Colab notebook!

#### V2.4.2 
Changes:

* Merged pull request from @FriedLabJHU to make f-strings more Pythonic. Thanks!!
* Changed `return_normalized` keyword to `normalized` in `meta.predict_pLDDT()` for consistency with other functions
* Added sanity check in case a passed sequence is an empty string (h/t Broder Schmidt)
* Added docs for the mode keyword in `meta.percent_disorder()`, so this is actually obvious to understand (h/t Broder Schmidt)
* Added several additional tests and updated the docs

#### V2.4.1
Changes:

* Some minor bug fixes and updates to code 

#### V2.3 
Changes:

* Merged pull request from @FriedLabJHU to fix keyword name `cutoff` to `disorder_threshold` in `meta.percent_disorder()`. Thanks!!

* Added the `mode` keyword into `meta.percent_disorder()` so disorder can be predicted in terms of what percentage of residues fall within IDRs, as well as what percent are above some fixed threshold.

#### V2.2

Changes: 
Fixed bug in metapredict-name command that could result in the organism name being named twice in the title of the graph.

#### V2.1

Changes:
Added functionality to graph the disorder of a protein by specifying its common name using the *metapredict-name* command.


#### V2.0

Changes:
Massive update to the network behind metapredict to improve accuracy. Implementation of code to keep the original network accessible to users. Changes to predict_disorder_domain functions where a DisorderObject is no returned and access to values are used by calling properties from the generated object. Graphing functionality updated to accommodate new cutoff value for the new network at 0.5. If the original metapredict network is used, then the cutoff value automatically resets to the original value of 0.3. Tests updated. Added metapredict-predict-idrs command to the command line. Added ability to predict disorder domains from python using external scores.


#### V1.51

Changes:
Updated to require V1.0 of alphaPredict for pLDDT scores. This improves accuracy from over 9% per residue to about 8% per residue for pLDDT score predictions. Documentation was updated for this change.


#### V1.5

Changes:
Fixed bug causing some functions to fail when getting sequences from Uniprot.
Added information on citing metapredict because the final publication went live.


#### V1.4

Change:
For clarity, previous functions that used the term 'confidence' such as *graph_confidence_uniprot()* were changed to use the term pLDDT rather than confidence. This is to clarify that the confidence scores are AlphaFold2 pLDDT confidence scores and not scores to reflect the confidence that the user should have in the metapredict disorder prediction. For command-line usage where confidence scores are optional (such as metapredict-graph-disorder), when a *-c* or *--confidence* flag used to be used, now a *-p* or *--pLDDT* flag is used to graph confidence scores. This is similarly reflected in Python where now you must use *pLDDT_scores=True* instead of *confidence_scores=True*.

#### V1.3

Change:
Added functionality to generate predicted AlphaFold2 pLDDT confidence scores. Can get scores or generate graphs from Python or command-line. Can also generate graphs with both predicted disorder and predicted pLDDT confidence scores. Also added functionality to predict disorder domains using scores from a different disorder predictor. 

#### V1.2

Change:
Major update. Changed some basic functionality. Made it such that you don't need to specify to save (for disorder prediction values or graphs). Rather, if a file path is specified, the files will be saved. Updated graphing functionality to allow for specifying the disorder cutoff line and to allow users to highlight various regions of the graph. Changed import such that you can now just use import metapredict as meta in Python (as opposed to import metapredict and then from metapredict import meta). Lots of backend changes to make metapredict more stable. Added additional testing. Updated documentation. Standardized file reading/writing. Made it so user can specify file type of saved graphs. Added backend meta_tools.py to handle the busywork. Changed version numbering for networks. Updated code to avoid OMPLIB issue (known bug in previous versions). Updated all command-line tools to match backend code.

#### V1.1

Change:
Fixed some bugs.

#### V1.0

Change:
Added functionality to generate graphs using a Uniprot ID as the input from command line. Added functionality to predict disorder domains. Added functionality to predict/graph disorder and predict disorder domains using a Uniprot ID from Python. Updated tests to include testing new functionality.


#### V0.61

Change:
Added functionality to predict or graph a disordered sequence from the command line by directly inputting the sequence. This can only do one sequence at a time and does not save the disorder values or graph. It is meant to provide a very quick and easy way to check something out.

#### V0.60

Change:
Added functionality to specify the horizontal lines that appear across the graphs rather than only having the option of having the dashed lines appear at intervals of 0.2. This functionality is in both Python and the command line.

#### V0.58

Change:
Updated the network with a newly trained network (using the same dataset as the original) that is slightly more accurate.

Reason:
I am always trying to find ways to make metapredict more accurate. When I manage to make the predictor better, I will update it.

#### V0.57

Change:
Bug fix that could result in prediction values to six decimal places in some scenarios

Change:
Changed titles for graphs generated by ``metapredict-graph-disorder`` to be 14 characters instead of 10. This is reflected in the title graph and the saved files.

Reason:
The 10 character save file was occasionally the same for multiple proteins. This resulted in the inability to discern which protein corresponded to which graph and could result in overwriting previously generated graphs. The 14 characters should be long enough to keep unique names for all proteins being analyzed.

Change:
Fixed bug that could result in crashing due to short fasta headers.


#### V0.56

Change:
Number of decimals in predictions was reduced from 6 to 3.

Reason:
It is not necessary to have accuracy out to 6 decimal places.

Change:
Added functionality to use . to specify current directory from command line.

Reason:
Improve functionality.

Change:
-DPI flag changed to -dpi in command line graphing function

Reason:
It was annoying to have to do all caps for this flag.

Change:
The ``predict-disorder`` command is now ``metapredict-predict-disorder`` and the ``graph-disorder`` command is now ``metapredict-graph-disorder``

Reason:
This will help users be able to use auto complete functionality from the command line using tab to pull up the graph or predict disorder commands while only having to remember metapredict.

Change:
The output for `.csv` files will now have a comma space between each value instead of just a comma.

Reason:
Improve readability.


### Copyright

Copyright (c) 2020-2023, Holehouse Lab - Washington University School of Medicine



