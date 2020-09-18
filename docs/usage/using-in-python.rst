metapredict in Python
=====================

In addition to using metapredict from the command line, you can also use it directly in Python.

First import metapredict - 

.. code-block:: python

	import metapredict
	from metapredict import meta

Once metapredict is imported, you can work with individual sequences or .fasta files. 

Predicting Disorder
--------------------

The ``predict_disorder`` function will return a list of predicted disorder consensus values for the residues of the input sequence. The input sequence should be a string. Running -

.. code-block:: python
	
	meta.predict_disorder("DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR")

would output -

.. code-block:: python
	
	[1, 1, 1, 1, 1, 1, 1, 0.958249, 0.915786, 0.845275, 0.75202, 0.687313, 0.588148, 0.603413, 0.506673, 0.476576, 0.407988, 0.432979, 0.286987, 0.160754, 0.102596, 0.094578, 0.073396, 0.140863, 0.27831, 0.327464, 0.336405, 0.351597, 0.356424, 0.354656, 0.379971, 0.351955, 0.456596, 0.365483]

**Additional Usage:**

**Disabling prediction value normalization -**
By default, output prediction values are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 or slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. However, the user can get the raw prediction values by specifying *normalized=False* as a second argument in meta.predict_disorder. There is not a very good reason to do this, and it is generally not recommended. However, we wanted to give users the maximum amount of flexibility when using metapredict, so we made it an option.

.. code-block:: python
	
	meta.predict_disorder("DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR", normalized=False)


Graphing Disorder
------------------

The ``graph_disorder`` function will show a plot of the predicted disorder consensus values across the input amino acid sequence. Running - 

.. code-block:: python
	
	meta.graph_disorder("GHPGKQRNPGEHHSSRNVKRNWNNSPSGPNEGRESQEERKTPPRRGGQQSGESHNQDETNKPNPSDNHHEEEKADDNAHRGNDSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLRAKRVLRENFVQCEKAWHRRRLAHPYNRINMQWLDVFDGDCWLAPQLCFGFQFGHDRPVWKIFWYHERGDLRYKLILKDHANVLNKPAHSRNARCESSAPSHDPHGNANSYDKKVTTPDPTEIKSSQESGNSNPDHSPHMPGRDMQEQPGEEPGGHPEKRLIRSKGKTDYKDNRSPRNNPSTDPEWESAHFQWSHDPNEQWLHNLGWPMRWMWQLPNPGIEPFSLNTRKKAPSWINLLYNADPCKTQDDERDCEHHMYQIQPIAPVPKIAMHYCTCFPRVHRIPC")

would output -

.. image:: ../images/meta_predict_disorder.png
  :width: 400

**Additional Usage:**

**Changing title of generated graph -**
There are two parameters that the user can change easily for graph_disorder. The first is the name of the title for the generated graph. The name by default is blank and the title of the graph is simply *Predicted Consensus Disorder*. However, the name can be specified in order to add the name of the protein after the default title. For example, specifing *name* = " - *MadeUpProtein*" would result in a title of *Predicted Consensus Disorder - MadeUpProtein*. Running - 

.. code-block:: python

	meta.graph_disorder("GHPGKQRNPGEHHSSRNVKRNWNNSPSGPNEGRESQEERKTPPRRGGQQSGESHNQDETNKPNPSDNHHEEEKADDNAHRGNDSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLRAKRVLRENFVQCEKAWHRRRLAHPYNRINMQWLDVFDGDCWLAPQLCFGFQFGHDRPVWKIFWYHERGDLRYKLILKDHANVLNKPAHSRNARCESSAPSHDPHGNANSYDKKVTTPDPTEIKSSQESGNSNPDHSPHMPGRDMQEQPGEEPGGHPEKRLIRSKGKTDYKDNRSPRNNPSTDPEWESAHFQWSHDPNEQWLHNLGWPMRWMWQLPNPGIEPFSLNTRKKAPSWINLLYNADPCKTQDDERDCEHHMYQIQPIAPVPKIAMHYCTCFPRVHRIPC", name="- MadeUpProtein")

would output -

.. image:: ../images/python_meta_predict_MadeUpProtein.png
  :width: 400

**Changing the resolution of the generated graph -**
By default, the output graph has a DPI of 150. However, the user can change the DPI of the generated graph (higher values have greater resolution). To do so, simply specify *DPI=Number* where the number is an integer.

**Example:**

.. code-block:: python

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", DPI=300)


Calculating Percent Disorder:
-----------------------------

The ``percent_disorder`` function will return the percent of residues in a sequence that  have predicted consensus disorder values of 50% or more (as a decimal value). Running -

.. code-block:: python

	meta.percent_disorder("DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR")

would output - 

.. code-block:: python

	0.4411764705882353

By default, this uses a cutoff predicted value of equal to or greater than 0.5 for a residue to be considered disordered.

**Additional Usage:**

**Changing the cutoff value -**
If you want to be more strict in what you consider to be disordered for calculating percent disorder of an input sequence, you can simply specify the cutoff value by adding the argument *cutoff=decimal* where the decimal corresponds to the percent you would like to use as the cutoff (for example, 0.8 would be 80%).

**Example:**

.. code-block:: python

	meta.percent_disorder("DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR", cutoff = 0.8)

