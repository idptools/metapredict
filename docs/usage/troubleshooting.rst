HELP! Metapredict isn't working!
=================================

Python Version Issues
----------------------

We have received occasional feedback that metapredict is not working for a user. A common problem is that the user is using a different version of Python than metapredict was made on. 

metapredict requires Python 3.9 or later, and is tested on 3.9, 3.10, 3.11, 3.12, 3.13, and 3.14. metapredict was developed for macOS and Linux, but our automated tests now run on Linux, macOS, and Windows for every supported Python version, and we provide prebuilt wheels for all three.

If you commonly use a Python version outside of the 3.9 - 3.14 window, a convenient workaround is to use a conda environment that has Python 3.11 set as the default version of Python. For more info on conda, please see https://docs.conda.io/projects/conda/en/latest/index.html

Once you have conda installed, simply use the command 

.. code-block:: bash

	conda create --name my_env python=3.11
	conda activate my_env

and once activated install metapredict from PyPI

.. code-block:: bash

	pip install metapredict

You can, then use metapredict from within this conda environment. In all our testing, this setup leads to a working version of metapredict. However, in principle, metapredict should work automatically when installed from pip.

Running tests
----------------------
If you would like to check if metapredict is working, you can also run the test suite found in the source directory (``metapredict/tests``). The tests load their input files using paths relative to that directory, so you need to run them from inside it.

To run all tests simply run:

.. code-block:: bash

	pytest --verbose
	
From within the directory. Note you may need to install pytest first:

.. code-block:: bash

	pip install pytest

If you are working from a clone of the GitHub repository, install metapredict from it in editable mode together with its test dependencies (this compiles the Cython extension, so you need a C compiler - see :doc:`../getting_started`), and then run the tests from the ``metapredict/tests`` directory:

.. code-block:: bash

	pip install -e ".[test]"
	cd metapredict/tests
	pytest --verbose

To test metapredict across every supported Python version (3.9 - 3.14), we use `tox <https://tox.wiki/>`_. Each tox environment builds and installs metapredict into a fresh, isolated environment and runs the test suite against that installed copy. You only need pip to install tox: tox installs the ``tox-uv`` plugin it needs itself, and with it `uv <https://docs.astral.sh/uv/>`_, which downloads any Python versions you don't already have. From the root of the repository, run:

.. code-block:: bash

	pip install tox
	tox -m python     # every supported Python version
	tox -e py312      # a single Python version

``README.md`` and ``devtools/README.md`` in the repository explain the testing setup in more detail, including testing on NVIDIA GPUs, testing on Linux from a Mac using Docker, and checking the oldest supported versions of PyTorch and scipy.


Reporting Issues
-----------------

If you are having other problems, please report them to the issues section on the metapredict Github page at
https://github.com/idptools/metapredict/issues
