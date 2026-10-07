**********************************
metapredict from the command-line
**********************************


A quick note on selecting the metapredict network
======================================================

Over three iterations we have updated the network behind metapredict to improve prediction accuracy. In case you were using a specific version for something or prefer one version over another, we implemented our updates such that all networks generated previously are still available. You can specify any of the metapredict disorder prediction networks by using the ``-v`` or ``--version`` flag and choosing 1, 2, or 3!


A quick note on memory use and batch size
===========================================

The tools that predict scores for a whole FASTA file (``metapredict-predict-disorder``, ``metapredict-predict-idrs``, ``metapredict-predict-pLDDT`` and ``metapredict-caid``) run the sequences through the network in batches. By default they use metapredict's default batch size for the network and device you are using (each tool's ``--help`` lists these defaults), and you can change it with the ``-b`` or ``--batch-size`` option, which takes a power of two of at least 32 (32, 64, 128, 256, 512, 1024, ...). Larger batches are usually faster on a GPU but need more memory; if you run out of memory, use a smaller batch size. To see how much memory a prediction will need, and how that scales with batch size and sequence length, see the :doc:`FAQ <../faq>`.


Running the tools with ``python -m``
======================================

Every command-line tool can also be run as a Python module with ``python -m``, which is handy if the tools aren't on your ``PATH`` or you want to be sure which Python environment is being used. The module name is ``metapredict.scripts.`` followed by the tool name with each ``-`` replaced by ``_``. For example, these two commands do the same thing:

.. code-block:: bash

    $ metapredict-predict-disorder interestingProteins.fasta
    $ python -m metapredict.scripts.metapredict_predict_disorder interestingProteins.fasta


Predicting Disorder Scores from FASTA Files
==============================================

The ``metapredict-predict-disorder`` command-line tool processes a ``.fasta`` file as input and generates disorder scores for each sequence in the file. The results are saved to a ``.csv`` file for further analysis. Each row of the file contains the FASTA header (with any commas replaced by spaces), then the amino acid sequence, then one disorder score per residue.

Once ``metapredict`` is installed, you can run ``metapredict-predict-disorder`` from the command line:

.. code-block:: bash
	
	$ metapredict-predict-disorder <Path to .fasta file> 

Example of usage:
^^^^^^^^^^^^^^^^^^
.. code-block:: bash

    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta

By default, the results are saved to a ``disorder_scores.csv`` file in the current working directory. Additionally, a progress bar is displayed, and predictions will automatically use a GPU if one is available.

Note that as of metapredict V3, all three networks can be submitted in batch for massive increases in prediction speed. Further, metapredict will automatically use a GPU if available (a CUDA GPU with any network, or Apple Silicon MPS with the default V3 network). A progress bar will also be generated in the terminal.

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

To use a specific version (e.g., V1, V2, or V3) of ``metapredict``, use the ``-v`` or ``--version`` flag. This allows you to run predictions using previous network versions for compatibility.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -v 1


Specifying the Device for Prediction
-------------------------------------

You can manually specify the device for prediction with the ``-d`` or ``--device`` flag. Available options are ``cpu``, ``mps`` (for Apple Silicon), ``cuda`` (for GPUs), or ``cuda:int`` to specify a specific GPU by its index. A bare index such as ``0`` is treated the same as ``cuda:0``.

By default, ``metapredict`` automatically selects a device for you. A CUDA GPU is always used first if one is available. Otherwise, the default V3 network uses Apple Silicon MPS if it is available and the CPU if not, while the smaller V1 and V2 networks use the CPU, because they run faster on the CPU than on MPS. If you ask for a device that isn't available (for example ``-d cuda`` on a machine without a CUDA GPU), metapredict stops with an error rather than falling back to the CPU.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder interestingProteins.fasta -d cuda:0

Setting the Batch Size
----------------------

Use the ``-b`` or ``--batch-size`` flag to set how many sequences are run through the network together. It must be a power of two of at least 32. By default ``metapredict-predict-disorder`` uses metapredict's default for the network and device; running the tool with ``--help`` lists the default batch size for each network on each device (and the :doc:`FAQ <../faq>` explains how batch size affects memory use). Larger batches are usually faster on a GPU but use more memory, so use a smaller batch size if you run out of memory.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder interestingProteins.fasta -b 1024

Silencing Output
-----------------

To suppress output and the progress bar, use the ``-s`` or ``--silent`` flag. This option is useful when running predictions in scripts where minimal output is preferred.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder interestingProteins.fasta -s


