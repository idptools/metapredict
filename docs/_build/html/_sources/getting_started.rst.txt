Getting Started with metapredict
================================

What is metapredict?
--------------------
**metapredict** is a bit different than your typical protein disorder predictor. Instead of predicting the percent chance that a residue within a sequence might be disordered, metapredict tries to predict the consensus disorder score for the residue. This is because metapredict was trained on **consensus** values from MobiDB. These values are the percent of other disorders that predicted a residue in a sequence to be disordered. For example, if a residue in a sequence has a value of 1 from the MobiDB consensus values, then *all 8 predictors predicted that residue to be disordered*. If the value was 0.5, than half of the predictors predicted that residue to be disordered. In this way, metapredict can help you quickly determine the likelihood that any given sequence is disordered by giving you an approximations of what other predictors would predict (things got pretty 'meta' there, hence the name metapredict).

Why is metapredict useful?
--------------------------
A major drawback of consensus disorder databases is that they can only give you values of *previously predicted protein sequencecs*. Therefore, if your sequence of interest is not in their database, tough luck. Fortunately, metapredict gives you a way around this problem!

How was metapredict made?
--------------------------
**metapredict** uses a bidirectional recurrent neural network trained on the consensus disorder values from 8 disorder predictors from 12 proteomes that were obtained from MobiDB. The creation of metapredict was made possible by IDP-parrot.


Installation
------------

metapredict is available through GitHub or the Python Package Index (PyPI). To install through PyPI, run

.. code-block:: bash

	$ pip install metapredict

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

.. code-block:: bash

	$ git clone https://github.com/idptools/metapredict.git
	$ cd metapredict
	$ pip install .

This will install metapredict locally. If you modify the source code in the local repository, be sure to reinstall with pip.

Testing
-------

To see if your installation of metapredict is working properly, you can run the unit test included in the package by navigating to the metapredict/tests folder within the installation directory and running:

.. code-block:: bash

	$ pytest -v

Example datasets
----------------

Example data that can be used with metapredict can be found in the metapredict/data folder on GitHub. The example data set is just a .fasta file containing 5 protein sequences.