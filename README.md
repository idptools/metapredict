# metapredict: A machine learning-based tool for predicting protein disorder.
### Last updated April 2024

## Current version: metapredict V3 (V3.0)
The current recommended and default version of metapredict is metapredict V3 (version 3.0). There are major changes to how metapredict V3 works behind the scenes *and a new (and from our benchmarks more accurate) network*. For this update, we did try to make sure everything we have is backwards compatible. If you have any compatibility issues, let us know! 

## What is new with V3?
1. **A new disorder prediction network**: We have trained a new disorder prediction network for metapredict V3, which is more accurate than our previous networks.
2. **A new pLDDT prediction network**: metapredict used to rely on an external package called alphaPredict for pLDDT prediction. This same network is still available in metapredict, but with additional data availability and more computational power, we made a new (and by all metrics better) network for pLDDT prediction!
3. **Easier batch predictions**: V2 previously required you to use `predict_disorder_batch()` to take advantage of the 10-100x improvement in prediction speed on CPUs and GPUs. However, you can now use a single function - `predict_disorder()` - on individual sequences, lists of sequences, and dictionaries of sequences, and metapredict will automatically take care of the rest for you while automatically doing batch predictions if more than 1 sequence is present.
4. **Batch prediction for all**: Previously, batch predictions were only available for the V2 disorder prediction network of metapredict. Now, you can do batch predictions using all of the disorder prediction networks - v1 (legacy), v2, and v3!
5. **Batch pLDDT predictions**: Batch predictions (and therefore the massive speedups) are now available for pLDDT predictions using the `predict_pLDDT()` function. 
6. **More robust device selection**: Newer versions of Torch (>2.0) support MacOS GPU utilization through the Metal Performance Shaders (MPS) framework, so you can now choose to use *mps* on MacOS. In addition, if you try to specify using a GPU and it does not work, metapredict will not automatically fall back to CPU. 


## Installation

**Note -** metapredict V3 cannot currently be installed using Pip. Please see the **V3 installation** section below install metapredict v3!

### V3 installation

To install metapredict V3, you will need to first install numpy and cython and then install the V3 branch of metapredict. First run:

	conda install -c conda-forge -c pytorch python=3.11 numpy pytorch scipy cython matplotlib
	

after numpy and cython install, run:

	pip install git+https://github.com/idptools/metapredict@v3


**V3 is currently not the version of metapredict on readthedocs, so documentation for V3 will be below. There are some important changes to V3:**
  
*Changes in metapredict V3:*
* When using metapredict V3 from python, you can choose the version of metapredict by specifying ``version``
* For all predictions (single sequences, lists of sequences, and dictionaries of sequences), whe using Python, use the ``meta.predict_disorder()`` function. 
* For CAID, we have a custom Python function and a command-line script. They both take in a .fasta formatted file of sequences as the input and output a a 'CAID compliant' formatted file per sequence in the .fasta file that will save to a specified output directory. In Python, this function is called ``meta.predict_disorder_caid()``. From the command-line, you can use ``metapredict-caid``. Documetation is below. If you don't want to use those specific functions, we also have documentation for predicting disorder from Python or from the command-line below. CAID documentation is after the sections on using metapredict V3 in Python or from the command-line. 

#### V3 Python usage examples -

First, import metapredict:

```python: 
import metapredict as meta
```

Disorder prediction:

**Single sequence predictions using ``meta.predict_disorder()``**  

```python: 
meta.predict_disorder("DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR")
```

```python: 
array([0.8173, 0.8311, 0.8276, 0.8193, 0.8036, 0.7832, 0.7485, 0.708 ,0.6778, 0.64, 0.5948, 0.5439, 0.5062, 0.47, 0.448 , 0.4356, 0.412 , 0.3687, 0.3294, 0.2986, 0.2724, 0.2543, 0.238, 0.227, 0.2185, 0.2084, 0.1846, 0.1665, 0.1559, 0.1373, 0.124 , 0.1133, 0.0958, 0.0738], dtype=float32)
```

**Predicting lists of sequences using ``meta.predict_disorder()``**  

```python: 
sequences=['GSGSGSGSSGSGSGS', 'DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR']
meta.predict_disorder(sequences)
```

```python: 
[['GSGSGSGSSGSGSGS', array([0.8916, 0.9393, 0.9505, 0.9596, 0.9618, 0.9639, 0.9623, 0.9589, 0.9517, 0.9371, 0.917, 0.8955, 0.8827, 0.8773, 0.8686],dtype=float32)], ['DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR', array([0.8173, 0.8311, 0.8276, 0.8193, 0.8036, 0.7832, 0.7485, 0.708, 0.6778, 0.64, 0.5948, 0.5439, 0.5062, 0.47, 0.448, 0.4356, 0.412, 0.3687, 0.3294, 0.2986, 0.2724, 0.2543, 0.238, 0.227, 0.2185, 0.2084, 0.1846, 0.1665, 0.1559, 0.1373, 0.124, 0.1133, 0.0958, 0.0738], dtype=float32)]]
```

