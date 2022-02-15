# metapredict: A machine learning-based tool for predicting protein disorder.

**Important update** - as of February 15, 2022 we have updated metapredict to V2.0. This comes with important changes that improve the accuracy of metapredict. Please see the section on the update *Major update to metapredict predictions to increase overall accuracy* below. In addition, this update changes the functionality of the *predict_disorder_domains()* function, so please read the documenation on that function if you were using it previously. 


**metapredict** uses a bidirectional recurrent neural network trained on the consensus disorder values from 8 disorder predictors from 12 proteomes that were obtained from [MobiDB](https://mobidb.bio.unipd.it/). The creation of metapredict was made possible by [parrot](https://github.com/idptools/parrot).

## What is metapredict?

**metapredict** is a bit different than your typical protein disorder predictor. Instead of predicting the percent chance that a residue within a sequence might be disordered, metapredict tries to predict the consensus disorder score for the residue. This is because metapredict was trained on **consensus** values from MobiDB. These values are the percent of other disorder predictors that predicted a residue in a sequence to be disordered. For example, if a residue in a sequence has a value of 1 from the MobiDB consensus values, then *all disorder predictors predicted that residue to be disordered*. If the value was 0.5, than half of the predictors predicted that residue to be disordered. In this way, metapredict can help you quickly determine the likelihood that any given sequence is disordered by giving you an approximation of what other predictors would predict (things got pretty 'meta' there, hence the name metapredict).

## Major update to metapredict predictions to increase overall accuracy

We are always working to make metapredict better, and we have recently managed just that. More details will be below, but the short story is that we have made significant improvements in the accuracy of disorder predictions using metapredict. By analyzing our new network using the Disprot-PDB dataset predictions, we found that the MCC (which is a measurement accounting for false positives, false negatives, true positives, and true negatives) for metapredict increased from 0.588 for the old (original) network to 0.7 for our new network. To put this in perspective, our original network was ranked 12th most accurate when analyzing the Disprot-PDB dataset, and it is now ranked as the 2nd most accurate available predictor. We should also note that we are still trying a few 'tweaks' to this new network and plan to updated it if we can improve accuracy any further We will be publishing the updated benchmarks for the 'new metapredict' in the near future (unless we already have but forgot to take this sentance out of the documentation...).

### But wait! I need the old metapredict predictions!!!

No worries! We left users access to the old network. The *default network is now our new, more accurate network*. However, by calling **-l** or **--legacy** from the command line or by specififing **legacy=True** from Python, you will be able to use the original metapredict network. We wanted to keep making metapredict better, but we also wanted to minimize disruptions to anyone currently relying on the original metapredict predictions for whatever reason.


## So... how exactly was this more more accurate metapredict network made?

We didn't think it was possible, but metapredict has somehow become *even more meta*. Get ready, because things are about to get a little weird. When we implemented the AlphaFold2 pLDDT prediction feature (see section below), we noticed that there were occassional discrepencies between metapredict and the predicted pLDDT (ppLDDT) scores. When the ppLDDT scores get high enough, it is unlikely that a given region is actually disordered. So, we developed a version of metapredict that we originally called 'metapredict-hybrid' that essentially combined aspects of the ppLDDT scores and the original metapredict scores. We found that this 'hybrid predictor' was **much better** than the original metapredict disorder predictor at predicting disordered regions. **But we didn't stop there.** We think one of metapredicts best features is *it is really really fast*. This 'hybrid-predictor' was a little on the slow side, coming in at about 1/3 the speed of the original metapredict predictor. This is still VERY fast, but we thought we could do better. So, we took a little over 300,000 protein sequences and generated metapredict-hybrid scores for those sequences. We then fed those sequences and the corresponding metapredict-hybrid scores and generated a new bidirectional recurrent neural network (BRNN) using PARROT. We then tested this new network against the original metapredict-hybrid predictions and the original metapredict network. The new network that was trained on metapredict-hybrid scores *actually outperformed the metapredict-hybrid predictions when benchmarking against Disprot-PDB*. Importantly, this new (super accurate) network was only 30% slower than the original metapredict network, which is substantially better than the 70% hit that metapredict-hybrid took. 
 
**TL;DR** We made the original metapredict predictor using a network trained on consensus scores from MobiDB. We then trained a network on AlphaFold2 pLDDT scores. Next, we made a predictor that combined prediction values from the original metapredict predictor and the AlphaFold2 pLDDT predictor to make very accurate disorder predictions. Finally, we took hundreds of thousands of proteins, generated disorder prediction scores using the aforementioned combination of the original metapredict predictions and the AlphaFold2 predictions, and then trained our final network on those scores. **That's pretty dang meta.**


### In addition to predicting disorder, metapredict also can predict AlphaFold2 pLDDT confidence scores

In addition, metapredict offers predicted pLDDT confidence scores from AlphaFold2. These predicted scores use a bidirectional recurrent neural network (BRNN) trained on the per residue pLDDT (predicted IDDT-Ca) confidence scores generated by AlphaFold2 (AF2). The confidence scores (pLDDT) from the proteomes of *Danio rerio*, *Candida albicans*, *Mus musculus*, *Escherichia coli*, *Drosophila melanogaster*, *Methanocaldococcus jannaschii*, *Plasmodium falciparum*, *Mycobacterium tuberculosis*, *Caenorhabditis elegans*, *Dictyostelium discoideum*, *Trypanosoma cruzi*, *Saccharomyces cerevisiae*, *Schizosaccharomyces pombe*, *Rattus norvegicus*, *Homo sapiens*, *Arabidopsis thaliana*, *Zea mays*, *Leishmania infantum*, *Staphylococcus aureus*, *Glycine max*, *Oryza sativa* were used to generate the BRNN. These pLDDT scores measure the local confidence that AlphaFold2 has in its predicted structure. The scores go from 0-100 where 0 represents low confidence and 100 represents high confidence. For more information, please see: *Highly accurate protein structure prediction with AlphaFold* https://doi.org/10.1038/s41586-021-03819-2. In describing these scores, the team states that regions with pLDDT scores of less than 50 should not be interpreted except as *possible* disordered regions.


### What might the predicted pLDDT scores from AlphaFold2 be used for?

These scores can be used for many applications such as generating a quick preview of which regions of your protein of interest AF2 might be able to predict with high confidence, or which regions of your protein *might* be disordered. AF2 is not (strictly speaking) a disorder predictor, and the pLDDT scores are not directly representative of protein disorder. Therefore, any conclusions drawn with regards to disorder from predicted AF2 pLDDT scores should be interpreted with care, but they may be able to provide an additional metric to assess the likelihood that any given protein region may be disordered.

 
## Why is metapredict useful?

A major drawback of consensus disorder databases is that they can only give you values of *previously predicted protein sequences*. Therefore, if your sequence of interest is not in their database, tough luck. In addition, installing multiple different predictors to generate consensus scores locally is computationally expensive, time consuming, and in some cases simply not possible. Fortunately, **metapredict** gives you a way around this problem!

**metapredict** allows for predicting disorder for any amino acid sequence, and predictions can be output as graphs or as raw values. Additionally, metapredict allows for predicting disorder values for protein sequences from .fasta files either directly in Python or from the command-line. This gives maximum flexibility so the user can easily predict/graph disorder from a single sequence or for an entire proteome.

For full documentation, please see:
https://metapredict.readthedocs.io/en/latest/getting_started.html

For disorder predictions using our server, please see:
https://metapredict.net

## How to cite metapredict

If you use metapredict for your work, please cite the metapredict paper - 
 
*Emenecker RJ, Griffith D, Holehouse AS, metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure, Biophysical Journal (2021), doi: https:// doi.org/10.1016/j.bpj.2021.08.039.*


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

**Note** for any commands from the command-line, if you need to use the original metapredict predictor as opposed to our new, updated predictor, use the ``-l`` or ``--legacy`` flag!


### Predicting Disorder from a fasta file

The ``metapredict-predict-disorder`` command from the command line takes a .fasta file as input and returns disorder scores for the sequences in the FASTA file.

	$ metapredict-predict-disorder <Path to .fasta file>

**Example**

	$ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta 

**Additional Usage**

**specifying where to save the output -** 
If you would like to specify where to save the ouptut, simply use the ``-o`` or ``--output-file`` flag and then specify the file path and file name. By default this command will save the output file as disorder_scores.csv to your current working directory. However, you can specify the file name in the output path.

**Example**

    $ metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, use the ``-l`` or ``--legacy`` flag!

### Predicting Disorder from a sequence

``metapredict-quick-predict`` is a command that will let you input a sequence and get disorder values immediately printed to the terminal. The only argument that can be input is the sequence.

**Example:**

	$ metapredict-quick-predict ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, use the ``-l`` or ``--legacy`` flag!


### Predicting AlphaFold2 Confidence Scores from a fasta file

The ``metapredict-predict-pLDDT`` command from the command line takes a .fasta file as input and returns predicted AlphaFold2 pLDDT scores for the sequences in the FASTA file.

	$ metapredict-predict-pLDDT <Path to .fasta file>

**Example**

	$ metapredict-predict-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta 

**Additional Usage**

**Specify where to save the output -** 
If you would like to specify where to save the ouptut, simply use the ``-o`` or ``--output-file`` flag and then specify the file path. By default this command will save the output file as pLDDT_scores.csv to your current working directory. However, you can specify the file name in the output path.

**Example**

    $ metapredict-predict-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_pLDDT_predictions.csv


### Graphing Disorder from a fasta file

The ``metapredict-graph-disorder`` command from the command line takes a .fasta file as input and returns a graph for every sequence within the .fasta file. **Warning** This will return a graph for every sequence in the FASTA file. 

	$ metapredict-graph-disorder <Path to .fasta file> 

**Example**

	$ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta 

If no output directory is specified, this function will make an output directory in the current working directory called *disorder_out*. This directory will hold all generated graphs.

**Additional Usage**

**Adding AlphaFold2 Confidence Scores -**
To add predicted AlphaFold2 pLDDT scores, simply use the ``-p`` or ``--pLDDT`` flag.

**Example**

	$ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -p


**Specifying where to save the output -**
To specify where to dave the output, simply use the ``-o`` or ``--output-directory`` flag.

**Example**

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/FolderForCoolPredictions


**Changing resolution of saved graphs -**
By default, the output graphs have a DPI of 150. However, the user can change the DPI of the output (higher values have greater resolution but take up more space). To change the DPI simply add the flag ``-D`` or ``--dpi`` followed by the wanted DPI value. 

**Example**

	$ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ -D 300


**Changing the file type -**
By default the graphs will save as .png files. However, you can specify the file type by calling ``--filetype`` and then specifying the file type. Any matplotlib compatible file extension should work (for example, pdf).

**Example**

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --filetype pdf

**Indexing file names -**
If you would like to index the file names with a leading unique integer starting at 1, use the ``--indexed-filenames`` flag.

**Example**

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --indexed-filenames

**Changing the disorder threshhold line on the graph -**
If you would like to change the disorder threshold line plotted on the graph, use the ``--disorder-threshold`` flag followed by some value between 0 and 1. Default is 0.3.

**Example**

    $ metapredict-graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/DisorderGraphsFolder/ --disorder-threshold 0.5

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, use the ``-l`` or ``--legacy`` flag!


### Graphing Disorder from a sequence

``metapredict-quick-graph`` is a command that will let you input a sequence and get a plot of the disorder back immediately. You cannot input fasta files for this command. The command only takes three arguments, 1. the sequence 2. *optional* DPI ``-D``  or ``--dpi`` of the ouput graph which defaults to 150 DPI, and 3. *optional* to include predicted AlphaFold2 condience scores, use the ``-p`` or ``--pLDDT`` flag.


**Example:**

	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN

**Example:**

	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -D 200

**Example:**

	$ metapredict-quick-graph ISQQMQAQPAMVKSQQQQQQQQQQHQHQQQQLQQQQQLQMSQQQVQQQGIYNNGTIAVAN -D 200 -p

### Graphing Disorder from a Uniprot ID

``metapredict-uniprot`` is a command that will let you input any Uniprot ID and get a plot of the disorder for the corresponding protein. The default behavior is to have a plot automatically appear. Apart from the Uniprot ID which is required for this command, the command has four possible additional *optional* arguments, 1. To include predicted AlphaFold2 2 pLDDT confidence scores, use the ``-p``  or ``--pLDDT`` flag. DPI can be changed with the ``-D``  or ``--dpi`` flags, default is 150 DPI, 3. Using ``-o``  or ``--ourput-file`` will save the plot to a specified directory (default is current directory) - filenames and file extensions (pdf, jpg, png, etc) can be specified here. If there is no file name specified, it will save as the Uniprot ID and as a .png, 4. ``-t``  or ``--title`` will let you specify the title of the plot. By defualt the title will be *Disorder for* followed by the Uniprot ID.

**Example:**

	$ metapredict-uniprot Q8RYC8

**Example:**

	$ metapredict-uniprot Q8RYC8 -p

**Example:**

	$ metapredict-uniprot Q8RYC8 -D 300

**Example:**

	$ metapredict-uniprot Q8RYC8 -o /Users/ThisUser/Desktop/MyFolder/DisorderGraphs

**Example:**

	$ metapredict-uniprot Q8RYC8 -o /Users/ThisUser/Desktop/MyFolder/DisorderGraphs/my_graph.png

**Example:**

    $ metapredict-uniprot Q8RYC8 -t ARF19

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, use the ``-l`` or ``--legacy`` flag!


### Graphing Predicted AlphaFold2 Confidence Scores from a fasta file

The ``metapredict-graph-pLDDT`` command from the command line takes a .fasta file as input and returns a graph of the predicted AlphaFold2 pLDDT confidence score for every sequence within the .fasta file. **Warning** This will return a graph for every sequence in the FASTA file. 

	$ metapredict-graph-pLDDT <Path to .fasta file> 

**Example**

	$ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta 

If no output directory is specified, this function will make an output directory in the current working directory called *pLDDT_out*. This directory will hold all generated graphs.

**Additional Usage**

**Specifying where to save the output -**
To specify where to dave the output, simply use the ``-o`` or ``--output-directory`` flag.

**Example**

    $ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/FolderForCoolPredictions


**Changing resolution of saved graphs -**
By default, the output graphs have a DPI of 150. However, the user can change the DPI of the output (higher values have greater resolution but take up more space). To change the DPI simply add the flag ``-D`` or ``--dpi`` followed by the wanted DPI value. 

**Example**

	$ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/pLLDTGraphsFolder/ -D 300


**Changing the file type -**
By default the graphs will save as .png files. However, you can specify the file type by calling ``--filetype`` and then specifying the file type. Any matplotlib compatible file extension should work (for example, pdf).

**Example**

    $ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/pLDDTGraphsFolder/ --filetype pdf

**Indexing file names -**
If you would like to index the file names with a leading unique integer starting at 1, use the ``--indexed-filenames`` flag.

**Example**

    $ metapredict-graph-pLDDT /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/pLDDTGraphsFolder/ --indexed-filenames



### Predicting IDRs from a fasta file

The ``metapredict-predict-idrs`` command from the command line takes a .fasta file as input and returns a .fasta file containing the IDRs for every sequence from the input .fasta file. 

	$ metapredict-predict-idrs <Path to .fasta file> 

**Example**

	$ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta 

**Additional Usage**

**specifying where to save the output -** 
If you would like to specify where to save the ouptut, simply use the ``-o`` or ``--output-file`` flag and then specify the file path and file name.

**Example**

    $ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_idrs.fasta

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, use the ``-l`` or ``--legacy`` flag!

**Example**

    $ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_idrs.fasta -l

**Changing output threshold for disorder-**
To change the cutoff value for something to be considered disordered, simply use the ``--threshold`` flag and then specify your value. For legacy, the default is 0.42. For the new version of metapredict, the value is 0.5. 

**Example**

    $ metapredict-predict-idrs /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_idrs.fasta --threshold 0.3



## Using metapredict in Python:

In addition to using metapredict from the command line, you can also use metapredict directly in Python.

First import metapredict -
 
	import metapredict as meta


Once metapredict is imported you can work with individual sequences or .fasta files. 


### Predicting Disorder

The ``predict_disorder`` function will return a list of predicted disorder values for each residue of the input sequence. The input sequence should be a string. Running -

	meta.predict_disorder("DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR")

would output -

	[1, 1, 1, 1, 0.957, 0.934, 0.964, 0.891, 0.863, 0.855, 0.793, 0.719, 0.665, 0.638, 0.576, 0.536, 0.496, 0.482, 0.306, 0.152, 0.096, 0.088, 0.049, 0.097, 0.235, 0.317, 0.341, 0.377, 0.388, 0.412, 0.46, 0.47, 0.545, 0.428]

By default, output prediction values are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 or slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. However, the user can get the raw prediction values by specifying *normalized=False* as a second argument in meta.predict_disorder. There is not a very good reason to do this, and it is generally not recommended. However, we wanted to give users the maximum amount of flexibility when using metapredict, so we made it an option.

	meta.predict_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS", normalized=False)


**NOTE - using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.predict_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS", legacy=True)


### Predicting AlphaFold2 Confidence Scores

The ``predict_pLDDT`` function will return a list of predicted AlphaFold2 pLDDT confidence scores  for each residue of the input sequence. The input sequence should be a string. Running -

	meta.predict_pLDDT("DAPPTSQEHTQAEDKERD")

would output -

	[35.7925, 40.4579, 46.3753, 46.2976, 42.3189, 42.0248, 43.5976, 40.7481, 40.1676, 41.9618, 43.3977, 43.938, 41.8352, 44.0462, 44.5382, 46.3081, 49.2345, 46.0671]


### Predicting Disorder Domains

The ``predict_disorder_domains()`` function takes in an amino acid sequence and returns a DisorderObject. The DisorderObject has 6 dot variables that can be called to get informaton about your input sequence. They are as follows:


.sequence : str    
    Amino acid sequence 

.disorder : list or np.ndaarray
    Hybrid disorder score

.disordered_domain_boundaries : list
    List of domain boundaries for IDRs using Python indexing

.folded_domain_boundaries : list
    List of domain boundaries for folded domains using Python indexing

.disordered_domains : list
    List of the actual sequences for IDRs

.folded_domains : list
    List of the actual sequences for folded domains

**Examples**

	seq = meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHS")

Now we can call the various dot values for **seq**. 

**Getting the sequence**

	print(seq.sequence)

returns

	MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHS


**Getting the disorder scores**

	print(seq.disorder)

returns

	[0.922  0.9223 0.9246 0.9047 0.8916 0.8956 0.8931 0.883  0.8613 0.8573
 	0.852  0.8582 0.8614 0.8455 0.826  0.7974 0.7616 0.7248 0.6782 0.6375
 	0.5886 0.5476 0.5094 0.4774 0.4472 0.4318 0.4266 0.4222 0.3953 0.3993
 	0.3904 0.4004 0.3962 0.3721 0.3855 0.3582 0.3456 0.3682 0.3488 0.3274
 	0.3258 0.2937 0.2864 0.3004 0.3358 0.3815 0.4397 0.4594 0.4673 0.4535
 	0.4446 0.4481 0.4546 0.4454 0.4549 0.4564 0.4677 0.4539 0.4713 0.49
 	0.4934 0.4835 0.4815 0.4692 0.4548 0.4856 0.495  0.4809 0.502  0.4944
 	0.4612 0.4561 0.436  0.4203 0.3784 0.3624 0.3739 0.3983 0.4348 0.4369]


**Getting the disorder domain boundaries**

	print(seq.disordered_domain_boundaries)

returns

	[[0, 23]]

Where each nested list is the boundaries for a specific disordered region and the first element in each list is the start of that region and the second element is the end of that region.

**Getting the folded domain boundaries**

	print(seq.folded_domain_boundaries)

returns

	[[23, 80]]

Where each nested list is the boundaries for a specific folded region and the first element in each list is the start of that region and the second element is the end of that region.

**Getting the disordered domain sequences**

	print(seq.disordered_domains)

returns

	['MKAPSNGFLPSSNEGEKKPINSQ']

Where each element in the list is a specific disordered region identified in the sequence.

**Getting the folded domain sequences**

	print(seq.folded_domains)

returns

	['LWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHS']

Where each element in the list is a specific folded region identified in the sequence.


**Additional Usage**

**Altering the disorder theshhold -**
To alter the disorder theshold, simply set *disorder_threshold=my_value* where *my_value* is a float. The higher the treshold value, the more conservative metapredict will be for designating a region as disordered. Default = 0.42

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", disorder_threshold=0.3)

**Altering minimum IDR size -**
The minimum IDR size will define the smallest possible region that could be considered an IDR. In other words, you will not be able to get back an IDR smaller than the defined size. Default is 12.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_IDR_size = 10)

