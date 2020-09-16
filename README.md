# metapredict: A machine learning based tool for predicting protein disorder.

**metapredict** uses a bidirectional recurrent neural network trained on the consensus disorder values from 8 disorder predictors from 12 proteomes that were obtained from MobiDB. The creation of metapredict was made possible by IDP-parrot.

This package will allow for predicting disorder for any amino acid sequence, and predictions can be output as graphs or as raw values. Additionally, this package allows for predicting disorder values for protein sequences from .fasta files either from a Python IDE or from the command line.

## Installation:

metapredict is currently only availabile through Github. 

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

	$ git clone https://github.com/idptools/metapredict.git
	$ cd metapredict-master
	$ pip install .

This will install metapredict locally.

## Usage:

There are two ways you can use metapredict:
1. Directly from the command line
2. From within Python

## Command line usage:

### predicting disorder
The predict-disorder command from the command line takes a .fasta file as input and returns a .csv file containing rows where the first column in the row is the uniprot header and all following rows are predicted disorder values for each residue in the amino acid sequence associated with the fasta header. 

	$ predict-disorder <Path to .fasta file> <Path where to save the output> <Output file name>

This will save a .csv file to the location specified by <Path where to save the output>. The name specified in <Output file name> will be the name of the output file followed by .csv. The .csv extension is automatically added to the output file name.
**Example**

	$ predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions

**Additional Usage**
**Get raw prediction values**
By default, this will output prediction values that are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 and slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. However, if you want raw values, simply add the flag --no_normalization.

**Example**

	$ predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderPredictions/ myCoolPredictions --no_normalization


### graphing disorder
The graph-disorder command from the command line takes a .fasta file as input and returns a .png for every sequence within the .fasta file. The .png files for each sequence will be saved to wherever the user specifies as the output location. Each file will be named as predicted_disorder_ followed by the first 10 characters of the .fasta header (which is typically the unique identifier for the protein). For example, a fasta header of >sp|Q8N6T3|ARFG1_HUMAN will return a file saved as *predicted_disorder_sp|Q8N6T3|.png*. Additionally, the title of each graph is automatically generated and will have the title Predicted Protein Disorder followed by the first 10 characters of the .fasta header. In the previous example, the graph would be titled *Predicted Protein Disorder sp|Q8N6T3|*.

	$ graph-disorder <Path to .fasta file> <Path where to save the output>

**Example**

	$ graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/

**WARNING**
This command will generate a .png file for ***every*** sequence in the .fasta file. If you have 1,000 sequences in a .fasta file, it will generate **1,000** files. Therefore, I recommend saving the output to a dedicated folder (or at least not your Desktop...).

**Additional Usage**
**Changing resolution of save graphs**
By default, the output files have a DPI of 150. However, the user can change the DPI of the output (higher values have greater resolution but take up more space). To change the DPI simply add the flage -D followed by the wanted DPI value. 

**Example**

	$ graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/ -D 300

**Remove non-alphabetic characters from file name**
By default, the output files contain characters that are non-alphabetic (example *predicted_disorder_sp|Q8N6T3|.png*). This is not a problem on some operating systems, while others do not allow files to have names that contain certain characters. To get around this, you can add the --remove_characters flag. This will remove all non-alphabetic characters from the .fasta header when saving the file. The previous example with the header >sp|Q8N6T3|ARFG1_HUMAN would now save as *predicted_disorder_spQ8N726AR.png*. 

**Example**

	$ graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/ --remove_characters


## Using in Python:
In addition to using metapredict from the command line, you can also use it directly in Python.

First import metapredict -
 
	import metapredict
	from metapredict import meta

Once metapredict is imported you can work with individual sequences or .fasta files. 

### predicting disorder
The predict_disorder function will return a list of predicted disorder value for each residue of the input sequence. The input sequence should be a string.

	meta.predict_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS")

By default, the values are normalized between 1, but the user can get the raw prediction values by specifying 

	meta.predict_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS", normalized=False)


### graphing disorder 
The graph_disorder function will show a plot of the predicted disorder values across the input amino acid sequence.

	meta.graph_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS")

**additional usage**
**Changing title of generated graph**
There are two parameters that the user can change easily for graphing disorder. The first is the name of the title for the generate graph. The name by default is blank and the title of the graph is simply *Predicted Protein Disorder*. However, the name can be specified in order to add the name of the protein after the default title. For example, specifing name = "- PAB1" would result in a title of *Predicted Protein Disorder - PAB1*.

**Example**

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", name="Name of this nonexistant protein")

**Changing the resolution of the generate graph**
By default, the output graph has a DPI of 150. However, the user can change the DPI of the generated graph (higher values have greater resolution). To do so, simply specify DPI="Number" where the number is an integer.

**Example**

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", DPI=300)


### Calculating percent disorder
The percent_disorder function will return the percent of disordered residues in a sequence (as a decimal value).

**Example**

	meta.percent_disorder("DAPPTSQEHTQAEDKERD")

