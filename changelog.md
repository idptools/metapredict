## Changelog
This section is a log of recent changes with metapredict. My hope is that as I change things, this section can help you figure out why a change was made and if it will break any of your current workflows. The first major changes were made for the 0.56 release, so tracking will start there. Reasons are not provided for bug fixes for because the reason can assumed to be fixing the bug...

#### V3.0.1 (November 2024)
Changes:

* Fixed bug that caused memory issues when running many predictions.


#### V3.0 (November 2024)
Changes:

* Made the default pLDDT prediction network V2

* Removed alphaPredict as a dependency

* Made the default disorder prediction network V3

* Updated user-facing pLDDT predictions to allow specification of pLDDT network

* Added compatibility for doing batch predictions of pLDDT

* Added new pLDDT prediction network (V2)

* Overhaul of backend to accomadate pytorch-lightning architecture

* Massive change to how predictor is implemented. You can now do batch prediction on CPU, GPU (CUDA), or Mac GPU (MPS) for V1 (legacy), V2, and V3. 

* Update to user-facing docs to make changes of setting 'legacy=True' to specifying "version='V#'" when using different version of metapredict.

* Update to metapredict-uniprot to work with new version of getSequence. Allows for getting different protein isoforms if specified. 

* Update to how networks used in metapredict are tracked. Now everything needs to be added to /backend/network_parameters.py to maintain compatibility between old and future networks. 

* Reimplementation of pack-n-pad. Due to larger batch size in V3 network, it will likely be more useful to have fewer batches by using packing and padding instead of size collection under some scenarios. 

#### V2.65 (October 2024)
Changes:

* Changed tag to 2.65. Yep, that's it. Necessary to get a clean build up to Pypi.

#### V2.64 (October 2024)
Changes:

* Changed over to use pyproject.toml
* Removed max Python version of 3.12
* Changed alphaPredict to use 1.2 to get rid of Torch warning

#### V2.63 (November 2023)
Changes:

* Changed max version of Python compatibility to 3.11 because of issues in 3.12

* Changed line 207 in /backend/meta_predict_disorder.py from *output_values.append(round(float(i), 4))* to *output_values.append(round(float(i[0]), 4))* to git rid of Numpy deprecation warning when using Numpy 1.25 or later. Adding to change log in case this causes mayhem, but is passing all tests and additional local tests at this time so should be OK. 


#### V2.62 (metapredict V2-FF) (July 2023)
Changes:

* Made sure predictions used `torch.no_grad()`

* Removed torch dependency on < 2.0.

* Bug fix: When running `metapredict-predict-idrs` using `--mode shephard-domains` and `--mode shephard-domains-uniprot` in the 2.6 update, we accidentally return the start index of each IDR as the 0th indexed position, but SHEPHARD uses 1-index inclusive indexing. This has now been fixed.

* Bug fix: We discovered that when using torch 1.13.0 pack-n-pad (which is not the default and must be specifically requested) can lead to some small numerical inaccuracies in disorder predictions (<0.01). The reason this can be problematic is that it MAY alter the boundary between a disordered and folded domain when compared to the single iterative analysis. This issue is fixed in torch 2.0.1 and as such we now internally require torch 2.0.1 if pack-n-pad is going to be used, otherwise we fall back to size-collect. Note that this approach avoids a hard dependency on torch 2.0.1. To be clear, using pack-n-pad is currently impossible from the command line and would require someone to explicitly have requested it from the API.

#### V2.61 (metapredict V2-FF) (July 2023)
Changes:


* Renamed batch algorithms from mode 1 and mode 2 to size-collect and pack-n-pad.

* Default batch mode is always `size-collect` which in most cases is faster and is always available. You can force `pack-n-pad`

#### V2.6 (metapredict V2-FF) (May 2023)
Changes:

* V2.6 represents an update of metapredict to a version we refer to as metapredict V2-FF. V2-F22 provides a dramatic improvement in prediction performance when `batch_mode()` is used. On CPUs, this provides a 5-20x improvement in performance. On GPUs, this enables proteome-wide prediction in seconds. 

* Removed explicit multicore support and replaced with implicit parallelization in via `batch_predict()`.

* `batch_predict()` is now called in non-legacy predict for `predict_disorder_fasta()`, and can also be called via a `predict_disorder_batch()` which can take either a list or dictionary of sequences. 

* From command-line tools, `metapredict-predict-idrs`, and `metapredict-predict-disorder` will also use batch mode if legacy=False (default), which as well as being much faster now provide a status bar.

* Note that this update adds `tqdm` as a dependency for metapredict


#### V2.5 (March 2023)
Changes:

* Added the first multicore support to metapredict. Currently limited to metapredict-predict-disorder functionality.


#### V2.4.3
Changes:

* Updated the default names for `metapredict-predict-idrs` so that the FASTA output file is now called `idrs.fasta` instead of the inappropriate `shephard_idrs.tsv`.
* Added link to the new batch-mode Google Colab notebook!

#### V2.4.2 
Changes:

* Merged pull request from @FriedLabJHU to make f-strings more Pythonic. Thanks!!
* Changed `return_normalized` keyword to `normalized` in `meta.predict_pLDDT()` for consistency with other functions
* Added sanity check in case a passed sequence is an empty string (h/t Broder Schmidt)
* Added docs for the mode keyword in `meta.percent_disorder()`, so this is actually obvious to understand (h/t Broder Schmidt)
* Added several additional tests and updated the docs

#### V2.4.1
Changes:

* Some minor bug fixes and updates to code 

#### V2.3 
Changes:

* Merged pull request from @FriedLabJHU to fix keyword name `cutoff` to `disorder_threshold` in `meta.percent_disorder()`. Thanks!!

* Added the `mode` keyword into `meta.percent_disorder()` so disorder can be predicted in terms of what percentage of residues fall within IDRs, as well as what percent are above some fixed threshold.

#### V2.2

Changes: 
Fixed bug in metapredict-name command that could result in the organism name being named twice in the title of the graph.

#### V2.1

Changes:
Added functionality to graph the disorder of a protein by specifying its common name using the *metapredict-name* command.


#### V2.0

Changes:
Massive update to the network behind metapredict to improve accuracy. Implementation of code to keep the original network accessible to users. Changes to predict_disorder_domain functions where a DisorderObject is no returned and access to values are used by calling properties from the generated object. Graphing functionality updated to accommodate new cutoff value for the new network at 0.5. If the original metapredict network is used, then the cutoff value automatically resets to the original value of 0.3. Tests updated. Added metapredict-predict-idrs command to the command line. Added ability to predict disorder domains from python using external scores.


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
The output for `.csv` files will now have a comma space between each value instead of just a comma.

Reason:
Improve readability.

