*********************************
Getting Started with metapredict
*********************************

What is metapredict?
====================
**metapredict** is a software tool to predict intrinsically disordered regions in protein sequences. It is provided as a downloadable Python tool that includes a Python application programming interface (API) and a set of command-line tools for working with FASTA files. 

Our goal in building **metapredict** was to develop a robust, accurate, and high-performance predictor of intrinsic disorder that is also easy to install and use. As such, **metapredict** is implemented in Python and can be installed directly via `pip` (see below).

metapredict is ALSO available via a `webserver for single sequence prediction <http://https://metapredict.net>`__ and `a Google Colab notebook for batch prediction <https://colab.research.google.com/drive/1UOrOxun9i23XDE8lFo_4I89Tw8P3Z1D-?usp=sharing>`__. However, this documentation here focuses on the Python package which provides both a set of Python library functions and a set of command-line tools.


Recent metapredict updates and news
====================================

November 2024: Update to default version (metapredict V3)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In November 2024, we changed the default version of metapredict from V2 to V3. Small increments (3.0.x) may be made as bug fixes or feature enhancements.

For context, V3 provides major improvements to V2. Metapredict V3 uses a **new network to predict disorder** that in our benchmarks is the most accurate version to date. In addition, *V3 is backwards compatible with V2* and can be used as a drop-in replacement for V2. Although the Python API has been improved to massively simplify how you can use metapredict, we have **for the time being** updated it such that all previously created functions *should still work*. If they do not, please raise an issue and we will fix the problem ASAP!


What are the major changes for metapredict V3?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. **A new disorder prediction network**\ : Metapredict V3 uses a new (more accurate) network for disorder prediction. V1 and V2 are still available!
#. **A new pLDDT prediction network**\ : metapredict used to rely on an external package called `alphaPredict <https://github.com/ryanemenecker/alphaPredict>`_ for pLDDT prediction. This same network is still available in metapredict when using ``meta.predict_pLDDT()`` by setting ``pLDDT_version=1``. However, the default V2 network is by all metrics better for pLDDT prediction, so we recommend using V2!
#. **Easier batch predictions**\ : V2 previously required you to use ``predict_disorder_batch()`` to take advantage of the 10-100x improvement in prediction speed on CPUs and GPUs. However, you can now use a single function - ``predict_disorder()`` - on individual sequences, lists of sequences, and dictionaries of sequences, and metapredict will automatically take care of the rest for you including running batch predictions if you input more than 1 sequence. 
#. **Easier access to DisorderObject**. You can now return the ``DisorderObject`` by setting ``return_domains=True`` when using ``predict_disorder()``.
#. **Batch prediction for all**\ : Previously, batch predictions were only available for the V2 disorder prediction network of metapredict. Now, you can do batch predictions using all of the disorder prediction networks - V1 (previously called legacy), V2, and V3!
#. **Batch pLDDT predictions**\ : Batch predictions (and therefore the massive increases in prediction speed) are now available for pLDDT predictions using the ``predict_pLDDT()`` function. 
#. **More device selection**\ : Newer versions of Torch (>2.0) support MacOS GPU utilization through the Metal Performance Shaders (MPS) framework, so you can now choose to use *mps* on MacOS. 
#. **More clear device selection**\ : Metapredict used to fall back to using CPU for predictions if it failed to use GPU for whatever reason. This had good intentions but made troubleshooting GPU usage very tricky. Now if you specify using a specific device and it does not work, metapredict will not automatically fall back to CPU.
#. **Ability to get protein isoforms from Uniprot**\ : We updated ``metapredict-uniprot`` to work with the new version of `getSequence <https://github.com/ryanemenecker/getSequence>`_\ , which enables you to input a valid Uniprot ID including designations for different protein isoforms. If you want to predict a sequence from the CLI using the name of the protein and the organism name (optional but recommended), please use ``metapredict-name`` as **\ ``metapredict-uniprot`` will only work with valid Uniprot Accession numbers**.


Installation
=============

Metapredict is a software package written in Python. It can be installed from `PyPI <https://pypi.org/project/metapredict/>`_ (the Python Package Index) using the tool ``pip``. We always recommend managing your Python environment with conda. If these ideas are foreign to you, we recommend reading up a bit on Python package management and `conda <https://conda.io/projects/conda/en/latest/user-guide/getting-started.html>`_ before continuing.

TL/DR: Recommended install commands are:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In most situations, the following two commands will ensure all the necessary dependencies are installed and work correctly:

.. code-block:: bash

   # ensure dependencies are from the same ecosystem (conda)
   conda install -c conda-forge -c pytorch python=3.11 numpy pytorch scipy cython matplotlib

   # install from PyPI
   pip install metapredict

To check the installation has worked run:

.. code-block:: bash

   metapredict-predict-disorder --help

from the command line; this should yield help info on the ``metapredict-predict-disorder`` command.

