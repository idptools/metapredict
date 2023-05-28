*********************************
Getting Started with metapredict
*********************************

What is metapredict?
====================
**metapredict** is a software tool to predict intrinsically disordered regions in protein sequences. It is provided as a downloadable Python tool that includes a Python application programming interface (API) and a set of command-line tools for working with FASTA files. 

Our goal in building **metapredict** was to develop a robust, accurate, and high-performance predictor of intrinsic disorder that is also easy to install and use. As such, **metapredict** is implemented in Python and can be installed directly via `pip` (see below).

metapredict is ALSO available via a `webserver for single sequence prediction <http://https://metapredict.net>`__ and `a Google Colab notebook for batch prediction <https://colab.research.google.com/github/idptools/metapredict/blob/master/colab/metapredict_colab.ipynb>`__. However, this documentation here focuses on the Python package which provides both a set of Python library functions and a set of command-line tools.


metapredict updates and news
===============================
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



Installation
==============
The current stable version of **metapredict** is available through GitHub or the Python Package Index (PyPI). 

To install through PyPI, run:

.. code-block:: bash

	$ pip install metapredict


You can also install the current development version from

.. code-block:: bash

	$ pip install git+https://git@github.com/idptools/parrot


To clone the GitHub repository and gain the ability to modify a local copy of the code, run

.. code-block:: bash

	$ git clone https://github.com/idptools/metapredict.git
	$ cd metapredict
	$ pip install -e .
	
Note you will need the -e flag to ensure the `cython` code compiles correctly, but this also means the installed version is linked to the local version of the code.	

This will install **metapredict** locally. If you modify the source code in the local repository, be sure to re-install with `pip`.


About
======
It's important to understand how tools were built and developed. Below we provide a quick overview of how metapredict works and was trained.

How does metapredict work?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**metapredict V2** (the current default version) works by combining consensus disorder predictions (which is how V1 was developed) with structural predictions to assign a residue as being disordered or folded. 

The original metapredict (V1) was purely a consensus disorder predictor.  Instead of predicting the percent chance that a residue within a sequence might be disordered, **metapredict** tries to predict the *consensus disorder* score for the residue. Consensus disorder reports on the fraction of independent disorder predictors that would predict a given residue as disordered.

As of metapredict V2 (including V2-FF) the overall disorder prediction combines the V1 consensus disorder score with inverted AlphaFold2 predictions in a single deep learning network that provides robust, accurate, and fast assignment of individual residues as being either disordered or folded.

How was metapredict V1 trained?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**metapredict V1** is a deep-learning-based predictor trained on consensus disorder data from 8 different predictors, as pre-computed and provided by `MobiDB <https://mobidb.bio.unipd.it/>`_. Functionally, this means each residue is assigned a score between 0 and 1 which reflects the confidence we have that the residue is disordered (or not). If the score was 0.5, this means half of the predictors predict that residue to be disordered. In this way, **metapredict V1** can determine the likelihood that residues are disordered by giving you an approximation of what other predictors would predict (things got pretty 'meta' there, hence the name **metapredict**).

Note that metapredict V1 predictions are available via the :code:`legacy=True` flag.


How was metapredict V2 trained?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
V2 was trained by generating an initial hybrid score that combined AlphaFold2 predicted pLDDT scores with consensus disorder along with some signal process algorithms to make a new structure/disorder consensus prediction. Finally, we trained a new deep learning network to predict our hybrid network (meta meta), substantially improving accuracy with very little loss in performance.

