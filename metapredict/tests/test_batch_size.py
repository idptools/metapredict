# Tests for the user-facing ``batch_size`` option on the prediction functions.
#
# The batch size only controls how sequences are grouped for the forward pass; it
# must never change the predicted scores. These tests confirm that (a) predictions
# are invariant to batch size, (b) batched predictions match single-sequence
# predictions, and (c) invalid batch sizes are rejected.

import numpy as np
import pytest

import metapredict as meta
from metapredict.metapredict_exceptions import MetapredictError
from metapredict.backend.predictor import resolve_batch_size

from . import build_seq

# deterministic set of variable-length sequences, large enough that a batch size
# of 32 produces several batches (so batching is genuinely exercised)
np.random.seed(1138)
SEQS = [build_seq() for _ in range(60)]

DISORDER_VERSIONS = [1, 2, 3]
PLDDT_VERSIONS = [1, 2]
BATCH_SIZES = [32, 64, 128, 256, 512, 1024]

# batch grouping introduces only floating-point noise (~1e-6 at full precision)
BATCH_TOL = 1e-4
SINGLE_TOL = 1e-3


@pytest.mark.parametrize("network_version", DISORDER_VERSIONS)
def test_batch_size_does_not_change_disorder(network_version):
    """Disorder scores must be identical (to float noise) across batch sizes."""
    baseline = meta.predict_disorder(SEQS, version=network_version, device='cpu',
                                     round_values=False, batch_size=BATCH_SIZES[0])
    for bs in BATCH_SIZES[1:]:
        out = meta.predict_disorder(SEQS, version=network_version, device='cpu',
                                    round_values=False, batch_size=bs)
        for i in range(len(SEQS)):
            assert np.allclose(out[i][1], baseline[i][1], atol=BATCH_TOL), \
                f"v{network_version} batch_size={bs}: scores differ from batch_size={BATCH_SIZES[0]}"


@pytest.mark.parametrize("network_version", PLDDT_VERSIONS)
def test_batch_size_does_not_change_plddt(network_version):
    """pLDDT scores must be identical (to float noise) across batch sizes."""
    baseline = meta.predict_pLDDT(SEQS, pLDDT_version=network_version, device='cpu',
                                  round_values=False, batch_size=BATCH_SIZES[0])
    for bs in BATCH_SIZES[1:]:
        out = meta.predict_pLDDT(SEQS, pLDDT_version=network_version, device='cpu',
                                 round_values=False, batch_size=bs)
        for i in range(len(SEQS)):
            assert np.allclose(out[i][1], baseline[i][1], atol=BATCH_TOL), \
                f"pLDDT v{network_version} batch_size={bs}: scores differ from batch_size={BATCH_SIZES[0]}"


@pytest.mark.parametrize("network_version", DISORDER_VERSIONS)
def test_batched_matches_single_sequence(network_version):
    """A batched prediction must match the single-sequence prediction per sequence."""
    batched = meta.predict_disorder(SEQS, version=network_version, device='cpu',
                                    round_values=False, batch_size=64)
    # single-sequence predictions bypass batching entirely (the ground truth)
    for i, seq in enumerate(SEQS):
        single = meta.predict_disorder(seq, version=network_version, device='cpu',
                                       round_values=False)
        assert np.allclose(batched[i][1], single, atol=SINGLE_TOL), \
            f"v{network_version}: batched result differs from single-sequence prediction"


def test_batch_size_default_is_none_and_reproduces():
    """batch_size=None (default) must match an explicit valid batch size."""
    default = meta.predict_disorder(SEQS, device='cpu', round_values=False)
    explicit = meta.predict_disorder(SEQS, device='cpu', round_values=False, batch_size=512)
    for i in range(len(SEQS)):
        assert np.allclose(default[i][1], explicit[i][1], atol=BATCH_TOL)


@pytest.mark.parametrize("good", [32, 64, 128, 256, 512, 1024, 2048, None])
def test_valid_batch_sizes_accepted(good):
    """Powers of two >= 32 (and None) are accepted."""
    out = meta.predict_disorder(SEQS[:5], device='cpu', batch_size=good)
    assert len(out) == 5


@pytest.mark.parametrize("bad", [31, 33, 48, 100, 16, 8, 1, 0, -32, -1, 1.5, 64.0, True, "64", [64]])
def test_invalid_batch_sizes_rejected(bad):
    """Anything that is not a power of two >= 32 (or None) raises MetapredictError."""
    with pytest.raises(MetapredictError):
        meta.predict_disorder(SEQS[:5], device='cpu', batch_size=bad)


def test_predict_disorder_batch_honors_batch_size():
    """predict_disorder_batch also accepts batch_size, invariant to its value."""
    a = meta.predict_disorder_batch(SEQS, device='cpu', round_values=False, batch_size=32,
                                    show_progress_bar=False)
    b = meta.predict_disorder_batch(SEQS, device='cpu', round_values=False, batch_size=256,
                                    show_progress_bar=False)
    for i in range(len(SEQS)):
        assert np.allclose(a[i][1], b[i][1], atol=BATCH_TOL)


def test_invalid_batch_size_rejected_on_batch_and_plddt():
    """The validation applies on predict_disorder_batch and predict_pLDDT too."""
    with pytest.raises(MetapredictError):
        meta.predict_disorder_batch(SEQS[:5], device='cpu', batch_size=48, show_progress_bar=False)
    with pytest.raises(MetapredictError):
        meta.predict_pLDDT(SEQS[:5], device='cpu', batch_size=100)


# --- network- and device-dependent default batch size (used when batch_size is None) ---

# a network that defines its own per-device batch sizes (like V3)
_NET_WITH_DEV = {'batch_size': 999, 'device_batch_size': {'cuda': 256, 'mps': 512}}
# a network with no per-device batch sizes (like pLDDT) -> global fallback
_NET_NO_DEV = {'batch_size': 999}


@pytest.mark.parametrize("device,expected", [
    ("mps", 512),      # uses the network's own mps default
    ("cuda", 256),     # uses the network's own cuda default
    ("cuda:0", 256),   # a specific CUDA GPU still maps to the cuda default
    ("cuda:3", 256),
    ("cpu", 999),      # unlisted device -> the network's base 'batch_size'
])
def test_network_device_default_batch_size(device, expected):
    assert resolve_batch_size(None, device, _NET_WITH_DEV) == expected


@pytest.mark.parametrize("device,expected", [
    ("mps", 512),      # no per-network map -> global DEFAULT_BATCH_SIZE_BY_DEVICE
    ("cuda", 256),
    ("cpu", 999),      # unlisted -> network base 'batch_size'
])
def test_global_device_default_when_network_has_none(device, expected):
    assert resolve_batch_size(None, device, _NET_NO_DEV) == expected


@pytest.mark.parametrize("device", ["mps", "cuda", "cuda:1", "cpu"])
def test_explicit_batch_size_overrides_defaults(device):
    assert resolve_batch_size(128, device, _NET_WITH_DEV) == 128


def test_network_device_batch_size_config():
    """Lock the per-network per-device default batch sizes (mps 512, cuda/cpu 256)."""
    from metapredict.backend.network_parameters import metapredict_networks as N
    expected = {'cuda': 256, 'mps': 512, 'cpu': 256}
    assert N['V1']['parameters']['device_batch_size'] == expected
    assert N['V2']['parameters']['device_batch_size'] == expected
    assert N['V3']['parameters']['device_batch_size'] == expected
