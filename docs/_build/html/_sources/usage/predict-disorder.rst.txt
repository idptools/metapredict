predict-disorder
================

**predicting disorder**
``predict-disorder`` is a commant that takes a .fasta file as input and returns a .csv file containing rows where the first column in the row is the uniprot header and all following rows are predicted disorder values for each residue in the amino acid sequence associated with the fasta header. 
Once metapredict is installed, the user can run ``predict-disorder`` from the command line:

.. code-block:: bash
	
	$ predict-disorder <Path to .fasta file> <Path where to save the output> <Output file name> <flags>

This will save a .csv file to the location specified by <Path where to save the output>. The name specified in <Output file name> will be the name of the output file followed by .csv. The .csv extension is automatically added to the output file name.
**Example:**

.. code-block:: bash
	
	$ predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions

**Additional Usage:**

**Get raw prediction values**

``--no_normalization``
By default, this will output prediction values that are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 and slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. However, if you want raw values, simply add the flag --no_normalization.

**Example:**

.. code-block:: bash
	
	$ predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions --no_normalization
