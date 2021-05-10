# metapredict: A machine learning-based tool for predicting protein disorder.

**metapredict** uses a bidirectional recurrent neural network trained on the consensus disorder values from 8 disorder predictors from 12 proteomes that were obtained from [MobiDB](https://mobidb.bio.unipd.it/). The creation of metapredict was made possible by [parrot](https://github.com/idptools/parrot)

## What is metapredict?

**metapredict** is a bit different than your typical protein disorder predictor. Instead of predicting the percent chance that a residue within a sequence might be disordered, metapredict tries to predict the consensus disorder score for the residue. This is because metapredict was trained on **consensus** values from MobiDB. These values are the percent of other disorder predictors that predicted a residue in a sequence to be disordered. For example, if a residue in a sequence has a value of 1 from the MobiDB consensus values, then *all disorder predictors predicted that residue to be disordered*. If the value was 0.5, than half of the predictors predicted that residue to be disordered. In this way, metapredict can help you quickly determine the likelihood that any given sequence is disordered by giving you an approximations of what other predictors would predict (things got pretty 'meta' there, hence the name metapredict).
 
## Why is metapredict useful?

A major drawback of consensus disorder databases is that they can only give you values of *previously predicted protein sequences*. Therefore, if your sequence of interest is not in their database, tough luck. Fortunately, **metapredict** gives you a way around this problem!

For full documentation, please see:
https://metapredict.readthedocs.io/en/latest/getting_started.html

**metapredict** allows for predicting disorder for any amino acid sequence, and predictions can be output as graphs or as raw values. Additionally, metapredict allows for predicting disorder values for protein sequences from .fasta files either directly in Python or from the command-line.

## Installation:

**metapredict** is available through PyPI - to install simply run

	$ pip install metapredict


Alternatively, you can get **metapredict** directly from GitHub. 

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

	$ git clone https://github.com/idptools/metapredict.git
	$ cd metapredict
	$ pip install .

This will install **metapredict** locally.

## Usage:

There are two ways you can use metapredict:
1. Directly from the command-line
2. From within Python

## Using metapredict from the command-line:

### Predicting Disorder
The ``metapredict-predict-disorder`` command from the command line takes a .fasta file as input and returns a .csv file containing rows where the first cell in the row is the fasta header and all subsequent cells in that row are predicted consensus disorder values for each residue in the amino acid sequence associated with the fasta header. 

	$ metapredict-predict-disorder <Path to .fasta file> <Path where to save the output> <Output file name>

This will save a .csv file to the location specified by *Path where to save the output*. The name specified in *Output file name* will be the name of the output file followed by .csv. The .csv extension is automatically added to the output file name.

**Example**

	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions

**Additional Usage**

**Get raw prediction values -**
By default, the output prediction values are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 or slightly greater than 1. The negative values are replaced with 0 and the values greater than 1 are replaced with 1 by default. However, if you want raw values, simply add the flag ``--no_normalization``. There is not a very good reason to do this, and it is generally not recommended. However, I wanted to give users the maximum amount of flexibility when using metapredict, so I made it an option.

**Example**

	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions --no_normalization

**Quick predict**

``metapredict-quick-predict`` is a command that will let you input a sequence and get disorder values immediately printed to the terminal. The only argument that can be input is the sequence.

**Example:**

	$ metapredict-quick-predict ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN


### Graphing Disorder
The ``metapredict-graph-disorder`` command from the command line takes a .fasta file as input and returns a .png for every sequence within the .fasta file. The .png file for each sequence will be saved to wherever the user specifies as the output location. Each file will be named as predicted_disorder_ followed by the first 10 characters of the .fasta header (which is typically the unique identifier for the protein). For example, a fasta header of >sp|Q8N6T3|ARFG1_HUMAN will return a file saved as *predicted_disorder_sp|Q8N6T3|.png*. Additionally, the title of each graph is automatically generated and will have the title Predicted Consensus Disorder followed by the first 10 characters of the .fasta header. In the previous example, the graph would be titled *Predicted Consensus Disorder sp|Q8N6T3|*.

	$ metapredict-graph-disorder <Path to .fasta file> <Path where to save the output>

**Example**

	$ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/

**WARNING -**
This command will generate a .png file for ***every*** sequence in the .fasta file. If you have 1,000 sequences in a .fasta file, it will generate **1,000** files. Therefore, I recommend saving the output to a dedicated folder (or at least not your Desktop...).

**Additional Usage**

**Changing resolution of saved graphs -**
By default, the output graphs have a DPI of 150. However, the user can change the DPI of the output (higher values have greater resolution but take up more space). To change the DPI simply add the flag ``-D`` or ``-dpi`` followed by the wanted DPI value. 

**Example**

	$ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/ -D 300

**Specify the lines across a graph:**
``-lines`` / ``--line_intervals``

By default, the graphs have horizontal dashed lines at intervals of 0.2 from 0 to 1. Now, can specify the location of the dashed lines by using the ``-lines`` / ``--line_intervals`` argument

	$ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/ -lines 0.1 0.2 0.3 0.4 0.5


**Remove non-alphabetic characters from file names -**
By default, the output files contain characters that are non-alphabetic (for example, *predicted_disorder_sp|Q8N6T3|.png*). This is not a problem on some operating systems, but others do not allow files to have names that contain certain characters. To get around this, you can add the ``--remove_characters`` flag. This will remove all non-alphabetic characters from the .fasta header when saving the file. The previous example with the header >sp|Q8N6T3|ARFG1_HUMAN would now save as *predicted_disorder_spQ8N726AR.png*. 

**Example**

	$ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/ --remove_characters

**Quick graph**


``metapredict-quick-graph`` is a command that will let you input a sequence and get a plot of the disorder back immediately. You cannot input fasta files for this command. The command only takes two arguments, 1. the sequence and 2. *which is optional* is the DPI ``-D``  or ``--dpi`` of the ouput graph which defaults to 150 DPI

**Example:**

	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN

**Example:**

	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -D 200


**metapredict-uniprot**

``metapredict-uniprot`` is a command that will let you input any Uniprot ID and get a plot of the disorder for the corresponding protein. The default behavior is to have a plot automatically appear. Apart from the Uniprot ID which is required for this command, the command has four possible additional *optinonal* arguments, 1. DPI can be changed with the ``-D``  or ``--dpi`` flags, default is 150 DPI, 2. DPI ``-s``  or ``--save`` will save the plot. The default behavior *if a file path is not specified using the -p flag* is to save the graph to the current directory. The plot will save as the uniprot ID followed by .png, 3. ``-p``  or ``--path`` will let you specify the path to where to save the plot, and 4. ``-t``  or ``--title`` will let you specify the title of the plot. By defualt the title will be *Predicted Consensus Disorder* followed by the Uniprot ID. If you specify the title, the plot will save as your specified title followed by .png rather than save as the Uniprot ID.

**Example:**

	$ metapredict-uniprot Q8RYC8

**Example:**

	$ metapredict-uniprot Q8RYC8 -D 300

**Example:**

	$ metapredict-uniprot Q8RYC8 -t ARF19

**Example:**

	$ metapredict-uniprot Q8RYC8 -s

**Example:**

	$ metapredict-uniprot Q8RYC8 -s -p /Users/ThisUser/Desktop/MyFolder/DisorderGraphs



## Using metapredict in Python:
In addition to using metapredict from the command line, you can also use metapredict directly in Python.

First import metapredict -
 
	import metapredict
	from metapredict import meta

Once metapredict is imported you can work with individual sequences or .fasta files. 

### Predicting Disorder
The ``predict_disorder`` function will return a list of predicted disorder value for each residue of the input sequence. The input sequence should be a string. Running -

	meta.predict_disorder("DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR")

would output -

	[1, 1, 1, 1, 1, 1, 1, 0.958249, 0.915786, 0.845275, 0.75202, 0.687313, 0.588148, 0.603413, 0.506673, 0.476576, 0.407988, 0.432979, 0.286987, 0.160754, 0.102596, 0.094578, 0.073396, 0.140863, 0.27831, 0.327464, 0.336405, 0.351597, 0.356424, 0.354656, 0.379971, 0.351955, 0.456596, 0.365483]

By default, output prediction values are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 or slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. However, the user can get the raw prediction values by specifying *normalized=False* as a second argument in meta.predict_disorder. There is not a very good reason to do this, and it is generally not recommended. However, we wanted to give users the maximum amount of flexibility when using metapredict, so we made it an option.

	meta.predict_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS", normalized=False)

### Predicting Disorder Domains
The ``predict_disorder_domains`` function takes in an amino acid function and returns a 4-position tuple with: 0. the raw disorder scores from 0 to 1 where 1 is the highest probability that a residue is disordered, 1. the smoothed disorder score used for boundary identification, 2. a list of elements where each element is a list where 0 and 1 define the IDR location and 2 gives the actual sequence, and 3. a list of elements where each element is a list where 0 and 1 define the folded domain location and 2 gives the actual sequence

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHS")

would output - 

	[[0.828, 0.891, 0.885, 0.859, 0.815, 0.795, 0.773, 0.677, 0.66, 0.736, 0.733, 0.708, 0.66, 0.631, 0.601, 0.564, 0.532, 0.508, 0.495, 0.458, 0.383, 0.373, 0.398, 0.36, 0.205, 0.158, 0.135, 0.091, 0.09, 0.102, 0.126, 0.129, 0.114, 0.106, 0.097, 0.085, 0.099, 0.114, 0.093, 0.119, 0.117, 0.043, 0.015, 0.05, 0.139, 0.172, 0.144, 0.121, 0.124, 0.128, 0.147, 0.173, 0.129, 0.152, 0.169, 0.2, 0.172, 0.22, 0.216, 0.25, 0.272, 0.308, 0.248, 0.255, 0.301, 0.274, 0.264, 0.28, 0.25, 0.235, 0.221, 0.211, 0.235, 0.185, 0.14, 0.168, 0.307, 0.509, 0.544, 0.402], array([0.87596856, 0.86139124, 0.84596224, 0.82968293, 0.81255466,
       0.79457882, 0.77575677, 0.75608988, 0.73557951, 0.71422703,
       0.69203382, 0.66900124, 0.63956894, 0.62124099, 0.60188696,
       0.57893168, 0.55241615, 0.52131925, 0.4859528 , 0.44109689,
       0.39353789, 0.35264348, 0.31495776, 0.28      , 0.24661615,
       0.21469814, 0.18500621, 0.15963478, 0.13604845, 0.1172087 ,
       0.10798882, 0.1026882 , 0.09419503, 0.08462484, 0.08256398,
       0.08832671, 0.0908559 , 0.09263851, 0.09438758, 0.09309938,
       0.09102733, 0.09338137, 0.09665342, 0.10073913, 0.10392671,
       0.11010311, 0.11402981, 0.11898634, 0.12430683, 0.13169441,
       0.1381764 , 0.15245093, 0.16746957, 0.17518385, 0.18167578,
       0.18893043, 0.20013416, 0.21581491, 0.23015652, 0.2420559 ,
       0.25209814, 0.25817391, 0.26588944, 0.27456894, 0.27429068,
       0.26411925, 0.24452671, 0.23076894, 0.22834783, 0.21689842,
       0.20887549, 0.20564427, 0.20856996, 0.21901779, 0.23835296,
       0.26794071, 0.30914625, 0.36333478, 0.43187154, 0.51612174]), [[0, 20, 'MKAPSNGFLPSSNEGEKKPI']], [[20, 80, 'NSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHS']]]


**Additional Usage**

**Altering the disorder theshhold -**
To alter the disorder theshhold, simply set *disorder_threshold=my_value* where *my_value* is a float. The higher then treshold value, the more stringent the conservative metapredict will be for designating a region to be considered disordered. Default = 0.42

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", disorder_threshold=0.3)

**Altering minimum IDR size -**
The minimum IDR size will define the smallest possible region that could be considered an IDR. In other words, you will not be able to get back an IDR smaller than the defined size. Default is 12.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_IDR_size = 10)

