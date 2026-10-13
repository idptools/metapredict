Python Module Documentation
=============================

Recommended usage
-------------------
In general, we recommend using metapredict in Python by first importing metapredict as meta:

.. code-block:: python

	import metapredict as meta

	
The ``meta`` module can then be used to call all the user-facing functions. Documentation for these functions is included below.


metapredict functions
------------------------

.. automodule:: metapredict
   :members:


.. automodule:: metapredict.meta
   :members:


Lower-level prediction function
--------------------------------

We recommend using ``predict_disorder()`` to predict disorder. ``predict()`` is the lower-level function that ``predict_disorder()`` calls, and it exposes two additional options, ``use_slow`` and ``default_to_device``. Note that it selects the device with ``use_device`` rather than ``device``.

.. autofunction:: metapredict.predict


DisorderObject
------------------------

.. autoclass:: metapredict.backend.data_structures.DisorderObject

   You don't need to create a ``DisorderObject`` yourself. Domain boundaries are ``[start, end]`` pairs that follow Python indexing, so ``sequence[start:end]`` is the domain's sequence.

   .. py:attribute:: sequence
      :type: str

      The amino acid sequence.

   .. py:attribute:: disorder
      :type: numpy.ndarray or list

      The per-residue disorder scores, as a NumPy array or a list depending on the ``return_numpy`` option.

   .. py:attribute:: meta
      :type: numpy.ndarray or list

      The same object as ``disorder``, kept for backwards compatibility.

   .. py:attribute:: disordered_domain_boundaries
      :type: list

      A list of ``[start, end]`` boundaries, one for each IDR.

   .. py:attribute:: folded_domain_boundaries
      :type: list

      A list of ``[start, end]`` boundaries, one for each folded domain.

   .. py:attribute:: disordered_domains
      :type: list

      A list of the amino acid sequences of the IDRs.

   .. py:attribute:: folded_domains
      :type: list

      A list of the amino acid sequences of the folded domains.


Errors
------------------------

.. autoexception:: metapredict.MetapredictError

   The exception metapredict raises when it is given invalid input, for example an unknown network version or device, an invalid ``batch_size``, or an empty sequence. You can import it directly from ``metapredict``:

   .. code-block:: python

      import metapredict as meta
      from metapredict import MetapredictError

      try:
          meta.predict_disorder(['MKASNDYTQQATQSYGAYPTQPGQGYSQQSSQPYG', 'DSSPEAPAEPPKDVPHDWLYSYVFLTHHPADFLR'], batch_size=48)
      except MetapredictError as error:
          print(error)