**Altering the minimum folded domain size -**
The minimum folded domain size defines where we expect the limit of small folded domains to be. *NOTE* this is not a hard limit and functions more to modulate the removal of large gaps. In other words, gaps less than this size are treated less strictly. *Note* that, in addition, gaps < 35 are evaluated with a threshold of 0.35 x disorder_threshold and gaps < 20 are evaluated with a threshold of 0.25 x disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which are IDRs in isolation) often show up with reduced apparent disorder within IDRs but can be as short as 20-30 residues. The folded_domain_threshold is used based on the idea that it allows a 'shortest reasonable' folded domain to be identified. Default=50.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_folded_domain = 60)

**Altering gap_closure -**
The gap closure defines the largest gap that would be closed. Gaps here refer to a scenario in which you have two groups of disordered residues seprated by a 'gap' of not disordered residues. In general large gap sizes will favour larger contiguous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps are increasingly rare. Default=10.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", gap_closure = 5)


**Using the original metapredict network-**
To use the original metapredict network, simply set ``legacy=True``.

**Example:** 

	predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", legacy=True)






The ``predict_disorder_domains`` function takes in an amino acid sequence and returns a 4-position tuple with: 0. the raw disorder scores from 0 to 1 where 1 is the highest probability that a residue is disordered, 1. the smoothed disorder score used for boundary identification, 2. a list of elements where each element is a list where 0 and 1 define the IDR location and 2 gives the actual sequence, and 3. a list of elements where each element is a list where 0 and 1 define the folded domain location and 2 gives the actual sequence

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
To alter the disorder theshold, simply set *disorder_threshold=my_value* where *my_value* is a float. The higher the treshold value, the more conservative metapredict will be for designating a region as disordered. Default = 0.42

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", disorder_threshold=0.3)