By default, this uses a cutoff predicted value of equal to or greater than 0.5 for a residue to be considered disordered.

**additional usage**
**Changing cutoff value**
If you want to be more strict in what you consider to be disordered for calculating percent disorder of an input sequence, you can simply specify the cutoff value.


**Example**

	meta.percent_disorder("DAPPTSQEHTQAEDKERD", cutoff=0.8)

The higher the cutoff value, the higher the value for any given predicted residue must be greater than or equal to in order to be considered disordered when calculating the final percent disorder for the input sequence.


### Predicting disorder from a .fasta file
Similar to the command line, you can predict disorder values for the amino acid sequence in a .fasta file. By default, this function will return a dictionary where the keys in the dictionary are the fasta headers and the values are the disorder predictions of the amino acid sequence associated with each fasta header in the original .fasta file.

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta")


**additional usage**
**Save the output values**
By default the predict_disorder_fasta function will immediately return a dictionary. However, you can also save them to a .csv file by specifying *save=True* and output_path="location you want to save the file to". This will save a file called *predicted_disorder_values.csv* to the location you specify for the output_path

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta", save=True, output_path="file path where the output .csv should be saved")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=True output_path"/Users/thisUser/Desktop/")

**Specifying the name of the output file**
By default, the generated .csv file will save as *predicted_disorder_values.csv*. However, you can change the default by specifing output_name="my_cool_file".

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta", save=True, output_path="file path where the output .csv should be saved", output_name="name of file")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=True output_path"/Users/thisUser/Desktop/", output_name="my_predictions")

Importantly, you do not need to add the .csv file extension to your file name specified in output_name. However, if you do specify .csv as a file extension, everything should still work.

**Get raw prediction values**
By default, this will output prediction values that are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 and slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. If you want the raw values simply specify normalized=False.

**Example**

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", normalized=False)


### Generating graphs from a .fasta file
Similar to the command line, you can graph predicted disorder values for the amino acid sequence in a .fasta file. The graph_disorder_fasta function takes a .fasta file as input and returns a .png for every sequence within the .fasta file. The .png files for each sequence will be saved to wherever the user specifies as the output location. Each file will be named as predicted_disorder_ followed by the first 10 characters of the .fasta header (which is typically the unique identifier for the protein). For example, a fasta header of >sp|Q8N6T3|ARFG1_HUMAN will return a file saved as *predicted_disorder_sp|Q8N6T3|.png*. Additionally, the title of each graph is automatically generated and will have the title Predicted Protein Disorder followed by the first 10 characters of the .fasta header. In the previous example, the graph would be titled *Predicted Protein Disorder sp|Q8N6T3|*.

**WARNING**
This command will generate a .png file for ***every*** sequence in the .fasta file. If you have 1,000 sequences in a .fasta file, it will generate **1,000** files. Therefore, I recommend saving the output to a dedicated folder (or at least not your Desktop...).

**Example**

	meta.graph_disorder_fasta("file path to .fasta file/fileName.fasta", output_path="file path of where to save output graphs")

An actual filepath would look something like:

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_path="/Users/thisUser/Desktop/folderForGraphs")



**Additional Usage**
**Changing resolution of save graphs**
By default, the output files have a DPI of 150. However, the user can change the DPI of the output files (higher values have greater resolution but take up more space). To change the DPI, specify DPI=# where # is an whole integer number.

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", DPI=300, output_path="/Users/thisUser/Desktop/folderForGraphs")

**Remove non-alphabetic characters from file name**
By default, the output files contain characters that are non-alphabetic (example *predicted_disorder_sp|Q8N6T3|.png*). This is not a problem on some operating systems, while others do not allow files to have names that contain certain characters. To get around this, you can add the --remove_characters flag. This will remove all non-alphabetic characters from the .fasta header when saving the file. The previous example with the header >sp|Q8N6T3|ARFG1_HUMAN would now save as *predicted_disorder_spQ8N726AR.png*. 

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", DPI=300, output_path="/Users/thisUser/Desktop/folderForGraphs", remove_characters=True)

**Viewing generated graphs without saving**
The default behavior for the graph_disorder_fasta function is to save the generated graphs for viewing elsewhere. However, the user can choose to view the generated graphs without saving them. 

**WARNING**
If you choose to view the generated graphs instead of saving them, you can only view one at a time and each must be closed before the next will open. This is not a problem if you only have around 10 sequences in your .fasta file. However, if you have 1,000 sequences in a .fasta file, you will have to close out ***1,000*** graphs. This isn't a problem if you don't mind clicking... a lot.

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", save=False)



### Copyright

Copyright (c) 2020, Holehouse Lab - WUSM

#### Acknowledgements
IDP-Parrot, created by Dan Griffith, was used to generate the network used for metapredict. See https://pypi.org/project/idptools-parrot/ for some very cool machine learning stuff.

In addition to using Dan Griffith's tool for creating metapredict, the code for brnn_architecture.py and encode_sequence.py was written by Dan (originally for IDP-Parrot). 

Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.3.
