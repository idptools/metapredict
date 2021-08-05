metapredict from the command-line
==================================

Predicting Disorder from Fasta Files
---------------------------------------

The ``metapredict-predict-disorder`` command from the command line takes a .fasta file as input and returns disorder scores for the sequences in the FASTA file.

Once metapredict is installed, the user can run ``metapredict-predict-disorder`` from the command line:

.. code-block:: bash
	
	$ metapredict-predict-disorder <Path to .fasta file> 

**Example:** 

.. code-block:: bash
	
	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta 


**Additional Usage:**

**Specifying where to save the output -** 
If you would like to specify where to save the ouptut, simply use the ``-o`` or ``--output-file`` flag and then specify the file path and file name. By default this command will save the output file as disorder_scores.csv to your current working directory. However, you can specify the file name in the output path.

**Example:** 

.. code-block:: bash
    
    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv


Predicting Disorder from a Sequence
------------------------------------

``metapredict-quick-predict`` is a command that will let you input a sequence and get disorder values immediately printed to the terminal. The only argument that can be input is the sequence.

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-predict ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN


Predicting AlphaFold2 Confidence Scores from a Fasta File
------------------------------------------------------------

The ``metapredict-predict-pLDDT`` command from the command line takes a .fasta file as input and returns predicted AlphaFold2 pLDDT confidence scores for the sequences in the FASTA file.

.. code-block:: bash
	
	$ metapredict-predict-pLDDT <Path to .fasta file>

**Example**

.. code-block:: bash
	
	$ metapredict-predict-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta 

**Additional Usage**

**Specify where to save the output -** 
If you would like to specify where to save the ouptut, simply use the ``-o`` or ``--output-file`` flag and then specify the file path. By default this command will save the output file as pLDDT_scores.csv to your current working directory. However, you can specify the file name in the output path.

**Example**

.. code-block:: bash
	
	$ metapredict-predict-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_pLDDT_predictions.csv



Graphing Disorder from a Fasta file
------------------------------------

The ``metapredict-graph-disorder`` command from the command line takes a .fasta file as input and returns a graph for every sequence within the .fasta file. **Warning** This will return a graph for every sequence in the FASTA file.  

.. code-block:: bash

    $ metapredict-graph-disorder <Path to .fasta file> 

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta 

If no output directory is specified, this function will make an output directory in the current working directory called *disorder_out*. This directory will hold all generated graphs.

**Additional Usage**


**Adding AlphaFold2 Confidence Scores -**
To add predicted AlphaFold2 pLDDT confidence scores, simply use the ``-p`` or ``--pLDDT`` flag.

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta p


**Specifying where to save the output -**
To specify where to dave the output, simply use the ``-o`` or ``--output-directory`` flag.

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

**Changing the disorder threshold line on the graph -**
If you would like to change the disorder threshold line plotted on the graph, use the ``--disorder-threshold`` flag followed by some value between 0 and 1. Default is 0.3.

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --disorder-threshold 0.5

Quick Graphing
---------------

``metapredict-quick-graph`` is a command that will let you input a sequence and get a plot of the disorder back immediately. You cannot input fasta files for this command. The command only takes three arguments, 1. the sequence 2. *optional* DPI ``-D``  or ``--dpi`` of the ouput graph which defaults to 150 DPI, and 3. *optional* to include predicted AlphaFold2 condience scores, use the ``p`` or ``--pLDDT`` flag.

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -p

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -D 200


Graphing using Uniprot ID
--------------------------

``metapredict-uniprot`` is a command that will let you input any Uniprot ID and get a plot of the disorder for the corresponding protein. The default behavior is to have a plot automatically appear. Apart from the Uniprot ID which is required for this command, the command has four possible additional *optional* arguments, 1. To include predicted AlphaFold2 pLDDT confidence scores, use the ``-p``  or ``--pLDDT`` flag. DPI can be changed with the ``-D``  or ``--dpi`` flags, default is 150 DPI, 3. Using ``-o``  or ``--ourput-file`` will save the plot to a specified directory (default is current directory) - filenames and file extensions (pdf, jpg, png, etc) can be specified here. If there is no file name specified, it will save as the Uniprot ID and as a .png, 4. ``-t``  or ``--title`` will let you specify the title of the plot. By defualt the title will be *Disorder for* followed by the Uniprot ID.

**Example:**

.. code-block:: bash
	
	$ metapredict-uniprot Q8RYC8

**Example:**

.. code-block:: bash
	
	$ metapredict-uniprot Q8RYC8 -p

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



Graphing Predicted AlphaFold2 pLDDT Scores from a fasta file
-------------------------------------------------------------------

The ``metapredict-graph-pLDDT`` command from the command line takes a .fasta file as input and returns a graph of the predicted AlphaFold2 pLDDT confidence score for every sequence within the .fasta file. **Warning** This will return a graph for every sequence in the FASTA file. 

.. code-block:: bash
	
	$ metapredict-graph-pLDDT <Path to .fasta file> 

**Example**

.. code-block:: bash
	
	$ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta 

If no output directory is specified, this function will make an output directory in the current working directory called *pLDDT_out*. This directory will hold all generated graphs.

**Additional Usage**

**Specifying where to save the output -**
To specify where to dave the output, simply use the ``-o`` or ``--output-directory`` flag.

**Example**

.. code-block:: bash
	
	$ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/FolderForCoolPredictions


**Changing resolution of saved graphs -**
By default, the output graphs have a DPI of 150. However, the user can change the DPI of the output (higher values have greater resolution but take up more space). To change the DPI simply add the flag ``-D`` or ``--dpi`` followed by the wanted DPI value. 

**Example**

.. code-block:: bash
	
	$ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/pLDDTGraphsFolder/ -D 300


**Changing the file type -**
By default the graphs will save as .png files. However, you can specify the file type by calling ``--filetype`` and then specifying the file type. Any matplotlib compatible file extension should work (for example, pdf).

**Example**

.. code-block:: bash
	
	$ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/pLDDTGraphsFolder/ --filetype pdf

**Indexing file names -**
If you would like to index the file names with a leading unique integer starting at 1, use the ``--indexed-filenames`` flag.

**Example**

.. code-block:: bash
	
	$ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/pLDDTGraphsFolder/ --indexed-filenames