**Altering minimum IDR size -**
The minimum IDR size will define the smallest possible region that could be considered an IDR. In other words, you will not be able to get back an IDR smaller than the defined size. Default is 12.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_IDR_size = 10)

**Altering the minimum folded domain size -**
The minimum folded domain size defines where we expect the limit of small folded domains to be. *NOTE* this is not a hard limit and functions more to modulate the removal of large gaps. In other words, gaps less than this size are treated less strictly. *Note* that, in addition, gaps < 35 are evaluated with a threshold of 0.35 x disorder_threshold and gaps < 20 are evaluated with a threshold of 0.25 x disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which are IDRs in isolation) often show up with reduced apparent disorder within IDRs but can be as short as 20-30 residues. The folded_domain_threshold is used based on the idea that it allows a 'shortest reasonable' folded domain to be identified. Default=50.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_folded_domain = 60)

**Altering gap_closure -**
The gap closure defines the largest gap that would be closed. Gaps here refer to a scenario in which you have two groups of disordered residues seprated by a 'gap' of not disordered residues. In general large gap sizes will favour larger contigous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps are increasingly rare. Default=10.

**Example**

	meta.predict_disorder_domains("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", gap_closure = 5)

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.predict_disorder_domains("DAPTSQEHTQAEDKERDSKTHPQKKQSPS", legacy=True)


