Frequently asked questions
==========================

How metapredict works
---------------------

What does a disorder score mean?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

metapredict gives every residue a score, between 0 and 1 by default, where higher scores mean the residue is more likely to be disordered. metapredict treats residues scoring above 0.5 as disordered (above 0.42 for the V1 network); this is the default ``disorder_threshold`` used to find IDRs and to calculate :code:`percent_disorder()`.

What the score represents depends on the network. V1 was trained to reproduce the consensus of eight disorder predictors from `MobiDB <https://mobidb.bio.unipd.it/>`_, so a score of 0.5 roughly means that half of those predictors would call the residue disordered. V2 and V3 were trained on a hybrid score that combines V1 consensus disorder with AlphaFold2 pLDDT scores (predicted pLDDT scores for V2, and the real pLDDT scores of AlphaFold2 structures, smoothed over a 25-residue window, for V3). See :doc:`getting_started` for more on how each network was trained.


Which network should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

V3, the default, is the most accurate network in our benchmarks, and we recommend it for new work. V1 (originally called "legacy") and V2 are still available, for example to reproduce earlier analyses: choose them with ``version=1`` or ``version=2`` in Python, or ``-v 1`` or ``-v 2`` on the command line. Note that V1 uses a lower default disorder threshold (0.42) than V2 and V3 (0.5). Whichever network you use, please report it when you cite metapredict.


Does metapredict use multiple sequence alignments or protein structures?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. metapredict only needs the amino acid sequence. Each residue is encoded as one of the 20 standard amino acids and passed through a small neural network (a bidirectional LSTM) that outputs one score per residue. This is why metapredict is fast enough to predict whole proteomes in minutes.


Does a residue's score depend on the rest of the sequence?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. The network reads the whole sequence in both directions, so each residue's score depends on the residues around it, near and far. As a result, the same region can get different scores when it is predicted on its own and when it is part of the full-length protein: for example, residues 1–100 of human p53 predicted on their own differ from the same residues predicted within full-length p53 by up to 0.28 (0.07 on average). For the most meaningful scores, predict full-length proteins and take the region you are interested in afterwards.


How does metapredict decide where the IDRs are?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`predict_disorder(..., return_domains=True)`, :code:`predict_disorder_domains()` and ``metapredict-predict-idrs`` split each sequence into IDRs and folded domains in four steps:

#. The disorder scores are smoothed (with a Savitzky–Golay filter over a window of about twice ``minimum_IDR_size``, so 23 residues by default) to remove residue-to-residue noise.
#. Residues whose smoothed score is above the disorder threshold are marked as disordered.
#. Short gaps of up to ``gap_closure`` residues (10 by default) between disordered stretches are filled in, and disordered stretches of ``minimum_IDR_size`` residues or fewer (12 by default) are discarded, so with the default settings the shortest IDR reported is 13 residues.
#. Short folded regions whose disorder is only somewhat below the threshold are merged into the IDRs around them: regions shorter than ``minimum_folded_domain`` (50 residues by default) whose average smoothed score is above 0.75 × the threshold, and regions shorter than 35 or 20 residues whose average is above 0.35 or 0.25 × the threshold. This stops short stretches of reduced disorder, such as coiled coils inside long IDRs, from splitting an IDR in two.

The result gives the start and end of every IDR and folded domain (using Python indexing) and their sequences. All of these settings can be changed; see :doc:`usage/using-in-python`. You can also apply the same algorithm to disorder scores from another predictor with :code:`predict_disorder_domains_from_external_scores()`.


What is the predicted pLDDT score, and how does it relate to disorder?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`predict_pLDDT()` predicts, from the sequence alone, the pLDDT score that AlphaFold2 would give each residue. pLDDT (0 to 100) is AlphaFold2's confidence in its own predicted structure, and the AlphaFold2 authors note that regions scoring below 50 should not be interpreted except as possible disorder. The default pLDDT network (V2) was trained on the pLDDT scores of AlphaFold2 (v4) structures of SwissProt proteins; V1 is the network from our earlier alphaPredict package.

