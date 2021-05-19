HELP! Metapredict isn't working!
=================================

Python Version Issues
----------------------

I have recieved occassional feedback that metapredict is not working for a user. A common problem is that the user is using a different version of Python than metapredict was made on. metapredict was made using Python version 3.7, but works on 3.8 as well. I recommend using one of these versions to avoid problems (I haven't done extensive testing using other versions of Python, so if you're not using 3.7 or 3.8, do so at your own risk). A convenient workaround is to use a conda environment that has Python 3.7 set as the default version of Python. For more info on conda, please see https://docs.conda.io/projects/conda/en/latest/index.html

Once you have conda installed, simply use the command 

.. code-block:: bash

	conda create --name my_env python=3.7
	conda activate my_env

and once activate install metapredict from PyPI

.. code-block:: bash

	pip install metapredict


You can, then use metapredict from within this conda environment. In all our testing, this setup leads to a working version of metapredict. However, in principle metapredict should work automatically when installed from pip.

Reporting Issues
-----------------

If you are having other problems, please report them to the issues section on the metapredict Github page at
https://github.com/idptools/metapredict/issues