Additional Notes
----------------

1. **Error Handling**: If the input file is missing or invalid, an error message will be displayed, and the script will terminate. This includes a FASTA file with no sequences in it, or one where ``--invalid-sequence-action`` removes every sequence, either of which stops every tool that reads a FASTA file with an error rather than writing an empty output file.
2. **Relative vs Absolute Paths**: You can provide either relative or absolute paths for both input and output files. If the specified output directory doesn't exist, you may encounter an error, so ensure the directory is created beforehand.


Handling Non-Standard Amino Acids
----------------------------------

Use the ``--invalid-sequence-action`` flag to control how sequences containing non-standard amino acids are handled when the input FASTA file is parsed. The default is ``convert``, which converts non-standard residues to their closest standard amino acid. See the `protfasta documentation <https://protfasta.readthedocs.io/en/latest/read_fasta.html>`__ for the full list of options.

**Example**:

.. code-block:: bash

    $ metapredict-predict-disorder interestingProteins.fasta --invalid-sequence-action convert


Predicting IDRs from a fasta file
===================================

The ``metapredict-predict-idrs`` command from the command line takes a .fasta file as input and returns a .fasta file containing the IDRs for every sequence from the input .fasta file.

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

- ``fasta``: Outputs a FASTA file with IDR start and end positions added to the header (as ``IDR_START=`` and ``IDR_END=``, indexed from 0 as in Python slice notation).
- ``shephard-domains``: Generates a SHEPHARD-compliant domains file with 1-based indexing.
- ``shephard-domains-uniprot``: Extracts the UniProt ID from the header and generates a SHEPHARD-compliant domains file. The UniProt ID is taken to be the text between the first and second ``|`` (as in ``>sp|P04637|P53_HUMAN``), so if any header doesn't contain a ``|`` the tool stops with an error.

By default, predictions are reported in ``fasta`` mode. In every mode, each IDR gets its own entry, so a sequence with several IDRs appears several times and a sequence with no IDRs doesn't appear at all.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta --mode shephard-domains

Adjusting Disorder Threshold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--threshold`` flag allows you to specify a custom disorder threshold. By default, the threshold is 0.42 for version 1 and 0.5 for versions 2 and 3. The threshold must be a number between 0 and 1.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta --threshold 0.45

Specifying the Device for Prediction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``-d`` or ``--device`` flag to choose the device for prediction. Available options include ``cpu``, ``mps`` (for Apple Silicon), ``cuda`` (for GPUs), or ``cuda:int`` to specify a specific GPU by its index. A bare index such as ``0`` is treated the same as ``cuda:0``.

By default, ``metapredict-predict-idrs`` automatically selects a device in the same way as ``metapredict-predict-disorder``: a CUDA GPU is always used first if one is available; otherwise the default V3 network uses Apple Silicon MPS if it is available and the CPU if not, while the V1 and V2 networks use the CPU.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs interestingProteins.fasta -d cuda:0

Setting the Batch Size
~~~~~~~~~~~~~~~~~~~~~~

Use the ``-b`` or ``--batch-size`` flag to set how many sequences are run through the network together. It must be a power of two of at least 32. By default ``metapredict-predict-idrs`` uses metapredict's default for the network and device; running the tool with ``--help`` lists the default batch size for each network on each device (and the :doc:`FAQ <../faq>` explains how batch size affects memory use). Larger batches are usually faster on a GPU but use more memory, so use a smaller batch size if you run out of memory.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs interestingProteins.fasta -b 1024



Handling Non-Standard Amino Acids
----------------------------------

Use the ``--invalid-sequence-action`` flag to control how sequences containing non-standard amino acids are handled when the input FASTA file is parsed. The default is ``convert``, which converts non-standard residues to their closest standard amino acid. See the `protfasta documentation <https://protfasta.readthedocs.io/en/latest/read_fasta.html>`__ for the full list of options.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs interestingProteins.fasta --invalid-sequence-action convert


Printing Status Updates
------------------------

Use the ``--verbose`` flag to print status updates to the terminal as IDRs are predicted.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs interestingProteins.fasta --verbose


Silencing Output
-----------------

To suppress the progress bar and the message saying where the predictions were saved, use the ``-s`` or ``--silent`` flag.

**Example**:

.. code-block:: bash

    $ metapredict-predict-idrs interestingProteins.fasta -s


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

The disorder scores are printed to the terminal as a comma-separated list, with one score per residue.