AlphaFold2 is not a disorder predictor, so a low pLDDT score is a hint of disorder rather than a measure of it. If you want a disorder-like score anyway, ``return_as_disorder_score=True`` rescales the pLDDT so that scores of 35 or below become 1, scores of 95 or above become 0, and scores in between are scaled linearly.


Inputs and results
------------------

What happens to non-standard amino acids or lowercase letters?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lowercase letters are fine; sequences are converted to uppercase before prediction. Only the 20 standard amino acids can be predicted, so passing a sequence that contains anything else (for example ``X``, ``B``, ``U`` or ``*``) to :code:`predict_disorder()` or :code:`predict_pLDDT()` raises an error that names the residue.

The functions and command-line tools that read FASTA files instead convert non-standard residues by default (``invalid_sequence_action='convert'``, or ``--invalid-sequence-action`` on the command line), using protfasta's rules: ``B`` becomes ``N``, ``U`` becomes ``C``, ``X`` becomes ``G``, ``Z`` becomes ``Q``, and ``*``, ``-`` and spaces are removed. Other options let you skip such sequences or stop with an error instead; see the `protfasta documentation <https://protfasta.readthedocs.io/en/latest/read_fasta.html>`_.


Is there a minimum or maximum sequence length?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any sequence with at least one residue can be predicted (an empty sequence raises an error). For very short sequences, IDR detection works on the sequence as a whole: with the default settings, sequences shorter than 31 residues are reported as a single IDR if at least half of their residues score above the disorder threshold (with the default threshold of 0.5), and as a single folded domain otherwise.

There is no fixed maximum length on the CPU or on an Apple Silicon GPU; the limit is the memory available (see `Memory and batch size`_ below). On NVIDIA GPUs (CUDA), sequences can be at most 65,535 residues long, and metapredict stops with an error if a longer sequence is sent to a CUDA GPU. Predict such sequences on the CPU instead.


Why can the same sequence give slightly different scores?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because of floating-point rounding, scores can differ very slightly depending on where and how they were calculated:

* **Device.** CPUs, NVIDIA GPUs and Apple Silicon GPUs do the same calculation in slightly different ways. A single sequence is always predicted on the CPU, while a list or dictionary of sequences may run on a GPU, so predicting a sequence on its own and as part of a list can give slightly different scores.
* **Batch.** Which other sequences share a batch, and so the batch size, also changes scores very slightly (see `Memory and batch size`_ below).

These differences are tiny, but because scores are rounded to 4 decimal places by default they can occasionally change the last reported digit. On the same device, with the same settings and the same input sequences, predictions are exactly reproducible from one run to the next. If you need identical scores across different machines, predict on the CPU with ``device='cpu'`` (or ``-d cpu`` on the command line).


Why is a single sequence always predicted on the CPU?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For one sequence, the time it takes to move data to and from a GPU outweighs any gain from using it, so :code:`predict_disorder()` and :code:`predict_pLDDT()` always predict a single sequence (a string) on the CPU, even if you pass ``device``. To use a GPU, pass your sequences as a list or a dictionary; they are then predicted together in batches.


How can I check how fast metapredict is on my computer?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`print_performance()` times metapredict on random sequences and prints (and returns) the number of residues predicted per second:

.. code-block:: python

    import metapredict as meta

    meta.print_performance()                 # the default network and device
    meta.print_performance(device='cpu')     # a specific device
    meta.print_performance(version=1)        # a specific network

By default it predicts 2,000 sequences of 500 residues; ``num_seqs``, ``seq_len`` and ``variable_length`` change the test set.


Which version of metapredict did I use, and how should I cite it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``metapredict.__version__`` gives the version of the package you have installed, and :code:`meta.print_metapredict_network_version()` gives the default disorder network (V3). When you cite metapredict, please say which network you used (V1, V2 or V3); see :doc:`how_to_cite` for the papers to cite.


Memory and batch size
---------------------

metapredict runs lists and dictionaries of sequences through the network in batches. These questions cover how much memory that needs, how the batch size affects memory and speed, and what to do if you run out of memory.