**Altering the minimum folded domain size -**
The minimum folded domain size defines where we expect the limit of small folded domains to be. *NOTE* this is not a hard limit and functions more to modulate the removal of large gaps. In other words, gaps less than this size are treated less strictly. *Note* that, in addition, gaps < 35 are evaluated with a threshold of 0.35 x disorder_threshold and gaps < 20 are evaluated with a threshold of 0.25 x disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which are IDRs in isolation) often show up with reduced apparent disorder within IDRs, and but can be as short as 20-30 residues. The folded_domain_threshold is used based on the idea that it allows a 'shortest reasonable' folded domain to be identified. Default=50.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_folded_domain = 60)

**Altering gap_closure -**
The gap closure defines the largest gap that would be closed. Gaps here refer to a scenario in which you have two groups of disordered residues seprated by a 'gap' of un-disordered residues. In general large gap sizes will favour larger contigous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps are increasingly rare. Default=10.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", gap_closure = 5)

### Predicting Disorder Domains using a Uniprot ID
In addition to inputting a sequence, you can predict disorder domains by inputting a Uniprot ID by usign the ``predict_disorder_domains_uniprot`` function. This function has the exact same functionality as ``predict_disorder_domains`` except you can now input a Uniprot ID. 

**Example**

    meta.predict_disorder_domains_uniprot('Q8N6T3')


