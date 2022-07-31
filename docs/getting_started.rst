*********************************
Getting Started with metapredict
*********************************

What is metapredict?
====================
**metapredict** is a software tool to predict intrinsically disordered regions in protein sequences. It is provided as a downloadable Python tool that includes a Python application programming interface (API) and a set of command-line tools for working with FASTA files. 

Our goal in building **metapredict** was to develop a robust, accurate, and high-performance predictor of intrinsic disorder that is also easy to install and use. As such, **metapredict** is implemented in Python and can be installed directly via `pip` (see below).

**Important update** - as of February 15, 2022 we have updated metapredict to V2. This comes with important changes that improve the accuracy of metapredict. Please see the section on the update *Major update to metapredict predictions to increase overall accuracy* below. In addition, this update changes the functionality of the *predict_disorder_domains()* function, so please read the documentation on that function if you were using it previously. 

We recently released a `preprint <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_ documenting all these changes and more!

As well as providing a set of high-performance software tools, **metapredict** is provided as a stand-alone web server which can predict disorder profiles, scores, and contiguous IDRs for single sequences.

To access the web server go to `metapredict.net <http://metapredict.net/>`_. 

How does metapredict work?
===========================
**metapredict** is a bit different than your typical protein disorder predictor. Instead of predicting the percent chance that a residue within a sequence might be disordered, **metapredict** tries to predict the *consensus disorder* score for the residue. Consensus disorder reports on the fraction of independent disorder predictors that would predict a given residue as disordered.

This already seems complicated...
----------------------------------

**metapredict** is a deep-learning-based predictor trained on consensus disorder data from 8 different predictors, as pre-computed and provided by `MobiDB <https://mobidb.bio.unipd.it/>`_. Functionally, this means each residue is assigned a score between 0 and 1 which reflects the confidence we have that the residue is disordered (or not). If the score was 0.5, this means half of the predictors predict that residue to be disordered. In this way, **metapredict** can help you quickly determine the likelihood that residues are disordered by giving you an approximation of what other predictors would predict (things got pretty 'meta' there, hence the name **metapredict**).


Major update to metapredict predictions to increase overall accuracy
------------------------------------------------------------------------
We are always working to make metapredict better, and we have recently managed just that. More details will be below, but the short story is that we have made significant improvements in the accuracy of disorder predictions using metapredict. By analyzing our new network using the Disprot-PDB dataset predictions, we found that the MCC (which is a measurement accounting for false positives, false negatives, true positives, and true negatives) for metapredict increased from 0.588 for the old (original) network to 0.7 for our new network. To put this in perspective, our original network was ranked 12th most accurate when analyzing the Disprot-PDB dataset, and by our own estimates V2 is now ranked as the 2nd most accurate available predictor. 

For more information on the changes made please see our recent preprint:

Emenecker, R. J., Griffith, D., & Holehouse, A. S. (2022). Metapredict V2: 
`An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure.  <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_ In bioRxiv (p. 2022.06.06.494887). https://doi.org/10.1101/2022.06.06.494887

Any questions, please don't hesitate to reach out!


But wait! I need the old metapredict predictions!!!
====================================================
No worries! We left users access to the old network. The *default network is now our new, more accurate network*. However, by calling ``-l`` or ``--legacy`` from the command line or by specifying ``legacy=True`` from Python, you will be able to use the original metapredict network. We wanted to keep making metapredict better, but we also wanted to minimize disruptions to anyone currently relying on the original metapredict predictions for whatever reason.


So... how exactly was this more accurate metapredict network made?
=========================================================================
We didn't think it was possible, but metapredict has somehow become *even more meta*. Get ready, because things are about to get a little weird. When we implemented the AlphaFold2 pLDDT prediction feature (see section below), we noticed that there were occasional discrepancies between metapredict and the predicted pLDDT (ppLDDT) scores. When the ppLDDT scores get high enough, it is unlikely that a given region is actually disordered. So, we developed a version of metapredict that we originally called 'metapredict-hybrid' that essentially combined aspects of the ppLDDT scores and the original metapredict scores. We found that this 'hybrid predictor' was **much better** than the original metapredict disorder predictor at predicting disordered regions. **But we didn't stop there.** 

We think one of metapredicts best features is *it is really really fast*. This 'hybrid-predictor' was a little on the slow side, coming in at about 1/3 the speed of the original metapredict predictor. This is still VERY fast, but we thought we could do better. So, we took a little over 300,000 protein sequences and generated metapredict-hybrid scores for those sequences. We then fed those sequences and the corresponding metapredict-hybrid scores and generated a new bidirectional recurrent neural network (BRNN) using PARROT. We then tested this new network against the original metapredict-hybrid predictions and the original metapredict network. The new network that was trained on metapredict-hybrid scores *actually outperformed the metapredict-hybrid predictions when benchmarking against Disprot-PDB*. Importantly, this new (super accurate) network was only 30% slower than the original metapredict network, which is substantially better than the 70% hit that metapredict-hybrid took. 
 
**TL;DR** We made the original metapredict predictor using a network trained on consensus scores from MobiDB. We then trained a network on AlphaFold2 pLDDT scores. Next, we made a predictor that combined prediction values from the original metapredict predictor and the AlphaFold2 pLDDT predictor to make very accurate disorder predictions. Finally, we took hundreds of thousands of proteins, generated disorder prediction scores using the aforementioned combination of the original metapredict predictions and the AlphaFold2 predictions, and then trained our final network on those scores. **That's pretty dang meta.**


Generating AlphaFold2 pLDDT scores in metapredict
======================================================
In addition, metapredict offers predicted confidence scores from AlphaFold2. These predicted scores use a bidirectional recurrent neural network (BRNN) trained on the per residue pLDDT (predicted IDDT-Ca) confidence scores generated by AlphaFold2 (AF2). The confidence scores (pLDDT) from the proteomes of *Danio rerio*, *Candida albicans*, *Mus musculus*, *Escherichia coli*, *Drosophila melanogaster*, *Methanocaldococcus jannaschii*, *Plasmodium falciparum*, *Mycobacterium tuberculosis*, *Caenorhabditis elegans*, *Dictyostelium discoideum*, *Trypanosoma cruzi*, *Saccharomyces cerevisiae*, *Schizosaccharomyces pombe*, *Rattus norvegicus*, *Homo sapiens*, *Arabidopsis thaliana*, *Zea mays*, *Leishmania infantum*, *Staphylococcus aureus*, *Glycine max*, and *Oryza sativa* were used to generate the BRNN. These confidence scores measure the local confidence that AlphaFold2 has in its predicted structure. The scores go from 0-100 where 0 represents low confidence and 100 represents high confidence. For more information, please see: *Highly accurate protein structure prediction with AlphaFold* https://doi.org/10.1038/s41586-021-03819-2. In describing these scores, the team states that regions with pLDDT scores of less than 50 should not be interpreted except as *possible* disordered regions.


What might the predicted confidence scores from AlphaFold2 be used for?
========================================================================
These scores can be used for many applications such as generating a quick preview of which regions of your protein of interest AF2 might be able to predict with high confidence, or which regions of your protein *might* be disordered. AF2 is not (strictly speaking) a disorder predictor, and the confidence scores are not directly representative of protein disorder. Therefore, any conclusions drawn with regards to disorder from predicted AF2 confidence scores should be interpreted with care, but they may be able to provide an additional metric to assess the likelihood that any given protein region may be disordered.


Why is metapredict useful?
===========================
Consensus disorder scores are really useful as they distribute the biases and uncertainty associated with any specific predictor. However, a drawback of consensus disorder databases (like MobiDB) is that they can only give you values of *previously predicted protein sequences*. **metapredict** provides a way around this, allowing arbitrary sequences to be analyzed! 

The major advantages that **metapredict** offers over existing predictors is performance, ease of use, and ease of installation. Given **metapredict** uses a pre-trained bidirectional recurrent neural network, on hardware we've tested **metapredict** gives ~10,000 residues per second prediction power. This means that predicting disorder across entire proteomes is accessible in minutes - for example it takes ~20 minutes to predict disorder for every human protein in the reviewed human proteome (~23000 sequences). We provide **metapredict** as a simple-to-use Python library to integrate into existing Python workflows, and as a set of command-line tools for the stand-alone prediction of data from direct input or from FASTA files.


How to cite metapredict
===========================

If you use metapredict for your work, please cite the metapredict paper - 
 
Emenecker RJ, Griffith D, Holehouse AS, metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure, Biophysical Journal (2021), doi: https:// doi.org/10.1016/j.bpj.2021.08.039.

Additionally, if you are using V2 (which is now the default) please make this clear in methods section. You should not feel obliged to cite the `V2 preprint <https://www.biorxiv.org/content/10.1101/2022.06.06.494887v2>`_, and this pre-print exists soley so we could fully document the changes and test some edge cases in an accessible and clear way.


Installation
==============
**metapredict** is available through GitHub or the Python Package Index (PyPI). To install through PyPI, run

.. code-block:: bash

	$ pip install metapredict

To clone the GitHub repository and gain the ability to modify a local copy of the code, run

.. code-block:: bash

	$ git clone https://github.com/idptools/metapredict.git
	$ cd metapredict
	$ pip install .

This will install **metapredict** locally. If you modify the source code in the local repository, be sure to re-install with `pip`.

Known installation/execution issues
====================================

Below we include documentation on known issues. 

macOS libiomp clash 
=======================

PyTorch currently ships with its own version of the OpenMP library (``libiomp.dylib``). Unfortunately when numpy is installed from ``conda`` (although not from ``pip``) this leads to a collision because the ``conda``-derived numpy library also includes a local copy of the ``libiomp5.dylib`` library. This leads to the following error message (included here for google-ability).

.. code-block:: none 

   OMP: Error #15: Initializing libiomp5.dylib, but found libomp.dylib already initialized.
   OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. 
   That is dangerous, since it can degrade performance or cause incorrect results. The best thing to 
   do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static 
   linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you 
   can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, 
   but that may cause crashes or silently produce incorrect results. For more information, 
   please see http://www.intel.com/software/products/support/.

To avoid this error we make the executive decision to ignore this clash. This has largely not appeared to have any deleterious issues on performance or accuracy across the tests run. If you are uncomfortable with this then the code in ``metapredict/__init__.py`` can be edited with ``IGNORE_LIBOMP_ERROR`` set to ``False`` and **metapredict** re-installed from the source directory.

Testing
========

To see if your installation of **metapredict** is working properly, you can run the unit test included in the package by navigating to the metapredict/tests folder within the installation directory and running:

.. code-block:: bash

	$ pytest -v

Example datasets
==================

Example data that can be used with metapredict can be found in the metapredict/data folder on GitHub. The example data set is just a .fasta file containing 5 protein sequences.
