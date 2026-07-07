.. metapredict documentation master file, created by
   sphinx-quickstart on Thu Mar 15 13:55:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

metapredict
===========

**metapredict** is a fast, accurate, and easy-to-use predictor of intrinsic protein disorder. Given an amino acid sequence, metapredict returns a per-residue disorder score between 0 and 1 that reflects how likely each residue is to be disordered. It can also carve a sequence into discrete intrinsically disordered regions (IDRs) and folded domains, and it can generate predicted AlphaFold2 pLDDT confidence scores.

metapredict is distributed as a Python package that provides both a Python application programming interface (API) and a set of command-line tools for working with FASTA files. It is also available as a `webserver <https://metapredict.net>`_ for single-sequence prediction and as a `Google Colab notebook <https://colab.research.google.com/drive/1UOrOxun9i23XDE8lFo_4I89Tw8P3Z1D-?usp=sharing>`_ for large-scale batch prediction. To install metapredict and start making predictions, see :doc:`getting_started`.


How does metapredict work?
--------------------------

metapredict uses a deep-learning network to generate per-residue disorder scores directly from amino acid sequence. The name reflects the original training strategy: metapredict V1 was trained to reproduce the *consensus* disorder assigned by a panel of independent disorder predictors (as compiled by `MobiDB <https://mobidb.bio.unipd.it/>`_), so each score approximates what a collection of predictors would agree on — things got pretty "meta", hence the name.

Later networks build on this idea. V2 combines the V1 consensus disorder signal with predicted AlphaFold2 pLDDT scores, while V3 — the current default and most accurate network — combines consensus disorder with *experimental* AlphaFold2 pLDDT scores trained on a much larger dataset. All three networks remain available, and V3 is a drop-in replacement for the earlier versions. A more detailed description of each network is given in :doc:`getting_started`.

Because metapredict is a lightweight sequence-based network, it is also extremely fast — it can predict disorder for entire proteomes in minutes on a CPU and in seconds on a GPU, with no length limit on the sequences it can handle.


How to cite
-----------

If you use metapredict in your work, please cite the original metapredict paper and state which version of metapredict you used (V1, V2, V2-FF, or V3):

    Emenecker, R. J., Griffith, D. & Holehouse, A. S. metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure. Biophysical Journal 120, 4312–4319 (2021). doi:10.1016/j.bpj.2021.08.039

You may additionally cite the preprints describing later updates to metapredict; see the :doc:`how_to_cite` page for the full list.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   usage/command-line
   usage/using-in-python
   usage/api
   usage/acknowledgements
   usage/troubleshooting
   changes
   how_to_cite