Specifying the metapredict network
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To use a specific version (e.g., V1, V2, or V3) of ``metapredict``, use the ``-v`` or ``--version`` flag. This allows you to run the disorder prediction with different versions of the model.

**Example**:

.. code-block:: bash

    $ metapredict-quick-predict MVKVGVNGFGRIGRLVTRAAFNSGKVDIVLDSGDGVTHVVQ -v 2


Predicting AlphaFold2 Confidence Scores from a FASTA File
==========================================================

The ``metapredict-predict-pLDDT`` command-line tool allows you to generate AlphaFold2 pLDDT scores for sequences in a FASTA file.

.. code-block:: bash

    $ metapredict-predict-pLDDT <FASTA File>

Example of usage:
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta

By default, the script will generate a CSV file called ``pLDDT_scores.csv`` with pLDDT scores for each sequence in the input FASTA file. Each row contains the FASTA header (with any commas replaced by spaces), then the amino acid sequence, then one pLDDT score per residue.

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
To use a specific version of the pLDDT model (e.g., V1, V2), use the ``-v`` or ``--pLDDT-version`` flag. This allows you to specify which version of the model to use for generating the pLDDT scores. By default, V2 is used.

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
To specify the device to run the prediction on (CPU, MPS, CUDA), use the ``-d`` or ``--device`` flag. As for ``metapredict-predict-disorder``, the options are ``cpu``, ``mps``, ``cuda``, or ``cuda:int`` to specify a specific GPU by its index, and a bare index such as ``0`` is treated the same as ``cuda:0``. By default, a CUDA GPU is used if one is available, then Apple Silicon MPS, then the CPU.

**Example**:

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta -d cuda:0

Setting the Batch Size
----------------------

Use the ``-b`` or ``--batch-size`` flag to set how many sequences are run through the network together. It must be a power of two of at least 32. By default ``metapredict-predict-pLDDT`` uses metapredict's default for the network and device; running the tool with ``--help`` lists the default batch size for each network on each device (and the :doc:`FAQ <../faq>` explains how batch size affects memory use). Larger batches are usually faster on a GPU but use more memory, so use a smaller batch size if you run out of memory.

**Example**:

.. code-block:: bash

    $ metapredict-predict-pLDDT input_sequences.fasta -b 1024

Handling Non-Standard Amino Acids
----------------------------------

Use the ``--invalid-sequence-action`` flag to control how sequences containing non-standard amino acids are handled when the input FASTA file is parsed. The default is ``convert``, which converts non-standard residues to their closest standard amino acid. See the `protfasta documentation <https://protfasta.readthedocs.io/en/latest/read_fasta.html>`__ for the full list of options.

**Example**:

.. code-block:: bash

    $ metapredict-predict-pLDDT interestingProteins.fasta --invalid-sequence-action convert


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

Each graph is named after its FASTA header, with every run of characters other than letters, numbers and underscores replaced by a single ``_`` and the result cut to the first 14 characters (so ``>sp|P0DMV8|HS71A_HUMAN`` is saved as ``sp_P0DMV8_HS71.png``). If two headers give the same name, the later graph overwrites the earlier one, so use ``--indexed-filenames`` (see below) if your headers start the same way.

Additional Usage
~~~~~~~~~~~~~~~~~

Specifying an Output Directory
------------------------------
To specify a custom directory for the generated graphs, use the ``-o`` or ``--output-directory`` flag. If not provided, the output graphs will be saved in a default directory called ``disorder_out``. A directory you pass with ``-o`` must already exist.

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



Handling Non-Standard Amino Acids
----------------------------------

Use the ``--invalid-sequence-action`` flag to control how sequences containing non-standard amino acids are handled when the input FASTA file is parsed. The default is ``convert``, which converts non-standard residues to their closest standard amino acid. See the `protfasta documentation <https://protfasta.readthedocs.io/en/latest/read_fasta.html>`__ for the full list of options.

**Example**:

.. code-block:: bash

    $ metapredict-graph-disorder interestingProteins.fasta --invalid-sequence-action convert


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

This will generate a disorder graph for the protein sequence associated with the UniProt accession and display it. You can also give the accession of a specific isoform, such as ``P04637-2``.

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
You can provide a custom title for the graph using the ``-t`` or ``--title`` flag. By default, the title is ``Disorder for`` followed by the accession.

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

If you use ``-o`` without a filename, the graph will be saved with the UniProt accession number as the filename (e.g., ``P12345.png``). In that case, put ``-o`` after the accession, otherwise ``-o`` takes the accession as its filename. Without ``-o``, the graph is displayed rather than saved.

