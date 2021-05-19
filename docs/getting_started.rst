*********************************
Getting Started with metapredict
*********************************

What is metapredict?
====================
**metapredict** is a bit different than your typical protein disorder predictor. Instead of predicting the percent chance that a residue within a sequence might be disordered, metapredict tries to predict the consensus disorder score for the residue. This is because metapredict was trained on **consensus** values from MobiDB. These values are the percent of other disorders that predicted a residue in a sequence to be disordered. For example, if a residue in a sequence has a value of 1 from the MobiDB consensus values, then *all 8 predictors predicted that residue to be disordered*. If the value was 0.5, than half of the predictors predicted that residue to be disordered. In this way, metapredict can help you quickly determine the likelihood that any given sequence is disordered by giving you an approximations of what other predictors would predict (things got pretty 'meta' there, hence the name metapredict).

Why is metapredict useful?
===========================
A major drawback of consensus disorder databases is that they can only give you values of *previously predicted protein sequencecs*. Therefore, if your sequence of interest is not in their database, tough luck. Fortunately, metapredict gives you a way around this problem!

How was metapredict made?
===========================
**metapredict** uses a bidirectional recurrent neural network trained on the consensus disorder values from 8 disorder predictors from 12 proteomes that were obtained from MobiDB. The creation of metapredict was made possible by IDP-parrot.


Installation
==============
metapredict is available through GitHub or the Python Package Index (PyPI). To install through PyPI, run

.. code-block:: bash

	$ pip install metapredict

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

.. code-block:: bash

	$ git clone https://github.com/idptools/metapredict.git
	$ cd metapredict
	$ pip install .

This will install metapredict locally. If you modify the source code in the local repository, be sure to re-install with pip.

Known installation/execution issues
====================================

Below we include documentation on known issues. 

macOS libiomp clash 
^^^^^^^^^^^^^^^^^^^^^

PyTorch current ships with its own version of the OpenMP library (``libiomp.dylib``). Unfortunately when numpy is installed from ``conda`` (although not from ``pip``) this leads to a collision because the ``conda``-derived numpy library also includes a local copy of the ``libiomp5.dylib`` library. This leads to the following error message (included here for google-ability).

.. code-block:: none 

   OMP: Error #15: Initializing libiomp5.dylib, but found libomp.dylib already initialized.
   OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. 
   That is dangerous, since it can degrade performance or cause incorrect results. The best thing to 
   do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static 
   linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you 
   can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, 
   but that may cause crashes or silently produce incorrect results. For more information, 
   please see http://www.intel.com/software/products/support/.

To avoid this error we make the executive decision to ignore this clash. This has largely not appeared to have any deleterious issues on performance or accuracy accross the tests run. If you are uncomfortable with this then the code in ``metapredict/__init__.py`` can be edited with ``IGNORE_LIBOMP_ERROR`` set to ``False`` and metapredict resinstalled from the source directory.

Testing
========

To see if your installation of metapredict is working properly, you can run the unit test included in the package by navigating to the metapredict/tests folder within the installation directory and running:

.. code-block:: bash

	$ pytest -v

Example datasets
==================

Example data that can be used with metapredict can be found in the metapredict/data folder on GitHub. The example data set is just a .fasta file containing 5 protein sequences.
