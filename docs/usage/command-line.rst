metapredict from the command-line
==================================


Using the original metapredict network
---------------------------------------

Over three iterations we have updated the network behind metapredict to improve prediction accuracy. In case you were using a specific version for something or prefer one version over another, we implemented our updates such that all networks generated previously are still available. You can specify any of the metapredict disorder prediction networks by using the ``-v`` or ``--version`` flag and choosing V1, V2, or V3!


Predicting disorder scores from fasta files
--------------------------------------------

The ``metapredict-predict-disorder`` command from the command line takes a .fasta file as input and returns disorder scores for the sequences in the FASTA file.

Once metapredict is installed, you can run ``metapredict-predict-disorder`` from the command line:

.. code-block:: bash
	
	$ metapredict-predict-disorder <Path to .fasta file> 

**Example:** 

.. code-block:: bash
	
	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta 
	

Note that as of metapredict V3, all three networks can be submitted in batch for massive increases in prediction speed. Further, metapredict will automatically use a CUDA GPU if available. A progress bar will also be generated in the terminal.

**Additional Usage:**

**Specifying where to save the output -** 
If you would like to specify where to save the output, simply use the ``-o`` or ``--output-file`` flag and then specify the file path and file name. By default this command will save the output file as disorder_scores.csv to your current working directory. However, you can specify the file name in the output path.

**Example:** 

.. code-block:: bash
    
    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv


**Using the other versions of metapredict -**
To use legacy (V1) or V2 of metapredict, simply use the ``-v`` or ``--version`` flag.

**Example:** 

.. code-block:: bash
    
    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv -v v2


Predicting IDRs from a fasta file
----------------------------------------

The ``metapredict-predict-idrs`` command from the command line takes a .fasta file as input and returns a .fasta file containing the IDRs for every sequence from the input .fasta file. 

.. code-block:: bash

	$ metapredict-predict-idrs <Path to .fasta file> 

**Example**

.. code-block:: bash
	
	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta 

As of metapredict V3, you can automatically parallelize any metapredict network on a GPU or CPU if available.

**Additional Usage**

**specifying where to save the output -** 
If you would like to specify where to save the output, simply use the ``-o`` or ``--output-file`` flag and then specify the file path and file name.

**Example**

.. code-block:: bash
	
	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_idrs.fasta

**Using the an older version of the metapredict predictor**
If you want to use an older version of metapredict, you can specify the version by using the ``-v`` or ``--version`` flag and choosing V1, V2, or V3!

**Example**

.. code-block:: bash
	
	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_idrs.fasta -v v2

**Changing output threshold for disorder-**
To change the cutoff value for something to be considered disordered, simply use the ``--threshold`` flag and then specify your value. For legacy, the default is 0.42. For the newer versions of metapredict, the value is 0.5. 

**Example**

.. code-block:: bash
	
	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_idrs.fasta --threshold 0.3


Predicting disorder scores from sequence
------------------------------------------

``metapredict-quick-predict`` is a command that will let you input a sequence and get disorder values immediately printed to the terminal. The only argument that can be input is the sequence.

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-predict ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN


**Using the original metapredict network-**
To use the original metapredict network, simply use the ``-v`` or ``--version`` flag and specify V1. You can also specify V2 or V3 here.

**Example:** 

.. code-block:: bash
    
    $ metapredict-quick-predict ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVA -v v2


Predicting AlphaFold2 confidence scores from a fasta file
------------------------------------------------------------

The ``metapredict-predict-pLDDT`` command from the command line takes a .fasta file as input and returns predicted AlphaFold2 pLDDT confidence scores for the sequences in the FASTA file.

.. code-block:: bash
	
	$ metapredict-predict-pLDDT <Path to .fasta file>

**Example**

.. code-block:: bash
	
	$ metapredict-predict-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta 

**Additional Usage**

**Specify where to save the output -** 
If you would like to specify where to save the output, simply use the ``-o`` or ``--output-file`` flag and then specify the file path. By default this command will save the output file as pLDDT_scores.csv to your current working directory. However, you can specify the file name in the output path.

**Example**

.. code-block:: bash
	
	$ metapredict-predict-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_pLDDT_predictions.csv


**New: Specify which pLDDT prediction network to use-** 
We now have multiple networks for predicting pLDDT. The original network is ``v1`` and the new network is ``v2``. ``v2`` is the default pLDDT prediction network. To specify a version, use the ``-v`` or ``--pLDDT-version`` flag. 

**Example**

.. code-block:: bash
	
	$ metapredict-predict-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_pLDDT_predictions.csv -v v1

Plotting disorder profiles from a fasta file
-----------------------------------------------

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