### Predicting Disorder Domains using a Uniprot ID

In addition to inputting a sequence, you can predict disorder domains by inputting a Uniprot ID by using the ``predict_disorder_domains_uniprot`` function. This function has the exact same functionality as ``predict_disorder_domains`` except you can now input a Uniprot ID. 

**Example**

    meta.predict_disorder_domains_uniprot('Q8N6T3')


**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.predict_disorder_domains_uniprot('Q8N6T3', legacy=True)


### Graphing Disorder 

The ``graph_disorder`` function will show a plot of the predicted disorder consensus values across the input amino acid sequence.

	meta.graph_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS")

**Additional Usage**

**Adding Predicted AlphaFold2 Confidence Scores -**
To add predicted AlphaFold2 pLDDT confidence scores, simply specify *pLDDT_scores=True*.

**Example**

	meta.graph_disorder("DAPTSQEHTQAEDKERDSKTHPQKKQSPS", pLDDT_scores=True)


**Changing the title of the generated graph -**
There are two parameters that the user can change for graph_disorder. The first is the name of the title for the generated graph. The name by default is blank and the title of the graph is simply *Predicted protein disorder*. However, the title can be specified by specifing *title* = "my cool title" would result in a title of *my cool title*.

**Example**

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", title="Name of this nonexistant protein")