### Graphing Disorder 
The ``graph_disorder`` function will show a plot of the predicted disorder consensus values across the input amino acid sequence.

	meta.graph_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS")

**Additional Usage**

**Changing the title of the generated graph -**
There are two parameters that the user can change for graph_disorder. The first is the name of the title for the generated graph. The name by default is blank and the title of the graph is simply *Predicted Consensus Disorder*. However, the name can be specified in order to add the name of the protein after the default title. For example, specifing name = "- PAB1" would result in a title of *Predicted Consensus Disorder - PAB1*.

**Example**

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", name="Name of this nonexistant protein")

**Changing the resolution of the generated graph -**
By default, the output graph has a DPI of 150. However, the user can change the DPI of the generated graph (higher values have greater resolution). To do so, simply specify *DPI="Number"* where the number is an integer.

**Example**

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", DPI=300)


**Specify the lines across a graph -**
By default, the graphs have horizontal dashed lines at intervals of 0.2 from 0 to 1. Now, can specify the location of the dashed lines by using specifying *line_intervals*

**Example**

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", line_intervals = [0.1, 0.2, 0.3]


### Calculating Percent Disorder
The ``percent_disorder`` function will return the percent of residues in a sequence that  have predicted consensus disorder values of 50% or more (as a decimal value).

