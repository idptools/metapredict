**********************************
metapredict from the command-line
**********************************


A quick note on selecting the metapredict network
======================================================

Over three iterations we have updated the network behind metapredict to improve prediction accuracy. In case you were using a specific version for something or prefer one version over another, we implemented our updates such that all networks generated previously are still available. You can specify any of the metapredict disorder prediction networks by using the ``-v`` or ``--version`` flag and choosing 1, 2, or 3!


Predicting Disorder Scores from FASTA Files
==============================================

The ``metapredict-predict-disorder`` command-line tool processes a ``.fasta`` file as input and generates disorder scores for each sequence in the file. The results are saved to a ``.csv`` file for further analysis.

Once ``metapredict`` is installed, you can run ``metapredict-predict-disorder`` from the command line:

.. code-block:: bash
	
	$ metapredict-predict-disorder <Path to .fasta file> 

Example of usage:
^^^^^^^^^^^^^^^^^^
.. code-block:: bash

    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta

By default, the results are saved to a ``disorder_scores.csv`` file in the current working directory. Additionally, a progress bar is displayed, and predictions will automatically use a GPU if one is available.

Note that as of metapredict V3, all three networks can be submitted in batch for massive increases in prediction speed. Further, metapredict will automatically use a CUDA GPU if available. A progress bar will also be generated in the terminal.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying Output Location
----------------------------

Use the ``-o`` or ``--output-file`` flag to specify the desired output file path and name. By default, the output is saved as ``disorder_scores.csv`` in the current directory.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv

Selecting a Specific Version of ``metapredict``
-------------------------------------------------

To use a specific version (e.g., V1 or V2) of ``metapredict``, use the ``-v`` or ``--version`` flag. This allows you to run predictions using previous network versions for compatibility.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -v 1


Specifying the Device for Prediction
-------------------------------------

You can manually specify the device for prediction with the ``-d`` or ``--device`` flag. Available options are ``cpu``, ``mps`` (for Apple Silicon), ``cuda`` (for GPUs), or ``cuda:int`` to specify a specific GPU by its index.

By default, ``metapredict`` will use a CUDA-enabled GPU if available, otherwise it defaults to the CPU.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder interestingProteins.fasta -d cuda:0

Silencing Output
-----------------

To suppress output and the progress bar, use the ``-s`` or ``--silent`` flag. This option is useful when running predictions in scripts where minimal output is preferred.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder interestingProteins.fasta -s


Additional Notes
----------------

1. **Error Handling**: If the input file is missing or invalid, an error message will be displayed, and the script will terminate.
2. **Relative vs Absolute Paths**: You can provide either relative or absolute paths for both input and output files. If the specified output directory doesn't exist, you may encounter an error, so ensure the directory is created beforehand.


Predicting IDRs from a fasta file
===================================

The ``metapredict-predict-idrs`` command from the command line takes a .fasta file as input and returns a .fasta file containing the IDRs for every sequence from the input .fasta file. 

The ``metapredict-predict-disorder`` command-line tool processes a ``.fasta`` file as input and returns a ``.fasta`` file containing the IDRs for every sequence from the input file.

.. code-block:: bash

	$ metapredict-predict-idrs <Path to .fasta file> 

Example of usage:
^^^^^^^^^^^^^^^^^^

.. code-block:: bash
	
	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta 

As of metapredict V3, you can automatically parallelize any metapredict network on a GPU or CPU if available.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying Output Location
----------------------------

If you would like to specify where to save the output, simply use the ``-o`` or ``--output-file`` flag and then specify the file path and file name. By default, the file will be saved as ``idrs.fasta`` (if using --mode fasta) or ``shephard_idrs.tsv`` for the ``shephard-domains``, ``shephard-domains-uniprot`` modes.

**Example**

.. code-block:: bash
	
	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_idrs.fasta