These changes and new assessment of performance are available in our preprint: `An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure.  <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_ In bioRxiv (p. 2022.06.06.494887). https://doi.org/10.1101/2022.06.06.494887
 

As per the 2023 Critical Assessment of Intrinsic Disorder (CAID) competition, metapredict V2 is ranked the 9th most accurate disorder predictor available. However, importantly, it is among the fastest regardless of accuracy, and is accessible across multiple platforms, via a web server, and with very few software dependencies. Among the top 10, the difference in accuracy is 0.95 to 0.93 AUC, suggesting to us that all top 10 predictors are highly accurate. In short, we believe metapredict V2 hits a sweet spot of accuracy and performance.

How does metapredict V2 differ from V2-FF
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

metapredict V2 and V2-FF are identical in terms of predictions and features, with the major difference being that metapredict V2-FF offers batched predictions. Batched predictions are automatically parallelized on either the CPU or GPU. In addition, we rewrote the metapredict domain decomposition algorithm in C to provide a 10-20x improvement in performance for this step.

We note that V2-FF was released after CAID, so the performance reported there is the V2 network performance. Because metapredict V2-FF is implemented in a `Google Colab notebook for batch prediction <https://colab.research.google.com/github/idptools/metapredict/blob/master/colab/metapredict_colab.ipynb>`__ you don't have to take our word for it that it's fast; just upload a proteome and see for yourself! 


Generating predicted pLDDT (AlphaFold2 confidence) scores in metapredict
-----------------------------------------------------------------------------
In addition to predicting disorder scores, metapredict offers predicted confidence scores from AlphaFold2. These predicted scores use a bidirectional recurrent neural network (BRNN) trained on the per residue pLDDT (predicted IDDT-Ca) confidence scores generated by AlphaFold2 (AF2). The confidence scores (pLDDT) from the proteomes of *Danio rerio*, *Candida albicans*, *Mus musculus*, *Escherichia coli*, *Drosophila melanogaster*, *Methanocaldococcus jannaschii*, *Plasmodium falciparum*, *Mycobacterium tuberculosis*, *Caenorhabditis elegans*, *Dictyostelium discoideum*, *Trypanosoma cruzi*, *Saccharomyces cerevisiae*, *Schizosaccharomyces pombe*, *Rattus norvegicus*, *Homo sapiens*, *Arabidopsis thaliana*, *Zea mays*, *Leishmania infantum*, *Staphylococcus aureus*, *Glycine max*, and *Oryza sativa* were used to generate the BRNN. These confidence scores measure the local confidence that AlphaFold2 has in its predicted structure. The scores go from 0-100 where 0 represents low confidence and 100 represents high confidence. For more information, please see: *Highly accurate protein structure prediction with AlphaFold* https://doi.org/10.1038/s41586-021-03819-2. In describing these scores, the team states that regions with pLDDT scores of less than 50 should not be interpreted except as *possible* disordered regions.


What might the predicted confidence scores from AlphaFold2 be used for?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
These scores can be used for many applications such as generating a quick preview of which regions of your protein of interest AF2 might be able to predict with high confidence, or which regions of your protein *might* be disordered. 

AF2 is not (strictly speaking) a disorder predictor, and the confidence scores are not directly representative of protein disorder. Therefore, any conclusions drawn with regards to disorder from predicted AF2 confidence scores should be interpreted with care, but they may be able to provide an additional metric to assess the likelihood that any given protein region may be disordered.


Why is metapredict useful?
===========================
We think **metapredict** is useful for three main reasons.

1. It's highly accurate, provide strong boundaries between disordered and folded regions.
2. It's incredibly fast; on CPUs one can predict every IDR in the human proteome in ~5 minutes. On modest GPUs one can predict every IDR in the human proteome in 40 seconds. This stands in stark contrast to other predictors which place length caps on sequences and can take hours per sequence.
3. It is easy to use and distributed via a wide range of channels. In addition to this Python package, metapredict is distributed as a stand-alone webserver, colab notebooks for large-scale predictions, and as an `API for SHEPHARD <https://shephard.readthedocs.io/en/latest/apis.html#metapredict>`__, our general-purpose toolkit for working with an annotating large protein datasets. This Python package further implements metapredict as both Python modules and as a set of command-line tools. 

In summary, we believe metapredict provides the three key ingredients of a useful disorder predictor: it's extremely accurate, it's incredibly fast, and it's very easy to use.

How to cite
===========================

If you use metapredict for your work, please cite the metapredict paper 

Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophys. J. 120, 4312–4319 (2021).
	
Additionally, if you are using V2 (which is now the default) please make this clear in methods section. You should not feel obliged to cite the `V2 preprint <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_, and this pre-print exists solely so we could fully document the changes and test some edge cases in an accessible and clear way.



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