would output

.. code-block:: python

	0.29411764705882354

The higher the cutoff value, the higher the value any given predicted residue must be greater than or equal to in order to be considered disordered when calculating the final percent disorder for the input sequence.


Predicting Disorder From a .fasta File:
---------------------------------------

By using the ``predict_disorder_fasta`` function, you can predict disorder values for the amino acid sequences in a .fasta file. By default, this function will return a dictionary where the keys in the dictionary are the fasta headers and the values are the consensus disorder predictions of the amino acid sequence associated with each fasta header in the original .fasta file.

**Example:**

.. code-block:: python

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta")

An actual filepath would look something like:

.. code-block:: python

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta")


**Additional Usage:**

**Save the output values -**
By default the predict_disorder_fasta function will immediately return a dictionary. However, you can also save the output to a .csv file by specifying *save=True* and *output_path* ="*location you want to save the file to*". This will save a file called *predicted_disorder_values.csv* to the location you specify for the output_path. The first cell of each row will contain a fasta header and the subsequent cells in that row will contain predicted consensus disorder values for the protein associated with the fasta header.

**Example:**

.. code-block:: python

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta", save=True, output_path="file path where the output .csv should be saved")

An actual filepath would look something like:

.. code-block:: python

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=True, output_path"/Users/thisUser/Desktop/")

**Specifying the name of the output file -**
By default, the generated .csv file will save as *predicted_disorder_values.csv*. However, you can change the default by specifing output_name="file_name".

**Example:**

.. code-block:: python

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta", save=True, output_path="file path where the output .csv should be saved", output_name="name of file")

An actual filepath would look something like:

.. code-block:: python

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=True, output_path="/Users/thisUser/Desktop/", output_name="my_predictions")

Importantly, you do not need to add the .csv file extension to your file name specified in output_name. However, if you do specify .csv as a file extension, everything should still work.

**Get raw prediction values -**
By default, this function will output prediction values that are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 or slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. If you want the raw values simply specify *normalized=False*. There is not a very good reason to do this, and it is generally not recommended. However, we wanted to give users the maximum amount of flexibility when using metapredict, so we made it an option.

**Example:**

.. code-block:: python

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", normalized=False)


Generating Graphs From a .fasta File:
-------------------------------------

By using the ``graph_disorder_fasta`` function, you can graph predicted consensus disorder values for the amino acid sequences in a .fasta file. The *graph_disorder_fasta* function takes a .fasta file as input and returns a .png for every sequence within the .fasta file. The .png files for each sequence will be saved to wherever the user specifies as the output location. Each file will be named as predicted\_disorder\_ followed by the first 10 characters of the .fasta header (which is typically the unique identifier for the protein). For example, a fasta header of >sp|Q8N6T3|ARFG1_HUMAN will return a file saved as *predicted_disorder_sp|Q8N6T3|.png*. Additionally, the title of each graph is automatically generated and will have the title Predicted Consensus Disorder followed by the first 10 characters of the .fasta header. In the previous example, the graph would be titled Predicted Consensus Disorder sp|Q8N6T3|.

**WARNING:**

This command will generate a .png file for **every** sequence in the .fasta file. If you have 1,000 sequences in a .fasta file, it will generate **1,000** files. Therefore, I recommend saving the output to a dedicated folder (or at least not your Desktop...).

**Example:**

.. code-block:: python

	meta.graph_disorder_fasta("file path to .fasta file/fileName.fasta", output_path="file path of where to save output graphs")

An actual filepath would look something like:

.. code-block:: python

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_path="/Users/thisUser/Desktop/folderForGraphs")



**Additional Usage:**

**Changing resolution of saved graphs -**
By default, the output files have a DPI of 150. However, the user can change the DPI of the output files (higher values have greater resolution but take up more space). To change the DPI, specify *DPI=Number* where Number is an integer.

**Example:**

.. code-block:: python

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", DPI=300, output_path="/Users/thisUser/Desktop/folderForGraphs")

**Remove non-alphabetic characters from file names -**
By default, the output files contain characters that are non-alphabetic (for example, *predicted_disorder_sp|Q8N6T3|.png*). This is not a problem on some operating systems, but others do not allow files to have names that contain certain characters. To get around this, you can add an additional argument *remove\_characters=True*. This will remove all non-alphabetic characters from the .fasta header when saving the file. The previous example with the header >sp|Q8N6T3|ARFG1_HUMAN would now save as *predicted_disorder_spQ8N726AR.png*. 

**Example:**

.. code-block:: python

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", DPI=300, output_path="/Users/thisUser/Desktop/folderForGraphs", remove_characters=True)

**Viewing generated graphs without saving -**
The default behavior for the graph_disorder_fasta function is to save the generated graphs for viewing elsewhere. However, the user can choose to view the generated graphs without saving them by specifying *save=False*. 

**WARNING:**

If you choose to view the generated graphs instead of saving them, you can only view one at a time and each graph must be closed before the next will open. This is not a problem if you only have around 10 sequences in your .fasta file. However, if you have 1,000 sequences in a .fasta file, you will have to close out **1,000** graphs. This isn't a problem if you don't mind clicking... a lot.

**Example:**

.. code-block:: python

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=False)
