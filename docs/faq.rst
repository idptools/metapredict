Frequently asked questions
==========================

How much memory does metapredict need?
---------------------------------------

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
-------------------------------------------------

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

You can set the batch size yourself with the ``batch_size`` option of :code:`predict_disorder()`, :code:`predict_pLDDT()`, :code:`predict_disorder_batch()` and :code:`predict_disorder_stream()`. It must be a power of two and at least 32 (32, 64, 128, 256, 512, ...). Batch size mainly affects speed and memory. Because floating-point rounding depends on which sequences share a batch, scores can differ very slightly between batch sizes (in our tests by up to about 1e-6 for disorder scores and 3e-4 for pLDDT scores on the 0-100 scale), which occasionally changes the last of the 4 decimal places metapredict reports. The command-line tools always use the defaults.


How does memory change with batch size?
----------------------------------------

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
---------------------------------------------

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
-------------------------------------------------

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
-----------------------------------------------------------

* **Use a smaller batch size.** Halving ``batch_size`` roughly halves the memory each batch needs, at some cost in speed (see the timings above).
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
---------------------------------

The measurements used metapredict 3.1.0 with PyTorch 2.14.1 on Linux, on an NVIDIA RTX A4000 GPU (16 GB) and a 20-core CPU. Each measurement ran in a fresh Python process on random amino acid sequences and recorded the peak memory used by the prediction above what was in use after the network had loaded: on the CPU, the peak resident memory of the process; on the GPU, the peak GPU memory allocated by PyTorch. We have not measured Apple Silicon (MPS) GPUs, but the same proportional scaling with batch size and sequence length is expected.