**Using a different metapredict network-**
To use the a different metapredict network, simply use the ``-v`` or ``--version`` flag and specify the netowork. You can also specify V2 here. V3 is the default network. 

**Example:** 

.. code-block:: bash
    
    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ -v v1



Quick graphing of disorder scores
-------------------------------------

``metapredict-quick-graph`` is a command that will let you input a sequence and get a plot of the disorder back immediately. You cannot input fasta files for this command. The command only takes three arguments, 1. the sequence 2. *optional* DPI ``-D``  or ``--dpi`` of the output graph which defaults to 150 DPI, and 3. *optional* to include predicted AlphaFold2 confidence scores, use the ``p`` or ``--pLDDT`` flag.

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -p

**Example:**

.. code-block:: bash
	
	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -D 200

**Using the original metapredict network-**
To use the original metapredict network, simply use the ``-v`` or ``--version`` flag and specify V1. You can also specify V2 or V3 here. V3 is default.

**Example:** 

.. code-block:: bash
    
    $ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -v v1


Graphing disorder scores using UniProt ID
---------------------------------------------

``metapredict-uniprot`` is a command that will let you input any UniProt ID and get a plot of the disorder for the corresponding protein. The default behavior is to have a plot automatically appear. Apart from the UniProt ID which is required for this command, the command has four possible additional *optional* arguments, 1. To include predicted AlphaFold2 pLDDT confidence scores, use the ``-p``  or ``--pLDDT`` flag. DPI can be changed with the ``-D``  or ``--dpi`` flags, default is 150 DPI, 3. Using ``-o``  or ``--output-file`` will save the plot to a specified directory (default is current directory) - filenames and file extensions (pdf, jpg, png, etc) can be specified here. If there is no file name specified, it will save as the UniProt ID and as a .png, 4. ``-t``  or ``--title`` will let you specify the title of the plot. By default the title will be *Disorder for* followed by the UniProt ID.

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


**Using the original metapredict network-**
To use the original metapredict network, simply use the ``-v`` or ``--version`` flag and specify V1. You can also specify V2 or V3 here.

**Example:** 

.. code-block:: bash
    
    $ metapredict-uniprot Q8RYC8 -v v1


Graphing disorder using the common name of a protein
-----------------------------------------------------

Sometimes you just don't know the UniProt ID for your favorite protein, and looking it up can be a pain. With the ``metapredict-name`` command, you can input the common name of your favorite protein and get a graph in return. Metapredict will also print the name of the organisms and the UniProt ID it found so you know you're looking at the correct protein. This is because this functionality queries your input protein name on UniProt and takes the top hit. Sometimes this is the protein you're looking for, but not always. To increase the likelihood of success, use your protein name and the organism name for this command.

*Example*

.. code-block:: bash
    
    $ metapredict-name p53 

will graph the metapredict disorder scores for the Homo sapiens p53 protein. This is because Homo sapiens p53 is the top hit on UniProt when you search p53. However...

.. code-block:: bash
    
    $ metapredict-name p53 chicken

will graph the p53 from Gallus gallus!

**Additional Usage**

**Changing the DPI**

Changing the DPI will adjust the resolution of the graph. To change the DPI, use the ``-D`` or ``--dpi`` flag.

**Example**

.. code-block:: bash
    
    $ metapredict-name p53 -D 300


**Graphing predicted pLDDT scores**

To add predicted pLDDT scores to the graph, use the ``-p`` or ``--pLDDT`` flag.

**Example**

.. code-block:: bash
    
    $ metapredict-name p53 -p


**Changing the title**

To change the title, use the ``-t`` or ``--title`` flag.

**Example**

.. code-block:: bash
    
    $ metapredict-name p53 -t my_cool_graph_of_p53


**Using older versions of metapredict**

If you want to use an older version of metapredict, you can specify the version by using the ``-v`` or ``--version`` flag and choosing V1, V2, or V3!

**Example**

.. code-block:: bash
    
    $ metapredict-name p53 -v v2


**Printing the full UniProt ID to your terminal**

To have your terminal print the entire UniProt ID as well as the full protein sequence from your specified protein upon graphing, use the ``-v`` or ``--verbose`` flag.

**Example**

.. code-block:: bash
    
    $ metapredict-name p53 -v


**Turning off all printing to the terminal**

By default, the *metapredict-name* command prints the UniProt ID as well as other information related to your protein to the terminal. The purpose of this is to make it explicitly clear which protein was graphed because grabbing the top hit from UniProt *does not guarantee* that it is the protein you want or expected. However, this behavior can be turned off by using the ``-s`` or ``--silent`` flag.

**Example**

.. code-block:: bash
    
    $ metapredict-name p53 -s



Graphing predicted AlphaFold2 pLDDT scores from a fasta file
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