Selecting a Specific Version of ``metapredict``
-------------------------------------------------
If you want to use a version of metapredict other than the default (V3), you can specify the version by using the ``-v`` or ``--version`` flag and choosing 1, 2, or 3!

**Example**

.. code-block:: bash
	
	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -v 2


Selecting Prediction Output Mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``--mode`` flag to define how IDRs are reported. Available options are:
- ``fasta``: Outputs a FASTA file with IDR start and end positions added to the header.
- ``shephard-domains``: Generates a SHEPHARD-compliant domains file with 1-based indexing.
- ``shephard-domains-uniprot``: Extracts the UniProt ID from the header and generates a SHEPHARD-compliant domains file.

By default, predictions are reported in ``fasta`` mode.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta --mode shephard-domains

Adjusting Disorder Threshold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--threshold`` flag allows you to specify a custom disorder threshold. By default, the threshold is 0.42 for version 1 and 0.5 for versions 2 and 3.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta --threshold 0.45

Specifying the Device for Prediction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``-d`` or ``--device`` flag to choose the device for prediction. Available options include ``cpu``, ``mps`` (for Apple Silicon), ``cuda`` (for GPUs), or ``cuda:int`` to specify a specific GPU by its index.

By default, ``metapredict-predict-idrs`` will use a CUDA-enabled GPU if available, otherwise it defaults to the CPU.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs interestingProteins.fasta -d cuda:0



Predicting disorder scores from sequence
=========================================

The ``metapredict-quick-predict`` command-line tool allows you to input an amino acid sequence directly via the command line and receive the disorder prediction values. It provides a fast way to predict intrinsic disorder for short sequences without the need for a FASTA file.

**Example:**

.. code-block:: bash

    $ metapredict-quick-predict <Amino Acid Sequence>

Example of usage:
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ metapredict-quick-predict MVKVGVNGFGRIGRLVTRAAFNSGKVDIVLDSGDGVTHVVQ

Specifying the metapredict network
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To use a specific version (e.g., V1, V2, or V3) of ``metapredict``, use the ``-v`` or ``--version`` flag. This allows you to run the disorder prediction with different versions of the model.

**Example**:

.. code-block:: bash

    $ metapredict-quick-predict MVKVGVNGFGRIGRLVTRAAFNSGKVDIVLDSGDGVTHVVQ -v 2


Predicting AlphaFold2 Confidence Scores from a FASTA File
==========================================================

The ``metapredict-predict-pLDDT`` command-line tool allows you to generate AlphaFold2 pLDDTscores for sequences in a FASTA file.

.. code-block:: bash

    $ metapredict-predict-pLDDT <FASTA File>

Example of usage:
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta

By default, the script will generate a CSV file called ``pLDDT_scores.csv`` with pLDDT scores for each sequence in the input FASTA file.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying an Output File
--------------------------
To specify a custom output file where the pLDDT scores should be saved, use the ``-o`` or ``--output-file`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta -o my_plddt_scores.csv

Specifying a Specific Version of the pLDDT predictor
-----------------------------------------------------
To use a specific version of the pLDDT model (e.g., V1, V2), use the ``-v`` or ``--pLDDT-version`` flag. This allows you to specify which version of the model to use for generating the pLDDT scores.

**Example**:

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta -v 1

Suppressing the Progress Bar
-----------------------------
If you want to suppress the progress bar, use the ``-s`` or ``--silent`` flag. This is useful if you want a cleaner output without the progress bar display.

**Example**:

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta -s

Specifying the Device
---------------------
To specify the device to run the prediction on (CPU, MPS, CUDA), use the ``-d`` or ``--device`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta -d cuda:0

Generate Disorder Plots from FASTA files
=========================================

The ``metapredict-graph-disorder`` command from the command line takes a ``.fasta`` file as input and returns a graph for every sequence within the .fasta file. **Warning** This will return a graph for every sequence in the FASTA file.  

.. code-block:: bash

    $ metapredict-graph-disorder <FASTA File>