**Example**

	meta.percent_disorder("DAPPTSQEHTQAEDKERD")

By default, this function uses a cutoff value of equal to or greater than 0.5 for a residue to be considered disordered.

**Additional Usage**

**Changing the cutoff value -**
If you want to be more strict in what you consider to be disordered for calculating percent disorder of an input sequence, you can simply specify the cutoff value by adding the argument *cutoff=decimal* where the decimal corresponds to the percent you would like to use as the cutoff (for example, 0.8 would be 80%).


**Example**

	meta.percent_disorder("DAPPTSQEHTQAEDKERD", cutoff=0.8)

The higher the cutoff value, the higher the value any given predicted residue must be greater than or equal to in order to be considered disordered when calculating the final percent disorder for the input sequence.


### Predicting Disorder From a .fasta File
By using the ``predict_disorder_fasta`` function, you can predict disorder values for the amino acid sequences in a .fasta file. By default, this function will return a dictionary where the keys in the dictionary are the fasta headers and the values are the consensus disorder predictions of the amino acid sequence associated with each fasta header in the original .fasta file.

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta")


**Additional Usage**

**Save the output values -**
By default the predict_disorder_fasta function will immediately return a dictionary. However, you can also save the output to a .csv file by specifying *save=True* and *output_path = "location you want to save the file to*". This will save a file called *predicted_disorder_values.csv* to the location you specify for the output_path. The first cell of each row will contain a fasta header and the subsequent cells in that row will contain predicted consensus disorder values for the protein associated with the fasta header.

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta", save=True, output_path="file path where the output .csv should be saved")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=True, output_path="/Users/thisUser/Desktop/")

