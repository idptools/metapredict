metapredict from the command-line
==================================

Predicting Disorder
-------------------

``metapredict-predict-disorder`` is a command that takes a .fasta file as input and returns a .csv file where the first cell in each row is the uniprot header and all subsequent cells in that row are predicted consensus disorder values for each residue in the amino acid sequence associated with the fasta header. 

Once metapredict is installed, the user can run ``metapredict-predict-disorder`` from the command line:

.. code-block:: bash
	
	$ metapredict-predict-disorder <Path to .fasta file> <Path where to save the output> <Output file name> <flags>

This will save a .csv file to the location specified by <Path where to save the output>. The name specified in <Output file name> will be the name of the output file followed by .csv. The .csv extension is automatically added to the output file name.

**Example:** 

.. code-block:: bash
	
	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions

If the output path is not specified, output will save to the current directroy.

**Additional Usage:**

**Get raw prediction values**
``--no_normalization``

By default, the output prediction values are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 and slightly greater than 1. The negative values are replaced with 0 and the values greater than 1 are replaced with 1 by default. However, if you want raw values, simply add the flag ``--no_normalization``.

**Example:**

.. code-block:: bash
	
	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions --no_normalization

Quick Predictions
------------------

``metapredict-quick-predict`` is a command that will let you input a sequence and get disorder values immediately printed to the terminal. The only argument that can be input is the sequence.

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-predict ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN

Graphing Disorder
-------------------

The ``metapredict-graph-disorder`` command from the command line takes a .fasta file as input and returns a graph for every sequence within the .fasta file. **Warning** This will return a graph for every sequence in the FASTA file. These graphs will have to be closed sequentially. Therefore, it is not recommended to use this command without specifying an output directory specifying where to save the files. 

.. code-block:: bash

    $ metapredict-graph-disorder <Path to .fasta file> 

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta 

**Additional Usage**

**Saving the output -**
To save the output, simply use the ``-o`` or ``--output-directory`` flag to specify where to save the file.

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/FolderForCoolPredictions


**Changing resolution of saved graphs -**
By default, the output graphs have a DPI of 150. However, the user can change the DPI of the output (higher values have greater resolution but take up more space). To change the DPI simply add the flag ``-D`` or ``--dpi`` followed by the wanted DPI value. 

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ -D 300


**Changing the file type -**
By default the graphs will save as .png files. However, you can specify the file type by calling ``--dpi`` and then specifying the file type. Any matplotlib compatible file extension should work (for example, pdf).

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --filetype pdf

**Indexing file names -**
If you would like to index the file names with a leading unique integer starting at 1, use the ``--indexed-filenames`` flag.

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --indexed-filenames

**Changing the disorder threshhold line on the graph -**
If you would like to change the disorder threshold line plotted on the graph, use the ``--disorder-threshold`` flag followed by some value between 0 and 1. Default is 0.3.

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --disorder-threshold 0.5

Quick Graphing
---------------

``metapredict-quick-graph`` is a command that will let you input a sequence and get a plot of the disorder back immediately. You cannot input fasta files for this command. The command only takes two arguments, 1. the sequence and 2. *which is optional* is the DPI ``-D``  or ``--dpi`` of the ouput graph which defaults to 150 DPI

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN


**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -D 200


Graphing using Uniprot ID
--------------------------

``metapredict-uniprot`` is a command that will let you input any Uniprot ID and get a plot of the disorder for the corresponding protein. The default behavior is to have a plot automatically appear. Apart from the Uniprot ID which is required for this command, the command has four possible additional *optinonal* arguments, 1. DPI can be changed with the ``-D``  or ``--dpi`` flags, default is 150 DPI, 2. Using ``-o``  or ``--ourput-file`` will save the plot to a specified directory (default is current directory). Filenames and file extensions (pdf, jpg, png, etc) can be specified here. If there is no file name specified, it will save as the Uniprot ID and as a .png. 3. ``-t``  or ``--title`` will let you specify the title of the plot. By defualt the title will be *Predicted Consensus Disorder* followed by the Uniprot ID. If you specify the title, the plot will save as your specified title followed by .png rather than save as the Uniprot ID.

**Example:**

.. code-block:: bash
	
	$ metapredict-uniprot Q8RYC8

**Example:**

.. code-block:: bash
	
	$ metapredict-uniprot Q8RYC8 -D 300

**Example:**

.. code-block:: bash
	
	$ metapredict-uniprot Q8RYC8 -o /Users/ThisUser/Desktop/MyFolder/DisorderGraphs

**Example:**

.. code-block:: bash
	
	$ metapredict-uniprot Q8RYC8 -o /Users/ThisUser/Desktop/MyFolder/DisorderGraphs/my_graph.png

**Example:**

.. code-block:: bash
	
	$ metapredict-uniprot Q8RYC8 -t ARF19



