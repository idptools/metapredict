Recent changes
================================

About
------

This section is a log of recent changes with metapredict. My hope is that as I change things, this section can help you figure out why a change was made and if it will break any of your current work flows. The first major changes were made for the 0.56 release, so tracking will start there.


V2.4.2 
---------

Changes:

* Integrated in changes from @FriedLabJHU to make f-strings more Pythonic
* Changed ``return_normalized`` keyword to ``normalized`` in ``meta.predict_pLDDT()`` for consistency with other functions
* Added sanity check in case a passed sequence is an empty string (h/t Broder Schmidt)
* Added docs for the mode keyword in `meta.percent_disorder()`, so this is actually obvious to understand
* Added several additional tests and updated the docs.

V2.4.1
---------

Changes:

* Some minor bug fixes and updates to code 

V2.3 
---------

Changes:

* Merged pull request from @FriedLabJHU to fix keyword name `cutoff` to `disorder_threshold` in `meta.percent_disorder()`. Thanks!!

* Added the `mode` keyword into `meta.percent_disorder()` so disorder can be predicted in terms of what percentage of residues fall within IDRs, as well as what percent are above some fixed threshold.

V2.2
-----

Changes: 
Fixed bug in metapredict-name command that could result in the organism name being named twice in the title of the graph.


V2.1
------
Changes:
Added functionality to graph the disorder of a protein by specifying its common name using the *metapredict-name* command.


V2.0
-----
Changes:
Massive update to the network behind metapredict to improve accuracy. Implementation of code to keep the original network accessible to users. Changes to predict_disorder_domain functions where a DisorderObject is no returned and access to values are used by calling properties from the generated object. Graphing functionality updated to accomadate new cutoff value for the new network at 0.5. If the original metapredict network is used, then the cutoff value automatically resets to the original value of 0.3. Tests updated.


V1.51
-----
Changes:
Updated to require V1.0 of alphaPredict for pLDDT scores. This improves accuracy from over 9% per residue to about 8% per residue for pLDDT score predictions. Documentation was updated for this change.



V1.5
-----
Changes:
Fixed bug causing some functions to fail when getting sequences from Uniprot.
Added information on citing metapredict because the final publication went live.


V1.4
-----
Change:
For clarity, previous functions that used the term 'confidence' such as *graph_confidence_uniprot()* were changed to use the term pLDDT rather than confidence. This is to clarify that the confidence scores are AlphaFold2 pLDDT confidence scores and not scores to reflect the confidence that the user should have in the metapredict disorder prediction. For command-line usage where confidence scores are optional (such as metapredict-graph-disorder), when a *-c* or *--confidence* flag used to be used, now a *-p* or *--pLDDT* flag is used to graph confidence scores. This is similarly reflected in Python where now you must use *pLDDT_scores=True* instead of *confidence_scores=True*.


V1.3
-----
Change:
Added functionality to generate predicted AlphaFold2 confidence scores. Can get scores or generate graphs from Python or command-line. Can also generate graphs with both predicted disorder and predicted confidence scores. Also added functionality to predict disorder domains using scores from a different disorder predictor. 


V.1.2
------
Change:
Major update. Changed some basic functionality. Made it such that you don't need to specify to save (for disorder prediction values or graphs). Rather, if a file path is specified, the files will be saved. Updated graphing functionality to allow for specifying the disorder cutoff line and to allow users to highlight various regions of the graph. Changed import such that you can now just use import metapredict as meta in Python (as opposed to import metapredict and then from metapredict import meta). Lots of backend changes to make metapredict more stable. Added additional testing. Updated documentation. Standardized file reading/writing. Made it so user can specify file type of saved graphs. Added backend meta_tools.py to handle the busywork. Changed version numbering for networks. Updated code to avoid OMPLIB issue (known bug in previous versions). Updated all command-line tools to match backend code.

V.1.1
------
Change:
Fixed some bugs.


V.1.0
------
Change:
Added functionality to generate graphs using a Uniprot ID as the input. Added functionality to predict disorder domains. 


V.061
------

Change:
Added functionality to predict or graph a disordered sequence from the command line by directly inputting the sequence. This can only do one sequence at a time and does not save the disorder values or graph. It is meant to provide a very quick and easy way to check something out.


V.060
------

Change:
Added functionality to specify the horizontal lines that appear across the graphs rather than only having the option of having the dashed lines appear at intervals of 0.2.
This functionality is in both Python and the command line.

V0.58
------

Change:
Updated the network with a newly trained network (using the same dataset as the original) that is slightly more accurate.

Reason:
I am always trying to find ways to make metapredict more accurate. When I manage to make the predictor better, I will update it.

V0.57
-------

Change:
Bug fix that could result in prediction values to six decimal places in some scenarios

Change:
Changed titles for graphs generated by ``metapredict-graph-disorder`` to be 14 characters instead of 10. This is reflected in the title graph and the saved files.

Reason:
The 10 character save file was occassionally the same for multiple proteins. This resulted in the inability to discern which protein corresponded to which graph and could result in overwriting previously generated graphs. The 14 characters should be long enough to keep unique names for all proteins being analyzed.

Change:
Fixed bug that could result in crashing due to short fasta headers.

V0.56
-------

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