**Changing the resolution of the generated graph -**
By default, the output graph has a DPI of 150. However, the user can change the DPI of the generated graph (higher values have greater resolution). To do so, simply specify *DPI="Number"* where the number is an integer.

**Example**

	meta.graph_disorder("DAPPTSQEHTQAEDKERD", DPI=300)

**Changing the disorder threshold line -**
The disorder threshold line for graphs defaults to 0.3. However, if you want to change where the line designating the disorder cutoff is, simply specify *disorder_threshold = Float* where Float is some decimal value between 0 and 1. 

**Example**

    meta.graph_disorder("DAPPTSQEHTQAEDKERD", disorder_threshold=0.5)

**Adding shaded regions to the graph -** If you would like to shade specific regions of your generated graph (perhaps shade the disordered regions), you can specify *shaded_regions=[[list of regions]]* where the list of regions is a list of lists that defines the regions to shade.

**Example**

    meta.graph_disorder("DAPPTSQEHTQAEDKERDDAPPTSQEHTQAEDKERDDAPPTSQEHTQAEDKERD", shaded_regions=[[1, 20], [30, 40]])

In addition, you can specify the color of the shaded regions by specifying *shaded_region_color*. The default for this is red. You can specify any matplotlib color or a hex color string.

**Example**

    meta.graph_disorder("DAPPTSQEHTQAEDKERDDAPPTSQEHTQAEDKERDDAPPTSQEHTQAEDKERD", shaded_regions=[[1, 20], [30, 40]], shaded_region_color="blue")

**Saving the graph -** By default, the graph will automatically appear. However, you can also save the graph if you'd like. To do this, simply specify *output_file = path_where_to_save/filename.file_extension.* For example, output_file=/Users/thisUser/Desktop/cool_graphs/myCoolGraph.png. You can save the file with any valid matplotlib extension (.png, .pdf, etc.). 

**Example**

    meta.graph_disorder("DAPPTSQEHTQAEDKER", output_file=/Users/thisUser/Desktop/cool_graphs/myCoolGraph.png)

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.graph_disorder("DAPPTSQEHTQAEDKER", legacy=True)


### Graphing AlphaFold2 Confidence Scores

The ``graph_pLDDT`` function will show a plot of the predicted AlphaFold2 pLDDT confidence scores across the input amino acid sequence.

	meta.graph_pLDDT("DAPTSQEHTQAEDKERDSKTHPQKKQSPS")

This function has all of the same functionality as ``graph_disorder``.

### Calculating Percent Disorder

The ``percent_disorder`` function will return the percent of residues in a sequence that  have predicted consensus disorder values of 30% or more (as a decimal value).

**Example**

	meta.percent_disorder("DAPPTSQEHTQAEDKERD")

By default, this function uses a cutoff value of equal to or greater than 0.3 for a residue to be considered disordered.

**Additional Usage**