How much memory does metapredict need?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you predict a list or dictionary of sequences, metapredict runs them through the network in batches, and the memory a prediction needs is dominated by one batch at a time. On top of that there is a fixed cost: on the CPU, a Python process with PyTorch and a metapredict network loaded uses about 340 MB of RAM, and on an NVIDIA GPU the process holds about 230 MB of GPU memory once the network is loaded, almost all of it CUDA's own overhead (the network weights take only a few MB).

The memory one batch needs is proportional to the number of sequences in the batch (the batch size) multiplied by the length of the longest sequence in that batch:

.. code-block:: text

    memory per batch (MB)  ≈  k  ×  batch size  ×  (longest sequence length / 1000)

where *k* depends on the network and the device:

.. list-table::
   :header-rows: 1

   * - Network
     - *k* on an NVIDIA GPU
     - *k* on the CPU
   * - Disorder V1
     - 0.36
     - 0.5
   * - Disorder V2
     - 0.65
     - 0.7
   * - Disorder V3 (default)
     - 2.9
     - 2.3
   * - pLDDT V1
     - 5.5
     - 4.1
   * - pLDDT V2 (default)
     - 1.6
     - 0.9

For example, the default disorder network (V3) on a GPU, with the default batch size of 256 and sequences up to 1,000 residues long, needs about 2.9 × 256 × 1 ≈ 740 MB per batch (we measured 766 MB).

These numbers come from the measurements described at the end of this page. Exact values will differ with your hardware and PyTorch version, but the proportional scaling holds.


What batch size does metapredict use by default?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you don't pass ``batch_size``, metapredict picks a default for the network and device you are using:

.. list-table::
   :header-rows: 1

   * - Device
     - Default batch size
   * - CPU
     - 256 (32 for pLDDT V1)
   * - NVIDIA GPU (CUDA)
     - 256
   * - Apple Silicon GPU (MPS)
     - 512

You can set the batch size yourself with the ``batch_size`` option of :code:`predict_disorder()`, :code:`predict_pLDDT()`, :code:`predict_disorder_batch()`, :code:`predict_disorder_stream()`, :code:`predict_disorder_fasta()`, :code:`predict_pLDDT_fasta()` and :code:`predict_disorder_caid()`, or with the ``-b``/``--batch-size`` option of the command-line tools that predict a whole FASTA file (``metapredict-predict-disorder``, ``metapredict-predict-idrs``, ``metapredict-predict-pLDDT`` and ``metapredict-caid``). It must be a power of two and at least 32 (32, 64, 128, 256, 512, ...). Batch size mainly affects speed and memory. Because floating-point rounding depends on which sequences share a batch, scores can differ very slightly between batch sizes (in our tests by up to about 1e-6 for disorder scores and 3e-4 for pLDDT scores on the 0-100 scale), which occasionally changes the last of the 4 decimal places metapredict reports.


How does memory change with batch size?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Memory grows in direct proportion to batch size: doubling the batch size roughly doubles the memory each batch needs. These are the measured peak memory use for predicting 2,048 sequences of 500 residues each, above the fixed cost described above. Default batch sizes are in bold.

**NVIDIA GPU** (MB of GPU memory):

.. list-table::
   :header-rows: 1

   * - Batch size
     - 32
     - 64
     - 128
     - 256
     - 512
     - 1024
     - 2048
   * - Disorder V1
     - 22
     - 28
     - 38
     - **61**
     - 105
     - 194
     - 370
   * - Disorder V2
     - 42
     - 52
     - 72
     - **111**
     - 190
     - 349
     - 662
   * - Disorder V3
     - 78
     - 124
     - 217
     - **400**
     - 768
     - 1,505
     - 2,974
   * - pLDDT V1
     - 121
     - 208
     - 382
     - **732**
     - 1,431
     - 2,827
     - 5,619
   * - pLDDT V2
     - 43
     - 69
     - 121
     - **225**
     - 434
     - 853
     - 1,686

**CPU** (MB of RAM):

