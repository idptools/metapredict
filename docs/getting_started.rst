*********************************
Getting Started with metapredict
*********************************

What is metapredict?
====================
**metapredict** is a software tool to predict intrinically disordered regions in protein sequences. It is provided as a downloadable Python tool that includes a Python application programming interface (API) and a set of command-line tools for working with FASTA files. 

Our goal in building **metapredict** was to develop a robust, accurate, and high-performance predictor of intrinsic disorder that is also easy to install and use. As such, **metapredict** is implemented in Python and can be installed directly via `pip` (see below).

This already seems complicated...
-----------------------------------
As well as providing a set of high-performance software tools, **metapredict** is provided as a stand-alone webserver which can predict disorder profiles, scores, and contiguous IDRs for single sequences.

To access the webserver go to `metapredict.net <http://metapredict.net/>`_. 

How does metapredict work?
===========================
**metapredict** is a bit different than your typical protein disorder predictor. Instead of predicting the percent chance that a residue within a sequence might be disordered, **metapredict** tries to predict the *consensus disorder* score for the residue. Consensus disorder reports on the fraction of independent disorder predictors that would predict a given residue as disordered.

**metapredict** is a deep-learning-based predictor trained on consensus disorder data from 8 different predictors, as pre-computed and provided by `MobiDB <https://mobidb.bio.unipd.it/>`_. Functionally, this means each residue is assigned a score between 0 and 1 which reflects the confidence we have that the residue is disordered (or not). If the score was 0.5, this means half of the predictors predict that residue to be disordered. In this way, **metapredict** can help you quickly determine the likelihood that residues are disordered by giving you an approximation of what other predictors would predict (things got pretty 'meta' there, hence the name **metapredict**).

Why is metapredict useful?
===========================
Consensus disorder scores are really useful as they distribute the biases and uncertainty associated with any specific predictor. However, a drawback of consensus disorder databases (like MobiDB) is that they can only give you values of *previously predicted protein sequences*. **metapredict** provides a way around this, allowing arbitrary sequences to be analyzed! 

The major advantages that **metapredict** offers over existing predictors is performance, ease of use, and ease of installation. Given **metapredict** uses a pre-trained bidirectional recurrent neural network, on hardware we've tested **metapredict** gives ~10,000 residues per second prediction power. This means that predicting disorder across entire proteomes is accessible in minutes - for example it takes ~20 minutes to predict disorder for every human protein in the reviewed human proteome (~23000 sequences). We provide **metapredict** as a simple-to-use Python library to integrate into existing Python workflows, and as a set of command-line tools for the stand-alone prediction of data from direct input or from FASTA files.


Installation
==============
**metapredict** is available through GitHub or the Python Package Index (PyPI). To install through PyPI, run

.. code-block:: bash

	$ pip install metapredict

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

.. code-block:: bash

	$ git clone https://github.com/idptools/metapredict.git
	$ cd metapredict
	$ pip install .

This will install **metapredict** locally. If you modify the source code in the local repository, be sure to re-install with `pip`.

Known installation/execution issues
====================================

Below we include documentation on known issues. 

macOS libiomp clash 
^^^^^^^^^^^^^^^^^^^^^

PyTorch currently ships with its own version of the OpenMP library (``libiomp.dylib``). Unfortunately when numpy is installed from ``conda`` (although not from ``pip``) this leads to a collision because the ``conda``-derived numpy library also includes a local copy of the ``libiomp5.dylib`` library. This leads to the following error message (included here for google-ability).

.. code-block:: none 

   OMP: Error #15: Initializing libiomp5.dylib, but found libomp.dylib already initialized.
   OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. 
   That is dangerous, since it can degrade performance or cause incorrect results. The best thing to 
   do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static 
   linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you 
   can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, 
   but that may cause crashes or silently produce incorrect results. For more information, 
   please see http://www.intel.com/software/products/support/.

To avoid this error we make the executive decision to ignore this clash. This has largely not appeared to have any deleterious issues on performance or accuracy accross the tests run. If you are uncomfortable with this then the code in ``metapredict/__init__.py`` can be edited with ``IGNORE_LIBOMP_ERROR`` set to ``False`` and **metapredict** re-installed from the source directory.

Testing
========

To see if your installation of **metapredict** is working properly, you can run the unit test included in the package by navigating to the metapredict/tests folder within the installation directory and running:

.. code-block:: bash

	$ pytest -v

Example datasets
==================

Example data that can be used with metapredict can be found in the metapredict/data folder on GitHub. The example data set is just a .fasta file containing 5 protein sequences.