WARNING: Segfault when mixing ``conda`` and ``pip`` installs (March 2024)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of at least PyTorch 2.2.2 on macOS, there are binary incompatibilities between ``pip`` and ``conda`` versions of PyTorch and numpy. Therefore, it is essential your numpy and PyTorch installs are from the same package manager. metapredict will - by default - pull dependencies from PyPI. However, other packages installed from conda may require conda-dependent numpy installations, which can "brick" a previously-working installation.

WARNING: Problems with installing Torch with propert CUDA version (November 2024).
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**This is only relevent if you are trying to run metapredict on a CUDA-enabled GPU!**

If you are on an older version of CUDA, a torch version that *does not have the correct CUDA version* will be installed. This can cause a segfault when running metapredict. To fix this, you need to install torch for your specific CUDA version. For example, to install PyTorch on Linux using pip with a CUDA version of 12.1, you would run:

.. code-block:: bash

   pip install torch --index-url https://download.pytorch.org/whl/cu121

To figure out which version of CUDA you currently have (assuming you have a CUDA-enabled GPU that is set up correctly), you need to run:

.. code-block:: bash

   nvidia-smi

Which should return information about your GPU, NVIDIA driver version, and your CUDA version at the top.

Please see the `PyTorch install instructions <https://pytorch.org/get-started/locally/>`_ for more info. 

Extended installation info
^^^^^^^^^^^^^^^^^^^^^^^^^^

The current stable version of **metapredict** is available through GitHub or the Python Package Index (PyPI). 

To install from PyPI, run:

.. code-block:: bash

   pip install metapredict

You can also install the current development version from

.. code-block:: bash

   pip install git+https://git@github.com/idptools/metapredict

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

.. code-block:: bash

   git clone https://github.com/idptools/metapredict.git
   cd metapredict
   pip install -e .

Note you will need the -e flag to ensure the ``cython`` code compiles correctly, but this also means the installed version is linked to the local version of the code.    

This will install **metapredict** locally. If you modify the source code in the local repository, be sure to re-install with ``pip``.


About metapredict
====================
It's important to understand how tools were built and developed. Below we provide a quick overview of how metapredict works and was trained.

How does metapredict work?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**metapredict** uses a machine-learning network to generate per-residue scores from amino acid sequences that reflect the likelihood that the residue is disordered.

How was metapredict V1 trained?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**metapredict V1** is a deep-learning-based predictor trained on consensus disorder data from 8 different predictors, as pre-computed and provided by `MobiDB <https://mobidb.bio.unipd.it/>`_. Functionally, this means each residue is assigned a score between 0 and 1 which reflects the confidence we have that the residue is disordered (or not). If the score was 0.5, this means half of the predictors predict that residue to be disordered. In this way, **metapredict V1** can determine the likelihood that residues are disordered by giving you an approximation of what other predictors would predict (things got pretty 'meta' there, hence the name **metapredict**).

Note that metapredict V1 predictions are available via the :code:`--version 1` from the CLI or :code: version=1 in Python.

How was metapredict V2 trained?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
V2 was trained by generating an initial hybrid score that combined *predicted* AlphaFold2 pLDDT scores (pLDDT network V1) with consensus disorder (metapredict disorder scores V1) along with some signal process algorithms to make a new structure/disorder consensus prediction. Finally, we trained a new deep learning network to predict our hybrid network (meta meta), substantially improving accuracy with very little loss in performance.

These changes and new assessment of performance are available in our preprint: `An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure.  <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_ In bioRxiv (p. 2022.06.06.494887). https://doi.org/10.1101/2022.06.06.494887


How does metapredict V2 differ from V2-FF
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

metapredict V2 and V2-FF are identical in terms of predictions and features, with the major difference being that metapredict V2-FF offers batched predictions. Batched predictions are automatically parallelized on either the CPU or GPU. In addition, we rewrote the metapredict domain decomposition algorithm in C to provide a 10-20x improvement in performance for this step.

We note that V2-FF was released after CAID, so the performance reported there is the V2 network performance. Because metapredict V2-FF is implemented in a `Google Colab notebook for batch prediction <https://colab.research.google.com/drive/1UOrOxun9i23XDE8lFo_4I89Tw8P3Z1D-?usp=sharing>`__ you don't have to take our word for it that it's fast; just upload a proteome and see for yourself! **Note**: The colab notebook has now been updated to V3. However, all 3 metapredict networks are available for use in the notebook!

What is new as far as the disorder prediction in V3?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