**Predicting dictionaries of sequences using meta.predict_disorder()**  

```python: 
sequences={'seq1':'GSGSGSGSSGSGSGS', 'seq2':'DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR'}
meta.predict_disorder(sequences)
```

```python: 
{'seq1': ['GSGSGSGSSGSGSGS', array([0.8916, 0.9393, 0.9505, 0.9596, 0.9618, 0.9639, 0.9623, 0.9589, 0.9517, 0.9371, 0.917, 0.8955, 0.8827, 0.8773, 0.8686], dtype=float32)], 'seq2': ['DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR', array([0.8173, 0.8311, 0.8276, 0.8193, 0.8036, 0.7832, 0.7485, 0.708, 0.6778, 0.64, 0.5948, 0.5439, 0.5062, 0.47, 0.448, 0.4356, 0.412, 0.3687, 0.3294, 0.2986, 0.2724, 0.2543, 0.238, 0.227, 0.2185, 0.2084, 0.1846, 0.1665, 0.1559, 0.1373, 0.124, 0.1133, 0.0958, 0.0738], dtype=float32)]}
```

**Choosing a specific version of metapredict using meta.predict_disorder()**  

To choose a specific version of metapredict, simply specify ``version``.

**V1, AKA metapredict legacy**
  
```python: 
meta.predict_disorder("DSSPEAPAEPPKDVP", version='v1')
```
  
**V2**
  
```python: 
meta.predict_disorder("DSSPEAPAEPPKDVP", version='v2')
```
  
**V3, (new default, do not need to specify)**
  
```python: 
meta.predict_disorder("DSSPEAPAEPPKDVP", version='v3')
```

#### V3 command-line usage examples - 

Metapredict can predict disorder for sequences from a .fasta formatted file using ``metapredict-predict-disrder``  the command-line.

Once metapredict is installed, you can run ``metapredict-predict-disorder`` from the command line:

```bash: 
metapredict-predict-disorder <Path to .fasta file> 
```
**Example:** 

```bash:
metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta 
```

Note that as of metapredict V3, all three networks can be submitted in batch for massive increases in prediction speed. Further, metapredict will automatically use a CUDA GPU if available. A progress bar will also be generated in the terminal.

**Additional Usage:**

**Specifying where to save the output -** 

If you would like to specify where to save the output, simply use the ``-o`` or ``--output-file`` flag and then specify the file path and file name. By default this command will save the output file as disorder_scores.csv to your current working directory. However, you can specify the file name in the output path.

**Example:** 

```bash:
metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv
```

**Using the other versions of metapredict -**

To use legacy (V1) or V2 of metapredict, simply use the ``-v`` or ``--version`` flag.

**Example:** 

```bash:
metapredict-predict-disorder /Users/thisUser/Desktop/interestingProteins.fasta -o /Users/thisUser/Desktop/disorder_predictions/my_disorder_predictions.csv -v v2
```

#### CAID formatted predictions from the command-line

To get CAID formatted predictions per sequence from the command-line, use ``metapredict-caid``. There are 3 required arguments:
 1. `data_file` - the path to the .fasta file
 2. `output_path` - the path of where to save each CAID formatted prediction file. This should be a directory. Each sequence in the .fasta file will generate a file in this directory where the name of the file will be the sequence header and the file extension will be .caid.
 3. `version` - the version of metapredict to use.

The files generated are in .caid format where each sequence header is the first line then the following lines for that sequence are tab separated and contain:
 1. The amino acid number
 2. The amino acid letter
 3. The metapredict disorder score
 4. The binarized metapredict score where 1=disordered and 0=not disordered.
  

**Examples**

**V1, AKA metapredict legacy**
 
```bash
metapredict-caid /Users/thisUser/Desktop/myCaidSeqs.fasta /Users/thisUser/Desktop/CaidPredictions/metapredictV1 v1
```
  
  
**V2:**
 
```bash
metapredict-caid /Users/thisUser/Desktop/myCaidSeqs.fasta /Users/thisUser/Desktop/CaidPredictions/metapredictV2 v2
```
  

**V3**
 
```bash
metapredict-caid /Users/thisUser/Desktop/myCaidSeqs.fasta /Users/thisUser/Desktop/CaidPredictions/metapredictV3 v3
```


#### CAID formatted predictions from Python

To get CAID formatted predictions in Python, use the `predict_disorder_caid()` function. This function takes in the path to a .fasta formatted file of sequences and returns a 'CAID compliant' formatted file per sequence that is in the fasta file. The files generated are in .caid format where each sequence header is a line then the following lines for that sequence are tab separated and contain:
 1. The amino acid number
 2. The amino acid letter
 3. The metapredict disorder score
 4. The binarized metapredict score where 1=disordered and 0=not disordered.
  