**Changing the cutoff value -**
If you want to be more strict in what you consider to be disordered for calculating percent disorder of an input sequence, you can simply specify the cutoff value by adding the argument *cutoff=decimal* where the decimal corresponds to the percent you would like to use as the cutoff (for example, 0.8 would be 80%).


**Example**

	meta.percent_disorder("DAPPTSQEHTQAEDKERD", cutoff=0.8)

The higher the cutoff value, the higher the value any given predicted residue must be greater than or equal to in order to be considered disordered when calculating the final percent disorder for the input sequence.

**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.percent_disorder("DAPPTSQEHTQAEDKERD", legacy=True)


### Predicting Disorder From a .fasta File

By using the ``predict_disorder_fasta`` function, you can predict disorder values for the amino acid sequences in a .fasta file. By default, this function will return a dictionary where the keys in the dictionary are the fasta headers and the values are the consensus disorder predictions of the amino acid sequence associated with each fasta header in the original .fasta file.

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta")


**Additional Usage**

**Save the output values -**
By default the predict_disorder_fasta function will immediately return a dictionary. However, you can also save the output to a .csv file by specifying *output_file = "location you want to save the file to*". When specifying the file path, you also want to specify the file name. The first cell of each row will contain a fasta header and the subsequent cells in that row will contain predicted consensus disorder values for the protein associated with the fasta header.

**Example**

	meta.predict_disorder_fasta("file path to .fasta file/fileName.fasta", output_file="file path where the output .csv should be saved")

An actual filepath would look something like:

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_file="/Users/thisUser/Desktop/cool_predictions.csv")


**Get raw prediction values -**
By default, this function will output prediction values that are normalized between 0 and 1. However, some of the raw values from the predictor are slightly less than 0 or slightly greater than 1. The negative values are simply replaced with 0 and the values greater than 1 are replaced with 1 by default. If you want the raw values simply specify *normalized=False*. There is not a very good reason to do this, and it is generally not recommended. However, we wanted to give users the maximum amount of flexibility when using metapredict, so we made it an option.

**Example**

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", normalized=False)


**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.predict_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", legacy=True)


### Predicting AlphaFold2 pLDDT confidence scores From a .fasta File

Just like with ``predict_disorder_fasta``, you can use ``predict_pLDDT_fasta`` to get predicted AlphaFold2 pLDDT confidence scores from a fasta file. All the same functionality in ``predict_disorder_fasta`` is in ``predict_pLDDT_fasta``.

**Example**

	meta.predict_pLDDT_fasta("/Users/thisUser/Desktop/coolSequences.fasta")


### Predict Disorder Using Uniprot ID
By using the ``predict_disorder_uniprot`` function, you can return predicted consensus disorder values for the amino acid sequence of a protein by specifying the Uniprot ID. 

**Example**

    meta.predict_disorder_uniprot("Q8N6T3")


**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.predict_disorder_uniprot("Q8N6T3", legacy=True)


### Predicting AlphaFold2 Confidence Scores Using Uniprot ID

By using the ``predict_pLDDT_uniprot`` function, you can generate predicted AlphaFold2 pLDDT confidence scores by inputting a Uniprot ID.

**Example**

    meta.predict_pLDDT_uniprot('P16892')


### Generating Disorder Graphs From a .fasta File

By using the ``graph_disorder_fasta`` function, you can graph predicted consensus disorder values for the amino acid sequences in a .fasta file. The *graph_disorder_fasta* function takes a .fasta file as input and by default will return the graphs immediately. However, you can specify *output_dir=path_to_save_files* which result in a a .png file saved to that directory for every sequence within the .fasta file. You cannot specify the output file name here! By default, the file name will be the first 14 characters of the FASTA header followed by the filetype as specified by filetype. If you wish for the files to include a unique leading number (i.e. X_rest_of_name where X starts at 1 and increments) then set *indexed_filenames = True*. This can be useful if you have sequences where the 1st 14 characters may be identical, which would otherwise overwrite an output file. By default this will return a single graph for every sequence in the FASTA file. 

**WARNING -**
This command will generate a graph for ***every*** sequence in the .fasta file. If you have 1,000 sequences in a .fasta file and you do not specify the *output_dir*, it will generate **1,000** graphs that you will have to close sequentially. Therefore, I recommend specifying the *output_dir* such that the output is saved to a dedicated folder.

**Example**

	meta.graph_disorder_fasta("file path to .fasta file/fileName.fasta", output_dir="file path of where to save output graphs")

An actual filepath would look something like:

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_dir="/Users/thisUser/Desktop/folderForGraphs")


**Additional Usage**

**Adding Predicted AlphaFold2 Confidence Scores -**
To add predicted AlphaFold2 pLDDT confidence scores, simply specify *pLDDT_scores=True*.

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", pLDDT_scores=True)


**Changing resolution of saved graphs -**
By default, the output files have a DPI of 150. However, the user can change the DPI of the output files (higher values have greater resolution but take up more space). To change the DPI, specify *DPI=Number* where Number is an integer.

**Example**

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", DPI=300, output_dir="/Users/thisUser/Desktop/folderForGraphs")

**Changing the output File Type -** 
By default ths output file is a .png. However, you can specify the output file type by using *output_filetype="file_type"* where file_type is some matplotlib compatible file type (such as .pdf).

**Example**

    meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_dir="/Users/thisUser/Desktop/folderForGraphs", output_filetype = "pdf")


**Indexing generated files -**
If you would like to index the file names with a leading unique integer starting at 1, set *indexed_filenames=True*.

**Example**

    meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_dir="/Users/thisUser/Desktop/folderForGraphs", indexed_filenames=True)


**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.graph_disorder_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_dir="/Users/thisUser/Desktop/folderForGraphs", legacy=True)


