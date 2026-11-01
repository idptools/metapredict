# Tests for single-threaded CPU prediction.
#
# predict() and predict_pLDDT() drop PyTorch to CPU_PREDICTION_THREADS while they
# predict on the CPU, because metapredict's small LSTMs get slower with every
# extra thread. torch.set_num_threads is process-wide, so the caller's value must
# be put back afterwards, including when prediction raises.

import numpy as np
import pytest
import torch

import metapredict as meta
from metapredict.backend import predictor
from metapredict.parameters import CPU_PREDICTION_THREADS

from . import build_seq

np.random.seed(2002)
_THREAD_SEQS = [build_seq() for _ in range(20)]

# a caller thread count that differs from CPU_PREDICTION_THREADS, so a missing
# restore is detectable
_CALLER_THREADS = CPU_PREDICTION_THREADS + 2


@pytest.fixture
def caller_threads():
    """Set a distinctive caller thread count and put the original back afterwards."""
    original = torch.get_num_threads()
    torch.set_num_threads(_CALLER_THREADS)
    yield _CALLER_THREADS
    torch.set_num_threads(original)


@pytest.fixture
def threads_seen_by_model(monkeypatch):
    """Record torch's thread count each time a network is loaded for prediction."""
    seen = []
    original_get_model = predictor.get_model

    def recording_get_model(*args, **kwargs):
        seen.append(torch.get_num_threads())
        return original_get_model(*args, **kwargs)

    monkeypatch.setattr(predictor, 'get_model', recording_get_model)
    return seen


@pytest.mark.parametrize('inputs', [_THREAD_SEQS[0], _THREAD_SEQS])
def test_disorder_predicts_single_threaded_on_cpu(caller_threads, threads_seen_by_model, inputs):
    meta.predict_disorder(inputs, device='cpu')
    assert threads_seen_by_model == [CPU_PREDICTION_THREADS]
    assert torch.get_num_threads() == caller_threads


@pytest.mark.parametrize('inputs', [_THREAD_SEQS[0], _THREAD_SEQS])
def test_pLDDT_predicts_single_threaded_on_cpu(caller_threads, threads_seen_by_model, inputs):
    meta.predict_pLDDT(inputs, device='cpu')
    assert threads_seen_by_model == [CPU_PREDICTION_THREADS]
    assert torch.get_num_threads() == caller_threads


def test_caller_threads_restored_when_prediction_raises(caller_threads, monkeypatch):
    def broken_get_model(*args, **kwargs):
        raise RuntimeError('simulated failure while loading the network')

    monkeypatch.setattr(predictor, 'get_model', broken_get_model)
    with pytest.raises(RuntimeError):
        meta.predict_disorder(_THREAD_SEQS, device='cpu')
    assert torch.get_num_threads() == caller_threads