V2 and V3 are fairly similar given that they have the same underlying disorder prdiction approach in that both networks combine V1 consensus disorder scores and AlphaFold2 (AF2) pLDDT scores in some way to come up with a final 'disorder prediction score'. However, there are some important difference between V2 and V3 that allowed us to make a more accurate network. First, V3 was made at a time when **many more** AF2 structures (and therefore their AF2 pLDDT scores) were available. This allowed us to combine metapredict V1 scores with the *actual AF2 pLDDT scores* as opposed to V2 where we had to use *predicted pLDDT scores*. Second, we now have more powerful computational hardware available to us, allowing us to train on a larger dataset. Third, we used more advanced approaches to hyperparamter optimization during training. All of this allowed us to make a more accurate network for V3. 


Generating predicted pLDDT (AlphaFold2 confidence) scores in metapredict
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In addition to predicting disorder scores, metapredict offers predicted confidence scores from AlphaFold2. These confidence scores measure the local confidence that AlphaFold2 has in its predicted structure. The scores go from 0-100 where 0 represents low confidence and 100 represents high confidence. For more information, please see: *Highly accurate protein structure prediction with AlphaFold* https://doi.org/10.1038/s41586-021-03819-2. In describing these scores, the team states that regions with pLDDT scores of less than 50 should not be interpreted except as *possible* disordered regions.


What might the predicted confidence scores from AlphaFold2 be used for?
-----------------------------------------------------------------------------
These scores can be used for many applications such as generating a quick preview of which regions of your protein of interest AF2 might be able to predict with high confidence, or which regions of your protein *might* be disordered. 

AF2 is not (strictly speaking) a disorder predictor, and the confidence scores are not directly representative of protein disorder. Therefore, any conclusions drawn with regards to disorder from predicted AF2 confidence scores should be interpreted with care, but they may be able to provide an additional metric to assess the likelihood that any given protein region may be disordered.


Why is metapredict useful?
===========================
We think **metapredict** is useful for three main reasons.

1. It's highly accurate and provides strong boundaries between disordered and folded regions.
2. It's incredibly fast; on CPUs one can predict every IDR in the human proteome in ~2.5 minutes. On modest GPUs one can predict every IDR in the human proteome in under 5 seconds. This stands in stark contrast to other predictors which place length caps on sequences and can take hours per sequence.
3. It is easy to use and is distributed via a wide range of channels. In addition to this Python package, metapredict is distributed as a stand-alone webserver **(see: https://metapredict.net/ )**, colab notebooks for large-scale predictions, and as an `API for SHEPHARD <https://shephard.readthedocs.io/en/latest/apis.html#metapredict>`__, our general-purpose toolkit for working with an annotating large protein datasets. This Python package further implements metapredict as both Python modules and as a set of command-line tools. 

In summary, we believe metapredict provides the three key ingredients of a useful disorder predictor: it's extremely accurate, it's incredibly fast, and it's very easy to use.

How to cite
===========================

If you use metapredict for your work, please cite the metapredict paper: 

Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophys. J. 120, 4312–4319 (2021).

Note that in addition to the `original paper <https://www.cell.com/biophysj/fulltext/S0006-3495(21>`_\ 00725-6), there's a `V2 preprint <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_\ ; HOWEVER, we ask you only cite the original paper and describe the version being used (V1, V2, V2-FF, or V3).

We are hoping to get a paper out for V3 in the near future (we will update this section once the V3 paper is available)...



Known installation issues
====================================

Below we include documentation on known issues. 

macOS libiomp clash 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

To avoid this error we make the executive decision to ignore this clash. This has largely not appeared to have any deleterious issues on performance or accuracy across the tests run. If you are uncomfortable with this then the code in ``metapredict/__init__.py`` can be edited with ``IGNORE_LIBOMP_ERROR`` set to ``False`` and **metapredict** re-installed from the source directory.

Testing
========

To see if your installation of **metapredict** is working properly, you can run the unit test included in the package by navigating to the metapredict/tests folder within the installation directory and running:

.. code-block:: bash

	$ pytest -v

Example datasets
==================

Example data that can be used with metapredict can be found in the metapredict/data folder on GitHub. The example data set is just a .fasta file containing 5 protein sequences.


Previous updates
==================

May 2023: Update to default version (metapredict V2-FF)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As of May 2023, we have pushed our improved version metapredict V2-FF. metapredict V2-FF does not change any of the predictions, but does implement substantial performance improvements. Notably these are realized by using the :code:`predict_disorder_batch()` function. 

February 2022: Update to default version (metapredict V2)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As of February 15, 2022 we have updated metapredict to V2. This comes with important changes that improve the accuracy of metapredict. Please see the section on the update *Major update to metapredict predictions to increase overall accuracy* below. In addition, this update changes the functionality of the *predict_disorder_domains()* function, so please read the documentation on that function if you were using it previously. 

These changes are detailed in a `permanent preprint <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_ that lives on bioRxiv. We ask you still cite the original metapredict article rather than this preprint.

July 2021: Initial version (metapredict v1)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The initial version of metapredict was released in July 2021 with the corresponding paper published shortly thereafter in Biophysical Journal:

Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophys. J. 120, 4312–4319 (2021).