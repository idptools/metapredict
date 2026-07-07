# disorter thresholds depending on how disorder is predicted.
METAPREDICT_DISORDER_THRESHOLD=0.42
METAPREDICT_HYBRID_DISORDER_THRESHOLD_COOPERATIVE = 0.65
METAPREDICT_HYBRID_DISORDER_THRESHOLD_NONCOOPERATIVE = 0.50
METAPREDICT_LEGACY_THRESHOLD = 0.42
METAPREDICT_V2_THRESHOLD=0.5
METAPREDICT_V3_THRESHOLD=0.5

# set the current default network for metapredict.
DEFAULT_NETWORK = 'V3'
DEFAULT_NETWORK_PLDDT = 'V2'

# various constraints on predictions we've run across
MAX_CUDA_LENGTH=65535

# Default batch size to use per device when the caller does not pass an explicit
# batch_size. Larger batches better amortise per-batch overhead on MPS, while
# CUDA does well with a more moderate batch. Any device not listed here (e.g.
# cpu) falls back to the network's configured batch_size.
DEFAULT_BATCH_SIZE_BY_DEVICE = {'cuda': 256, 'mps': 512}
