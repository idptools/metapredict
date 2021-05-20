metapredict from the command-line
==================================

Predicting Disorder
-------------------

The ``metapredict-predict-disorder`` command from the command line takes a .fasta file as input and returns disorder scores for the sequences in the FASTA file.

Once metapredict is installed, the user can run ``metapredict-predict-disorder`` from the command line:

.. code-block:: bash
	
	$ metapredict-predict-disorder <Path to .fasta file> 

**Example:** 

.. code-block:: bash
	
	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta 


**Additional Usage:**

**Save the output -** 
If you would like to save the ouptut, simply use the ``-o`` or ``--output-file`` flag and then specify the file path. By default this will save the output file as disorder.csv. However, you can specify the file name in the output path.

**Example:** 

.. code-block:: bash
    
    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv


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
By default the graphs will save as .png files. However, you can specify the file type by calling ``--filetype`` and then specifying the file type. Any matplotlib compatible file extension should work (for example, pdf).

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

``metapredict-uniprot`` is a command that will let you input any Uniprot ID and get a plot of the disorder for the corresponding protein. The default behavior is to have a plot automatically appear. Apart from the Uniprot ID which is required for this command, the command has four possible additional *optional* arguments, 1. DPI can be changed with the ``-D``  or ``--dpi`` flags, default is 150 DPI, 2. Using ``-o``  or ``--ourput-file`` will save the plot to a specified directory (default is current directory) - filenames and file extensions (pdf, jpg, png, etc) can be specified here. If there is no file name specified, it will save as the Uniprot ID and as a .png, 3. ``-t``  or ``--title`` will let you specify the title of the plot. By defualt the title will be *Disorder for* followed by the Uniprot ID.

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