**Specifying the name of the output file -**
By default, the generated .csv file will save as *predicted_disorder_values.csv*. However, you can change the default by specifing *output_name="file_name*".

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta", save=True, output_path="file path where the output .csv should be saved", output_name="name of file")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=True output_path"/Users/thisUser/Desktop/", output_name="my_predictions")

Importantly, you do not need to add the .csv file extension to your file name specified in output_name. However, if you do specify .csv as a file extension, everything should still work.

**Get raw prediction values -**
By default, this function will output prediction values that are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 or slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. If you want the raw values simply specify *normalized=False*. There is not a very good reason to do this, and it is generally not recommended. However, we wanted to give users the maximum amount of flexibility when using metapredict, so we made it an option.

**Example**

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", normalized=False)

### Predict Disorder Using Uniprot ID
By using the ``predict_disorder_uniprot`` function, you can return predicted consensus disorder values for the amino acid sequence of a protein by specifying the Uniprot ID. 

**Example**

    meta.predict_disorder_uniprot("Q8N6T3")


### Generating Graphs From a .fasta File
By using the ``graph_disorder_fasta`` function, you can graph predicted consensus disorder values for the amino acid sequences in a .fasta file. The *graph_disorder_fasta* function takes a .fasta file as input and returns a .png for every sequence within the .fasta file. The .png files for each sequence will be saved to wherever the user specifies as the output location. Each file will be named as predicted_disorder_ followed by the first 10 characters of the .fasta header (which is typically the unique identifier for the protein). For example, a fasta header of >sp|Q8N6T3|ARFG1_HUMAN will return a file saved as *predicted_disorder_sp|Q8N6T3|.png*. Additionally, the title of each graph is automatically generated and will have the title Predicted Consensus Disorder followed by the first 10 characters of the .fasta header. In the previous example, the graph would be titled *Predicted Consensus Disorder sp|Q8N6T3|*.

**WARNING -**
This command will generate a .png file for ***every*** sequence in the .fasta file. If you have 1,000 sequences in a .fasta file, it will generate **1,000** files. Therefore, I recommend saving the output to a dedicated folder (or at least not your Desktop...).

**Example**

	meta.graph_disorder_fasta("file path to .fasta file/fileName.fasta", output_path="file path of where to save output graphs")

An actual filepath would look something like:

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_path="/Users/thisUser/Desktop/folderForGraphs")



**Additional Usage**

**Changing resolution of saved graphs -**
By default, the output files have a DPI of 150. However, the user can change the DPI of the output files (higher values have greater resolution but take up more space). To change the DPI, specify *DPI=Number* where Number is an integer.

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", DPI=300, output_path="/Users/thisUser/Desktop/folderForGraphs")

**Remove non-alphabetic characters from file name -**
By default, the output files contain characters that are non-alphabetic (for example, *predicted_disorder_sp|Q8N6T3|.png*). This is not a problem on some operating systems, while others do not allow files to have names that contain certain characters. To get around this, you can add an additional argument *remove_characters=True*. This will remove all non-alphabetic characters from the .fasta header when saving the file. The previous example with the header >sp|Q8N6T3|ARFG1_HUMAN would now save as *predicted_disorder_spQ8N726AR.png*. 

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", DPI=300, output_path="/Users/thisUser/Desktop/folderForGraphs", remove_characters=True)

**Viewing generated graphs without saving -**
The default behavior for the graph_disorder_fasta function is to save the generated graphs for viewing elsewhere. However, the user can choose to view the generated graphs without saving them by specifying *save=False*. 

**WARNING**
If you choose to view the generated graphs instead of saving them, you can only view one at a time and each must be closed before the next will open. This is not a problem if you only have around 10 sequences in your .fasta file. However, if you have 1,000 sequences in a .fasta file, you will have to close out ***1,000*** graphs. This isn't a problem if you don't mind clicking... a lot.

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=False)


### Generating Graphs Using Uniprot ID
By using the ``graph_disorder_uniprot`` function, you can graph predicted consensus disorder values for the amino acid sequence of a protein by specifying the Uniprot ID. 

**Example**

    meta.graph_disorder_uniprot("Q8N6T3")

This function carries all of the same functionality as ``graph_disorder`` including specifying line intervals, name of the graph, the DPI, and whether or not to save the output.