.. code-block:: bash

    $ metapredict-uniprot P12345 -o

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

If the name is more than one word, just type the words one after the other. This is also how you add the organism name, which we recommend, because a protein name on its own can match the same protein from a different organism. Unless you use ``-s``, metapredict prints the UniProt entry it found so you can check it's the one you wanted.

.. code-block:: bash

    $ metapredict-name p53 human

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
You can provide a custom title for the graph using the ``-t`` or ``--title`` flag. By default, the title is the name you searched for.

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

This will generate pLDDT score graphs for each sequence in the provided FASTA file. The graphs are named after the FASTA headers in the same way as for ``metapredict-graph-disorder``.

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
You can define a custom output directory using the ``-o`` or ``--output-directory`` flag. If not provided, the tool will save the graphs to a default directory named ``pLDDT_out``. A directory you pass with ``-o`` must already exist.

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
You can specify which version of the pLDDT predictor to use (V1 or V2) with the ``-v`` or ``--pLDDT-version`` flag. The default version is determined by the ``DEFAULT_NETWORK_PLDDT`` setting (currently V2).

**Example**:

.. code-block:: bash

    $ metapredict-graph-pLDDT proteins.fasta -v V2


Handling Non-Standard Amino Acids
----------------------------------

Use the ``--invalid-sequence-action`` flag to control how sequences containing non-standard amino acids are handled when the input FASTA file is parsed. The default is ``convert``, which converts non-standard residues to their closest standard amino acid. See the `protfasta documentation <https://protfasta.readthedocs.io/en/latest/read_fasta.html>`__ for the full list of options.

**Example**:

.. code-block:: bash

    $ metapredict-graph-pLDDT interestingProteins.fasta --invalid-sequence-action convert


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

This will generate `.caid` files with the disorder scores for each sequence in the specified output directory. Each ``.caid`` file starts with the sequence's FASTA header, followed by one tab-separated line per residue giving the residue number (starting at 1), the amino acid, the disorder score (to three decimal places), and whether the residue is predicted to be disordered (1) or not (0).

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
The second argument specifies the directory where the generated `.caid` files will be saved. If the directory does not exist, it will be created. Each file is named after the sequence's FASTA header, with any characters that aren't allowed in file names (such as the ``|`` in UniProt headers, or ``/ \ : * ? " < >``) replaced by ``_``, so for example ``>sp|P04637|P53_HUMAN`` is written to ``sp_P04637_P53_HUMAN.caid``. The header inside the file is unchanged. If two headers would give the same file name, metapredict raises an error rather than overwrite one of them.

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

Setting the Batch Size
----------------------

Use the ``-b`` or ``--batch-size`` flag to set how many sequences are run through the network together. It must be a power of two of at least 32. By default ``metapredict-caid`` uses metapredict's default for the network and device; running the tool with ``--help`` lists the default batch size for each network on each device (and the :doc:`FAQ <../faq>` explains how batch size affects memory use). Larger batches are usually faster on a GPU but use more memory, so use a smaller batch size if you run out of memory.

**Example**:

.. code-block:: bash

    $ metapredict-caid proteins.fasta output/ v3 -b 1024

CAID Output Binarization: Algorithmic Domain Assignment
-------------------------------------------------------

By default, ``metapredict-caid`` uses an algorithmic approach to assign binary labels for IDRs and folded domains. Instead of applying a strict per-residue disorder score cutoff, metapredict decomposes each sequence into contiguous intrinsically disordered regions (IDRs) and folded domains using a domain segmentation algorithm. This results in more biologically meaningful domain assignments that better reflect the underlying disorder/folded state segmentation.

If you prefer the legacy strict cutoff-based assignment, you can use the ``--use-fixed-cutoff`` flag to specify a threshold for per-residue binarization. On its own, ``--use-fixed-cutoff`` uses a cutoff of 0.5, or you can give a cutoff between 0 and 1 after the flag. Residues with a disorder score greater than or equal to the cutoff are labeled 1 (disordered) and all others 0. If you use the flag without a value, put it after the three arguments, otherwise ``metapredict-caid`` tries to read the FASTA file name as the cutoff.

**Example**:

.. code-block:: bash

    $ metapredict-caid proteins.fasta output/ v3 --use-fixed-cutoff
    $ metapredict-caid proteins.fasta output/ v3 --use-fixed-cutoff 0.3