To use this function, first import metapredict

```python:
import metapredict as meta
```

The function takes in three arguments: 
 1. `input_fasta` - the path to the .fasta file
 2. `output_path` - the path of where to save each CAID formatted prediction file. This should be a directory. Each sequence in the .fasta file will generate a file in this directory where the name of the file will be the sequence header and the file extension will be .caid.
 3. `version` - the version of metapredict to use.

The disorder cutoff values are handled automatically (0.42 for V1 and 0.5 for V2/V3).

**Examples**

**V1, AKA metapredict legacy**
 
```python: 
path_to_fasta='/Users/thisUser/Desktop/myCaidSeqs.fasta'
``` 

```python: 
meta.predict_disorder_caid(path_to_fasta, '/Users/thisUser/Desktop/CaidPredictions/metapredictV1, version='v1')
```
  
**V2**
  
 
```python: 
path_to_fasta='/Users/thisUser/Desktop/myCaidSeqs.fasta'
``` 

```python: 
meta.predict_disorder_caid(path_to_fasta, '/Users/thisUser/Desktop/CaidPredictions/metapredictV2, version='v2')
```
  
**V3, (new default, do not need to specify)**
  
 
```python: 
path_to_fasta='/Users/thisUser/Desktop/myCaidSeqs.fasta'
``` 

```python: 
meta.predict_disorder_caid(path_to_fasta, '/Users/thisUser/Desktop/CaidPredictions/metapredictV3, version='v3')
```

### Installing metapredict V2 (not needed if you install V3)

The current stable version of **metapredict** is available through GitHub or the Python Package Index (PyPI). 

To install from PyPI, run:

	pip install metapredict


You can also install the current development version from

	pip install git+https://git@github.com/idptools/metapredict

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

	git clone https://github.com/idptools/metapredict.git
	cd metapredict
	pip install -e .
	
Note you will need the -e flag to ensure the `cython` code compiles correctly, but this also means the installed version is linked to the local version of the code.	

This will install **metapredict** locally. If you modify the source code in the local repository, be sure to re-install with `pip`.

## Documentation
Documentation for metapredict V2 automatically builds from the `/doc` directory in this repository and is hosted at [https://metapredict.readthedocs.io/](https://metapredict.readthedocs.io/). 

In brief, metapredict provides both command-line tools and a set of user-face functions from the metapredict python module. Both sets of tools are fully documented online.

## How can I use metapredict?
Metapredict can be used in four different ways:

1. As a stand-alone command-line tool (installable via pip - the code in this repository).
2. As a Python library for integrating into your favorite bioinformatics pipeline (installable via pip - the code in this repository).
3. As a web-server for examining disorder predictions on individual sequences found at [https://metapredict.net/](https://metapredict.net/).
4. *NEW as of August 2022:* as a Google Colab notebook for batch-predicting disorder scores for larger numbers of sequences: [**LINK HERE**](https://colab.research.google.com/github/idptools/metapredict/blob/master/colab/metapredict_colab.ipynb). Performance-wise, batch mode can predict the entire yeast proteome in ~1.5 min.
5. *NEW as of May 2023:* as part of the [ALBATROSS paper](https://www.biorxiv.org/content/10.1101/2023.05.08.539824), we provide a colab notebook for predicting IDRs on a proteome-wide scale [**LINK HERE**](https://colab.research.google.com/github/holehouse-lab/ALBATROSS-colab/blob/main/idrome_constructor/idrome_constructor.ipynb).

## How to cite

If you use metapredict for your work, please cite the metapredict paper: 
 
Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophys. J. 120, 4312–4319 (2021).

Note that in addition to the original paper, there's a V2 preprint; HOWEVER, we ask you only cite the original paper and describe the version being used (V1, V2, V2-FF, or V3).

We are hoping to get a paper out for V3 in the near future (if we already have, then we just forgot to delete this sentence)...

Emenecker, R. J., Griffith, D. & Holehouse, A. S. Metapredict V2: An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure. bioRxiv 2022.06.06.494887 (2022). doi:10.1101/2022.06.06.494887## Changes

## Changes

For changes see the `changelog.md` file in this directory.

## Acknowledgements

PARROT, created by Dan Griffith, was used to generate the network used for metapredict. See [https://pypi.org/project/idptools-parrot/](https://pypi.org/project/idptools-parrot/) for some very cool machine learning stuff.

In addition to using Dan Griffith's tool for creating metapredict, the original code for `brnn_architecture.py` and `encode_sequence.py` was written by Dan.

We would like to thank the **DeepMind** team for developing AlphaFold and EBI/UniProt for making these data so readily available.

We would also like to thank the team at MobiDB for creating the database that was used to train this predictor. Check out their awesome stuff at [https://mobidb.bio.unipd.it](https://mobidb.bio.unipd.it)

## Copyright
Copyright (c) 2020-2023, Holehouse Lab - Washington University School of Medicine