### Generating AlphaFold2 Confidence Score Graphs from fasta files

By using the ``graph_pLDDT_fasta`` function, you can graph predicted AlphaFold2 pLDDT confidence scores for the amino acid sequences in a .fasta file. This works the same as ``graph_disorder_fasta`` but instead returns graphs with just the predicted AlphaFold2 pLDDT scores.

**Example**

	meta.graph_pLDDT_fasta("/Users/thisUser/Desktop/coolSequences.fasta", output_dir="/Users/thisUser/Desktop/folderForGraphs")


### Generating Predicted Disorder Graphs Using Uniprot ID

By using the ``graph_disorder_uniprot`` function, you can graph predicted consensus disorder values for the amino acid sequence of a protein by specifying the Uniprot ID. 

**Example**

    meta.graph_disorder_uniprot("Q8N6T3")

This function carries all of the same functionality as ``graph_disorder`` including specifying disorder_threshold, title of the graph, the DPI, and whether or not to save the output.

**Example**

    meta.graph_disorder_uniprot("Q8N6T3", disorder_threshold=0.5, title="my protein", DPI=300, output_file="/Users/thisUser/Desktop/my_cool_graph.png")

**Additional usage**

**Adding Predicted AlphaFold2 Confidence Scores -**
To add predicted AlphaFold2 pLDDT confidence scores, simply specify *pLDDT_scores=True*.

**Example**

	meta.graph_disorder_uniprot("Q8N6T3", pLDDT_scores=True)


**Using the original metapredict predictor**
To use the original metapredict predictor as opposed to our new, updated predictor, set ``legacy=True``

	meta.graph_disorder_uniprot("Q8N6T3", legacy=True)


### Generating AlphaFold2 Confidnce Score Graphs Using Uniprot ID

Just like with disorder predictions, you can also get AlphaFold2 pLDDT confidence score graphs using the Uniprot ID. This will **only display the pLDDT confidence scores** and not the predicted disorder scores. 

**Example**

	meta.graph_pLDDT_uniprot("Q8N6T3")



###  Predicting Disorder Domains from external scores:

The ``predict_disorder_domains_from_external_scores()`` function takes in an disorder scores, an amino acid sequence (optinally), and returns a DisorderObject. This function lets you use other disorder predictor scores and still use the predict_disorder_domains() functionality. The DisorderObject has 6 dot variables that can be called to get information about your input sequence. They are as follows: 

.sequence : str    
    Amino acid sequence 

.disorder : list or np.ndaarray
    Hybrid disorder score

.disordered_domain_boundaries : list
    List of domain boundaries for IDRs using Python indexing

.folded_domain_boundaries : list
    List of domain boundaries for folded domains using Python indexing

.disordered_domains : list
    List of the actual sequences for IDRs

.folded_domains : list
    List of the actual sequences for folded domains

**Examples**

	seq = meta.predict_disorder_domains_from_external_scores(disorder=[0.8577, 0.9313, 0.9313, 0.9158, 0.8985, 0.8903, 0.8895, 0.869, 0.8444, 0.8594, 0.8643, 0.8605, 0.8697, 0.8627, 0.8641, 0.8633, 0.8487, 0.8512, 0.8236, 0.8079, 0.8047, 0.8021, 0.7954, 0.7867, 0.7797, 0.7982, 0.7842, 0.7614, 0.7931, 0.8166, 0.8298, 0.8222, 0.8227, 0.8183, 0.8279, 0.838, 0.8535, 0.8512, 0.8464, 0.8469, 0.8322, 0.8265, 0.794, 0.7827, 0.7699, 0.7575, 0.7178, 0.5988], sequence = 'MKAPSNGFLPSSNEGEKKPINSQLMKAPSNGFLPSSNEGEKKPINSQL')

Now we can call the various dot values for **seq**. 

**Getting the sequence**

	print(seq.sequence)

returns

	MKAPSNGFLPSSNEGEKKPINSQLMKAPSNGFLPSSNEGEKKPINSQL


**Getting the disorder scores**

	print(seq.disorder)



**Getting the disorder domain boundaries**

	print(seq.disordered_domain_boundaries)



**Getting the folded domain boundaries**

	print(seq.folded_domain_boundaries)


**Getting the disordered domain sequences**

	print(seq.disordered_domains)


**Getting the folded domain sequences**

	print(seq.folded_domains)



**Additional Usage**

**Altering the disorder theshhold -**
To alter the disorder theshold, simply set *disorder_threshold=my_value* where *my_value* is a float. The higher the treshold value, the more conservative metapredict will be for designating a region as disordered. Default = 0.42

**Example**

	meta.predict_disorder_domains_from_external_scores("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", disorder_threshold=0.3)

**Altering minimum IDR size -**
The minimum IDR size will define the smallest possible region that could be considered an IDR. In other words, you will not be able to get back an IDR smaller than the defined size. Default is 12.

**Example**

	meta.predict_disorder_domains_from_external_scores("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_IDR_size = 10)

**Altering the minimum folded domain size -**
The minimum folded domain size defines where we expect the limit of small folded domains to be. *NOTE* this is not a hard limit and functions more to modulate the removal of large gaps. In other words, gaps less than this size are treated less strictly. *Note* that, in addition, gaps < 35 are evaluated with a threshold of 0.35 x disorder_threshold and gaps < 20 are evaluated with a threshold of 0.25 x disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which are IDRs in isolation) often show up with reduced apparent disorder within IDRs but can be as short as 20-30 residues. The folded_domain_threshold is used based on the idea that it allows a 'shortest reasonable' folded domain to be identified. Default=50.

**Example**

	meta.predict_disorder_domains_from_external_scores("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", minimum_folded_domain = 60)