Example of usage:
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta

**NOTE**: If no output directory is specified, this function will make an output directory in the current working directory called ``disorder_out/``. This directory will hold all generated graphs.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying an Output Directory
------------------------------
To specify a custom directory for the generated graphs, use the ``-o`` or ``--output-directory`` flag. If not provided, the output graphs will be saved in a default directory called ``disorder_out``.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta -o custom_output_dir

Specifying a Specific Version of ``metapredict``
------------------------------------------------
You can specify a specific version of the metapredict model (e.g., 1, 2, 3) by using the ``-v`` or ``--version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta -v 2


Including Predicted AlphaFold2 pLDDT Scores in the Graph
-----------------------------------------------------------
To include AlphaFold2 pLDDT scores in the graph, use the ``-p`` or ``--pLDDT`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta -p

Specifying a pLDDT Version
---------------------------
To specify which version of the pLDDT predictor to use (V1 or V2), use the ``-pv`` or ``--pLDDT_version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta -pv 2

Setting the DPI for Graph Resolution
--------------------------------------
You can adjust the resolution of the generated graphs by setting the DPI (dots per inch) using the ``-D`` or ``--dpi`` flag. The default DPI is 150.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta -D 300


Setting the Output Filetype
---------------------------
The output filetype can be specified using the ``--filetype`` flag. The valid options are ``png``, ``pdf``, and ``jpg``, with ``png`` as the default.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta --filetype pdf


Indexing Filenames
------------------
If you want the generated graph files to have indexed filenames (e.g., ``1_filename.png``), use the ``--indexed-filenames`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder input_sequences.fasta --indexed-filenames

Setting the Disorder Threshold Line
------------------------------------

If you would like to change the disorder threshold line plotted on the graph, use the ``--disorder-threshold`` flag followed by some value between 0 and 1. Default is 0.42 for V1 and 0.5 for V2 and V3.

**Example**

.. code-block:: bash

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --disorder-threshold 0.5



Quick Disorder Graph for a Sequence
===================================

The ``metapredict-quick-graph`` command-line tool allows you to quickly visualize the intrinsic disorder of a single amino acid sequence directly from the command line. This tool can also optionally include AlphaFold2 pLDDT (predicted Local Distance Difference Test) scores in the generated graph.

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph <Amino Acid Sequence>


Example of usage:
^^^^^^^^^^^^^^^^^^

To visualize the disorder profile of the sequence ``THISISASEQWENCE``, you would run:

.. code-block:: bash

    $ metapredict-quick-graph THISISASEQWENCE

This will generate a disorder graph for the sequence and display it.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying a Specific Version of ``metapredict``
------------------------------------------------
You can specify a specific version of the metapredict model (e.g., V1, V2, or V3) by using the ``-v`` or ``--version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-quick-graph THISISASEQWENCE -v 2

Including AlphaFold2 pLDDT Scores in the Graph
------------------------------------------------
To include AlphaFold2 pLDDT scores in the graph, use the ``-p`` or ``--pLDDT`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-quick-graph THISISASEQWENCE -p

Setting the DPI for Graph Resolution
--------------------------------------
You can adjust the resolution of the generated graph by setting the DPI (dots per inch) using the ``-D`` or ``--dpi`` flag. The default DPI is 150.

**Example**:

.. code-block:: bash

    $ metapredict-quick-graph THISISASEQWENCE -D 300

Specifying a pLDDT Version
---------------------------
To specify which version of the pLDDT predictor to use (V1 or V2), use the ``-pv`` or ``--pLDDT_version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-quick-graph THISISASEQWENCE -pv 2


Graph Disorder from UniProt Accession
=======================================

The ``metapredict-uniprot`` command-line tool allows you to graph the predicted intrinsic disorder of a protein sequence using a UniProt accession number. This tool can also include AlphaFold2 pLDDT (predicted Local Distance Difference Test) scores in the generated graph.

**Example**

.. code-block:: bash

    $ metapredict-uniprot <UniProt Accession>

Example of usage:
^^^^^^^^^^^^^^^^^^

To visualize the disorder profile of a protein with the UniProt accession ``P12345``, you would run:

.. code-block:: bash

    $ metapredict-uniprot P12345

This will generate a disorder graph for the protein sequence associated with the UniProt accession and display it.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying a Specific Version of ``metapredict``
------------------------------------------------
You can specify a specific version of the metapredict model (e.g., V1, V2, or V3) by using the ``-v`` or ``--version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-uniprot P12345 -v 2

Including AlphaFold2 pLDDT Scores in the Graph
------------------------------------------------
To include AlphaFold2 pLDDT scores in the graph, use the ``-p`` or ``--pLDDT`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-uniprot P12345 -p