.. list-table::
   :header-rows: 1

   * - Batch size
     - 32
     - 64
     - 128
     - 256
     - 512
     - 1024
     - 2048
   * - Disorder V1
     - 18
     - 37
     - 62
     - **100**
     - 189
     - 270
     - 505
   * - Disorder V2
     - 23
     - 40
     - 66
     - **117**
     - 210
     - 346
     - 721
   * - Disorder V3
     - 57
     - 120
     - 207
     - **357**
     - 643
     - 1,169
     - 2,331
   * - pLDDT V1
     - **96**
     - 166
     - 313
     - 564
     - 1,110
     - 2,105
     - 4,206
   * - pLDDT V2
     - 32
     - 54
     - 103
     - **215**
     - 327
     - 462
     - 914

Sequence length matters in the same way. With one batch of 256 sequences, the default disorder network (V3) needed 218 MB of GPU memory for sequences of 250 residues, 766 MB for 1,000 residues and 5,878 MB for 8,000 residues.


Will a bigger batch make predictions faster?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only up to about the default. For the default disorder network (V3), predicting 2,048 sequences of 500 residues took:

.. list-table::
   :header-rows: 1

   * - Batch size
     - 32
     - 256 (default)
     - 1024
     - 2048
   * - NVIDIA GPU
     - 1.55 s
     - 0.30 s
     - 0.21 s
     - 0.23 s
   * - CPU
     - 7.44 s
     - 2.16 s
     - 2.04 s
     - 1.98 s

Small batches are much slower, but beyond the default each doubling of the batch size doubles the memory for little or no gain in speed. The other networks behave the same way.


Why can a few long sequences use so much memory?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Within a batch, every sequence is padded to the length of the longest one, so a single long sequence makes its whole batch cost far more. metapredict also sorts sequences longest first before batching, so the longest sequences in your input end up together in the first batch.

For example, with the default disorder network (V3) and a batch of 256 sequences, 255 of which are 500 residues long and one of which is 8,000 residues long:

.. list-table::
   :header-rows: 1

   * - Batch of 256 sequences
     - NVIDIA GPU
     - CPU
   * - All 500 residues
     - 400 MB
     - 283 MB
   * - 255 of 500 residues plus one of 8,000
     - 2,463 MB
     - 2,661 MB
   * - All 8,000 residues
     - 5,878 MB
     - 4,502 MB

So for proteomes containing very long proteins, the first batch sets the peak. As a rough upper bound from the formula above, a batch of 256 sequences padded to the length of titin (about 34,000 residues) could need up to about 25 GB with V3 on a GPU, which is more than many GPUs have. Batches in which most sequences are much shorter than the longest one need less than this bound.


How can I reduce memory use or fix an out-of-memory error?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Use a smaller batch size.** Halving ``batch_size`` (or ``-b`` on the command line) roughly halves the memory each batch needs, at some cost in speed (see the timings above).
* **Predict very long sequences separately.** Run the few longest sequences on their own with a small batch size, and the rest with the default.
* **Use the CPU.** System RAM is usually much larger than GPU memory, so ``device='cpu'`` (or ``-d cpu`` on the command line) can handle batches that don't fit on a GPU.
* **Stream very large FASTA files.** :code:`predict_disorder_stream()` reads and predicts the file in chunks (``chunk_size`` sequences at a time), so the memory used for sequences and results stays bounded however large the file is. Combine it with ``batch_size`` to also bound the memory of each batch.

.. code-block:: python

    import metapredict as meta

    # half the default batch size: about half the memory per batch
    scores = meta.predict_disorder(sequences, batch_size=128)

    # run on the CPU, where there is usually much more memory than on a GPU
    scores = meta.predict_disorder(sequences, device='cpu')


How were these numbers measured?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The measurements used metapredict 3.1.0 with PyTorch 2.14.1 on Linux, on an NVIDIA RTX A4000 GPU (16 GB) and a 20-core CPU. Each measurement ran in a fresh Python process on random amino acid sequences and recorded the peak memory used by the prediction above what was in use after the network had loaded: on the CPU, the peak resident memory of the process; on the GPU, the peak GPU memory allocated by PyTorch. We have not measured Apple Silicon (MPS) GPUs, but the same proportional scaling with batch size and sequence length is expected.
