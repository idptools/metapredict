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

# Number of PyTorch intra-op threads used while predicting on the CPU. The
# metapredict networks are small LSTMs that step along the sequence one residue
# position at a time, so every step works on tiny tensors. PyTorch splits some
# of those operations across all cores (tanh on anything over 2,048 elements),
# and coordinating the threads costs several times the work itself, so every
# extra thread makes prediction slower. Single-threaded, the human proteome on
# an Apple M3 Max CPU takes 10 s instead of 23 s (V2) and 36 s instead of 56 s
# (V3), and pLDDT prediction is 1.4-2.3x faster. The caller's own thread count
# is restored after each prediction.
CPU_PREDICTION_THREADS = 1