Setting the DPI for Graph Resolution
--------------------------------------
You can adjust the resolution of the generated graph by setting the DPI (dots per inch) using the ``-D`` or ``--dpi`` flag. The default DPI is 150.

**Example**:

.. code-block:: bash

    $ metapredict-uniprot P12345 -D 300

Specifying a pLDDT Version
---------------------------
To specify which version of the pLDDT predictor to use (V1 or V2), use the ``-pv`` or ``--pLDDT_version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-uniprot P12345 -pv 1

Providing a Custom Title for the Graph
---------------------------------------
You can provide a custom title for the graph using the ``-t`` or ``--title`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-uniprot P12345 -t "Disorder Prediction for Protein X"

Saving the Graph to a File
--------------------------
You can specify the output file where the graph will be saved using the ``-o`` or ``--output-file`` flag. The file extension (e.g., pdf, png, jpg) determines the file format. If no filename is provided, the output will be saved using the UniProt accession ID as the filename.

**Example**:

To save the graph as a PNG file:

.. code-block:: bash

    $ metapredict-uniprot P12345 -o disorder_graph.png

If no output filename is provided, the graph will be saved with the UniProt accession number as the filename (e.g., ``P12345.png``).

Suppressing the Printed Output
-------------------------------
If you prefer to suppress any printed output, specifically when saving the generated graph, use the ``-s`` or ``--silent`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-uniprot P12345 -o disorder_graph.png -s



Graph Disorder from Protein Name
===================================

The ``metapredict-name`` command-line tool allows you to predict the intrinsic disorder of a protein sequence using a protein name (and ideally also the organism name...). This tool can also include AlphaFold2 pLDDT (predicted Local Distance Difference Test) scores in the generated graph.

*Example*

.. code-block:: bash
    
    $ metapredict-name <Protein Name> 

Example of usage:
^^^^^^^^^^^^^^^^^^

To visualize the disorder profile of a protein named ``p53``, you would run:

.. code-block:: bash

    $ metapredict-name p53

This will generate a disorder graph for the protein sequence associated with the provided name.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying a Specific Version of ``metapredict``
------------------------------------------------
You can specify a specific version of the metapredict model (e.g., V1, V2, or V3) by using the ``-v`` or ``--version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-name P53 -v 2

Including AlphaFold2 pLDDT Scores in the Graph
------------------------------------------------
To include AlphaFold2 pLDDT scores in the graph, use the ``-p`` or ``--pLDDT`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-name P53 -p

Setting the DPI for Graph Resolution
--------------------------------------
You can adjust the resolution of the generated graph by setting the DPI (dots per inch) using the ``-D`` or ``--dpi`` flag. The default DPI is 150.

**Example**:

.. code-block:: bash

    $ metapredict-name P53 -D 300

Specifying a pLDDT Version
---------------------------
To specify which version of the pLDDT predictor to use (V1 or V2), use the ``-pv`` or ``--pLDDT_version`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-name P53 -pv 2

