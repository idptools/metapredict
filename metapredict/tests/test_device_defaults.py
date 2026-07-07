# Tests for the per-network default device selection.
#
# The small disorder networks (V1, V2) are faster on CPU than on Apple-silicon
# MPS, so their default device order prefers cpu over mps; the larger V3 network
# benefits from a GPU and prefers mps. check_device() resolves an ordered list of
# devices to the first available one.

import numpy as np
import pytest

import metapredict as meta
from metapredict.backend.predictor import check_device
from metapredict.backend.network_parameters import metapredict_networks
from metapredict.metapredict_exceptions import MetapredictError

from . import build_seq

# deterministic sequences for the end-to-end default-device tests
np.random.seed(2001)
_DEV_SEQS = [build_seq() for _ in range(20)]
_DEV_TOL = 1e-3  # cross-device precision loss (cpu vs mps/cuda) is ~1e-4


def test_network_device_order():
    """V1/V2 prefer cpu over mps; V3 prefers mps over cpu."""
    assert metapredict_networks['V1']['parameters']['device_order'] == ['cuda', 'cpu', 'mps']
    assert metapredict_networks['V2']['parameters']['device_order'] == ['cuda', 'cpu', 'mps']
    assert metapredict_networks['V3']['parameters']['device_order'] == ['cuda', 'mps', 'cpu']


def test_check_device_ordered_list_returns_first_available():
    # cpu is always available, so any order with cpu before accelerators -> cpu
    assert check_device(None, default_device=['cpu']) == 'cpu'
    assert check_device(None, default_device=['cpu', 'cuda', 'mps']) == 'cpu'
    # V1/V2-style order on a machine without cuda must resolve to cpu (not mps)
    assert check_device(None, default_device=['cuda', 'cpu', 'mps']) in ('cuda', 'cpu')


def test_check_device_string_modes_still_work():
    assert check_device(None, default_device='cpu') == 'cpu'
    assert check_device('cpu') == 'cpu'
    assert check_device(None, default_device='gpu') in ('cuda', 'mps', 'cpu')


def test_check_device_invalid_preference_raises():
    with pytest.raises(MetapredictError):
        check_device(None, default_device='not-a-device')
    with pytest.raises(MetapredictError):
        check_device(None, default_device=['not-a-device'])


# --- end-to-end: predicting with NO device= uses the per-network default, and
#     whatever device that selects must produce results matching CPU ---

@pytest.mark.parametrize("network_version", [1, 2, 3])
def test_default_device_disorder_matches_cpu(network_version):
    default = meta.predict_disorder(_DEV_SEQS, version=network_version, round_values=False)
    cpu = meta.predict_disorder(_DEV_SEQS, version=network_version, device='cpu', round_values=False)
    for i in range(len(_DEV_SEQS)):
        assert np.allclose(default[i][1], cpu[i][1], atol=_DEV_TOL), \
            f"v{network_version}: default-device prediction differs from cpu"


@pytest.mark.parametrize("network_version", [1, 2])
def test_default_device_plddt_matches_cpu(network_version):
    default = meta.predict_pLDDT(_DEV_SEQS, pLDDT_version=network_version, round_values=False)
    cpu = meta.predict_pLDDT(_DEV_SEQS, pLDDT_version=network_version, device='cpu', round_values=False)
    for i in range(len(_DEV_SEQS)):
        assert np.allclose(default[i][1], cpu[i][1], atol=_DEV_TOL), \
            f"pLDDT v{network_version}: default-device prediction differs from cpu"