**Example**

    meta.graph_disorder_uniprot("Q8N6T3", line_intervals=[0.1, 0.2], name="my protein", DPI=300, save=True, output="/Users/thisUser/Desktop")



### metapredict isn't working!
I have recieved occassional feedback that metapredict is not working for a user. A common problem is that the user is using a different version of Python than metapredict was made on. metapredict was made using Python version 3.7, and I recommend using this version while using metapredict to avoid problems (I haven't done extensive testing using other versions of Python, so if you're not using 3.7, do so at your own risk). A convenient workaround is to use a conda environment that has Python 3.7 set as the default version of Python. For more info on conda, please see https://docs.conda.io/projects/conda/en/latest/index.html

Once you have conda installed, simply use the command 

	conda create --name my_env python=3.7

where you can replace the name of your environment with whatever you'd like. Then, use metapredict from within this conda environment.

If you are having other problems, please report them to the **issues** section on the metapredict Github page at
https://github.com/idptools/metapredict/issues


### Recent changes
This section is a log of recent changes with metapredict. My hope is that as I change things, this section can help you figure out why a change was made and if it will break any of your current work flows. The first major changes were made for the 0.56 release, so tracking will start there. Reasons are not provided for bug fixes for because the reason can assumed to be fixing the bug...

#### V1.0
Change:
Added functionality to generate graphs using a Uniprot ID as the input from command line. Added functionality to predict disorder domains. Added functionality to predict/graph disorder and predict disorder domains using a Uniprot ID from Python. Updated tests to include testing new functionality.


#### V0.61
Change:
Added functionality to predict or graph a disordered sequence from the command line by directly inputting the sequence. This can only do one sequence at a time and does not save the disorder values or graph. It is meant to provide a very quick and easy way to check something out.

#### V0.60
Change:
Added functionality to specify the horizontal lines that appear across the graphs rather than only having the option of having the dashed lines appear at intervals of 0.2. This functionality is in both Python and the command line.

#### V0.58
Change:
Updated the network with a newly trained network (using the same dataset as the original) that is slightly more accurate.

Reason:
I am always trying to find ways to make metapredict more accurate. When I manage to make the predictor better, I will update it.

#### V0.57
Change:
Bug fix that could result in prediction values to six decimal places in some scenarios

Change:
Changed titles for graphs generated by ``metapredict-graph-disorder`` to be 14 characters instead of 10. This is reflected in the title graph and the saved files.

Reason:
The 10 character save file was occasionally the same for multiple proteins. This resulted in the inability to discern which protein corresponded to which graph and could result in overwriting previously generated graphs. The 14 characters should be long enough to keep unique names for all proteins being analyzed.

Change:
Fixed bug that could result in crashing due to short fasta headers.


#### V0.56

Change:
Number of decimals in predictions was reduced from 6 to 3.

Reason:
It is not necessary to have accuracy out to 6 decimal places.

Change:
Added functionality to use . to specify current directory from command line.

Reason:
Improve functionality.

Change:
-DPI flag changed to -dpi in command line graphing function

Reason:
It was annoying to have to do all caps for this flag.

Change:
The ``predict-disorder`` command is now ``metapredict-predict-disorder`` and the ``graph-disorder`` command is now ``metapredict-graph-disorder``

Reason:
This will help users be able to use auto complete functionality from the command line using tab to pull up the graph or predict disorder commands while only having to remember metapredict.

Change:
The output for .csv files will now have a comma space between each value instead of just a comma.

Reason:
Improve readability.


### Copyright

Copyright (c) 2020-2021, Holehouse Lab - WUSM

#### Acknowledgements
IDP-Parrot, created by Dan Griffith, was used to generate the network used for metapredict. See [https://pypi.org/project/idptools-parrot/](https://pypi.org/project/idptools-parrot/) for some very cool machine learning stuff.

In addition to using Dan Griffith's tool for creating metapredict, the code for brnn_architecture.py and encode_sequence.py was written by Dan (originally for idp-parrot). 

I would also like to thank the team at MobiDB for creating the database that was used to train this predictor. Check out their awesome stuff at [https://mobidb.bio.unipd.it](https://mobidb.bio.unipd.it)

Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.3.