Providing a Custom Title for the Graph
--------------------------------------
You can provide a custom title for the graph using the ``-t`` or ``--title`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-name P53 -t "Disorder Prediction for P53"

Suppressing Terminal Output
---------------------------
If you prefer to suppress all printed text during execution, use the ``-s`` or ``--silent`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-name P53 -s


Generate AlphaFold2 pLDDT Score Figures from FASTA
===================================================

The ``metapredict-graph-pLDDT`` command-line tool generates AlphaFold2 pLDDT score figures for all sequences in a FASTA file. 

**Example**

.. code-block:: bash

    $ metapredict-graph-pLDDT <FASTA file path>

Example of usage:
^^^^^^^^^^^^^^^^^^

To visualize the pLDDT scores for all sequences in a FASTA file named ``proteins.fasta``, you would run:

.. code-block:: bash

    $ metapredict-graph-pLDDT proteins.fasta

This will generate pLDDT score graphs for each sequence in the provided FASTA file.

Additional Usage
~~~~~~~~~~~~~~~~~

Setting the DPI for Graph Resolution
--------------------------------------
You can adjust the resolution of the generated graphs by setting the DPI (dots per inch) using the ``-D`` or ``--dpi`` flag. The default DPI is 150.

**Example**:

.. code-block:: bash

    $ metapredict-graph-pLDDT proteins.fasta -D 300

Specifying the Output Filetype
------------------------------
You can specify the output filetype (e.g., PNG, PDF, JPG) for the generated graphs using the ``--filetype`` flag. The default filetype is PNG.

**Example**:

.. code-block:: bash

    $ metapredict-graph-pLDDT proteins.fasta --filetype pdf

Defining the Output Directory
-----------------------------
You can define a custom output directory using the ``-o`` or ``--output-directory`` flag. If not provided, the tool will save the graphs to a default directory named ``pLDDT_out``.

**Example**:

.. code-block:: bash

    $ metapredict-graph-pLDDT proteins.fasta -o custom_output_dir

Indexing Output Filenames
--------------------------
To index the output filenames with a leading unique integer, use the ``--indexed-filenames`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-graph-pLDDT proteins.fasta --indexed-filenames



Specifying the pLDDT Version
-----------------------------
You can specify which version of the pLDDT predictor to use (V1, V2, or V3) with the ``-v`` or ``--pLDDT-version`` flag. The default version is determined by the ``DEFAULT_NETWORK_PLDDT`` setting.

**Example**:

.. code-block:: bash

    $ metapredict-graph-pLDDT proteins.fasta -v V2


Generate Disorder Scores for CAID from a FASTA file
====================================================

The ``metapredict-caid`` allows you to easily run predictions of .fasta formatted files and returns a 'CAID compliant' formatted file per sequence that is in the fasta file.

**Example**:

.. code-block:: bash

    $ metapredict-caid <FASTA file path> <output path> <version>

Example of usage:
^^^^^^^^^^^^^^^^^^

To generate disorder scores for all sequences in a FASTA file named ``proteins.fasta`` and save the output to the directory ``output/``, using version ``v2`` of Metapredict, you would run:

.. code-block:: bash

    $ metapredict-caid proteins.fasta output/ v2

This will generate `.caid` files with the disorder scores for each sequence in the specified output directory.

Additional information
~~~~~~~~~~~~~~~~~~~~~~

FASTA Input File
----------------
The first argument is the path to the FASTA file containing the protein sequences for which disorder scores will be predicted.

**Example**:

.. code-block:: bash

    $ metapredict-caid proteins.fasta output/ v2

Output Directory
----------------
The second argument specifies the directory where the generated `.caid` files will be saved. If the directory does not exist, it will be created.

**Example**:

.. code-block:: bash

    $ metapredict-caid proteins.fasta output/ v2

Version
-------
The third argument specifies the version of Metapredict to use. The options are:
- ``v1``
- ``v2``
- ``v3``

**Example**:

.. code-block:: bash

    $ metapredict-caid proteins.fasta output/ v3


