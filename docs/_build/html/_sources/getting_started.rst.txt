Getting Started with metapredict
================================

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