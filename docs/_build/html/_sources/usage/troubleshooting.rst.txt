Metapredict isn't working!
===========================

Python Version Issues
----------------------

I have recieved occassional feedback that metapredict is not working for a user. A common problem is that the user is using a different version of Python than metapredict was made on. metapredict was made using Python version 3.7, and I recommend using this version while using metapredict to avoid problems (I haven't done extensive testing using other versions of Python, so if you're not using 3.7, do so at your own risk). A convenient workaround is to use a conda environment that has Python 3.7 set as the default version of Python. For more info on conda, please see https://docs.conda.io/projects/conda/en/latest/index.html

Once you have conda installed, simply use the command 

	conda create --name my_env python=3.7

where you can replace the name of your environment with whatever you'd like. Then, use metapredict from within this conda environment.

Reporting Issues
-----------------

If you are having other problems, please report them to the issues section on the metapredict Github page at
https://github.com/idptools/metapredict/issues