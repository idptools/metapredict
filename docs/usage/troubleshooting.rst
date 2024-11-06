HELP! Metapredict isn't working!
=================================

Python Version Issues
----------------------

We have received occasional feedback that metapredict is not working for a user. A common problem is that the user is using a different version of Python than metapredict was made on. 

metapredict was developed using Python version 3.7, but has been tested on 3.8, 3.9, 3.10, 3.11, and 3.12. However, metapredict was developed for macOS and Linux, and while we expect it to work for Windows this has been far less rigorously tested.

If you commonly use a Python version outside of the 3.7 - 3.12 window, a convenient workaround is to use a conda environment that has Python 3.8 set as the default version of Python. For more info on conda, please see https://docs.conda.io/projects/conda/en/latest/index.html

Once you have conda installed, simply use the command 

.. code-block:: bash

	conda create --name my_env python=3.8
	conda activate my_env

and once activate install metapredict from PyPI

.. code-block:: bash

	pip install metapredict

You can, then use metapredict from within this conda environment. In all our testing, this setup leads to a working version of metapredict. However, in principle, metapredict should work automatically when installed from pip.

Running tests
----------------------
If you would like to check if metapredict is working, you can also run the test suite found in the source directory (`metapredict/tests`).

To run all tests simply run:

.. code-block:: bash

	pytest --versbose
	
From within the directory. Note you may need to install pytest first:

.. code-block:: bash

	pip install pytest


Reporting Issues
-----------------

If you are having other problems, please report them to the issues section on the metapredict Github page at
https://github.com/idptools/metapredict/issues