**Altering gap_closure -**
The gap closure defines the largest gap that would be closed. Gaps here refer to a scenario in which you have two groups of disordered residues seprated by a 'gap' of not disordered residues. In general large gap sizes will favour larger contiguous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps are increasingly rare. Default=10.

**Example**

	meta.predict_disorder_domains_from_external_scores("MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLV", gap_closure = 5)


### metapredict isn't working!

I have recieved occassional feedback that metapredict is not working for a user. A common problem is that the user is using a different version of Python than metapredict was made on. metapredict was made using Python version 3.7, and I recommend using this version while using metapredict to avoid problems (I haven't done extensive testing using other versions of Python, so if you're not using 3.7, do so at your own risk). A convenient workaround is to use a conda environment that has Python 3.7 set as the default version of Python. For more info on conda, please see https://docs.conda.io/projects/conda/en/latest/index.html

Once you have conda installed, simply use the command 

	conda create --name my_env python=3.7

where you can replace the name of your environment with whatever you'd like. Then, use metapredict from within this conda environment.

If you are having other problems, please report them to the **issues** section on the metapredict Github page at
https://github.com/idptools/metapredict/issues

### Known Installation/Execution Issues

Below we include documentation on known issues. 

macOS libiomp clash 

PyTorch current ships with its own version of the OpenMP library (``libiomp.dylib``). Unfortunately when numpy is installed from ``conda`` (although not from ``pip``) this leads to a collision because the ``conda``-derived numpy library also includes a local copy of the ``libiomp5.dylib`` library. This leads to the following error message (included here for google-ability).


   OMP: Error #15: Initializing libiomp5.dylib, but found libomp.dylib already initialized.
   OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. 
   That is dangerous, since it can degrade performance or cause incorrect results. The best thing to 
   do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static 
   linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you 
   can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, 
   but that may cause crashes or silently produce incorrect results. For more information, 
   please see http://www.intel.com/software/products/support/.

To avoid this error we make the executive decision to ignore this clash. This has largely not appeared to have any deleterious issues on performance or accuracy accross the tests run. If you are uncomfortable with this then the code in ``metapredict/__init__.py`` can be edited with ``IGNORE_LIBOMP_ERROR`` set to ``False`` and **metapredict** re-installed from the source directory.

### Testing

To see if your installation of **metapredict** is working properly, you can run the unit test included in the package by navigating to the metapredict/tests folder within the installation directory and

**running:**

    $ pytest -v


### Example Datasets

Example data that can be used with metapredict can be found in the metapredict/data folder on GitHub. The example data set is just a .fasta file containing 5 protein sequences.


### Recent changes

This section is a log of recent changes with metapredict. My hope is that as I change things, this section can help you figure out why a change was made and if it will break any of your current work flows. The first major changes were made for the 0.56 release, so tracking will start there. Reasons are not provided for bug fixes for because the reason can assumed to be fixing the bug...


#### V2.0

Changes:
Massive update to the network behind metapredict to improve accuracy. Implementation of code to keep the original network accessible to users. Changes to predict_disorder_domain functions where a DisorderObject is no returned and access to values are used by calling properties from the generated object. Graphing functionality updated to accomadate new cutoff value for the new network at 0.5. If the original metapredict network is used, then the cutoff value automatically resets to the original value of 0.3. Tests updated. Added metapredict-predict-idrs command to the command line. Added ability to predict disorder domains from python using external scores.


#### V1.51

Changes:
Updated to require V1.0 of alphaPredict for pLDDT scores. This improves accuracy from over 9% per residue to about 8% per residue for pLDDT score predictions. Documentation was updated for this change.


#### V1.5

Changes:
Fixed bug causing some functions to fail when getting sequences from Uniprot.
Added information on citing metapredict because the final publication went live.


#### V1.4

Change:
For clarity, previous functions that used the term 'confidence' such as *graph_confidence_uniprot()* were changed to use the term pLDDT rather than confidence. This is to clarify that the confidence scores are AlphaFold2 pLDDT confidence scores and not scores to reflect the confidence that the user should have in the metapredict disorder prediction. For command-line usage where confidence scores are optional (such as metapredict-graph-disorder), when a *-c* or *--confidence* flag used to be used, now a *-p* or *--pLDDT* flag is used to graph confidence scores. This is similarly reflected in Python where now you must use *pLDDT_scores=True* instead of *confidence_scores=True*.

#### V1.3

Change:
Added functionality to generate predicted AlphaFold2 pLDDT confidence scores. Can get scores or generate graphs from Python or command-line. Can also generate graphs with both predicted disorder and predicted pLDDT confidence scores. Also added functionality to predict disorder domains using scores from a different disorder predictor. 

#### V1.2

Change:
Major update. Changed some basic functionality. Made it such that you don't need to specify to save (for disorder prediction values or graphs). Rather, if a file path is specified, the files will be saved. Updated graphing functionality to allow for specifying the disorder cutoff line and to allow users to highlight various regions of the graph. Changed import such that you can now just use import metapredict as meta in Python (as opposed to import metapredict and then from metapredict import meta). Lots of backend changes to make metapredict more stable. Added additional testing. Updated documentation. Standardized file reading/writing. Made it so user can specify file type of saved graphs. Added backend meta_tools.py to handle the busywork. Changed version numbering for networks. Updated code to avoid OMPLIB issue (known bug in previous versions). Updated all command-line tools to match backend code.

#### V1.1

Change:
Fixed some bugs.

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

We would like to thank the **DeepMind** team for developing AlphaFold.

We would also like to thank the team at MobiDB for creating the database that was used to train this predictor. Check out their awesome stuff at [https://mobidb.bio.unipd.it](https://mobidb.bio.unipd.it)

Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.3.
