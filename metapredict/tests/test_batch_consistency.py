# Cross-path batch-consistency tests.
#
# metapredict has three different code paths for turning sequences into
# predictions:
#   * pack-n-pad   (force_disable_batch=False, disable_pack_n_pad=False)
#   * size-collect (force_disable_batch=False, disable_pack_n_pad=True)
#   * per-sequence (force_disable_batch=True)
# and the batched paths additionally depend on batch_size.
#
# None of these should change the predicted scores. This module predicts a set of
# real sequences from ground_truth_500_seqs.fasta with every combination of
# batch_size (32..512), force_disable_batch, and disable_pack_n_pad, and asserts
# they all agree with a single reference. If any combination disagrees beyond
# floating-point noise, that is a real bug and should be investigated.

import os

import numpy as np
import protfasta
import pytest

import metapredict as meta

HERE = os.path.dirname(os.path.abspath(__file__))
FASTA = os.path.join(HERE, "input_data", "ground_truth_500_seqs.fasta")

# a subset of the 500 real sequences: enough (and varied enough in length) to
# exercise multiple batches and multiple size-collect groups, while staying fast
_all_seqs = protfasta.read_fasta(FASTA, invalid_sequence_action="convert")
KEYS = list(_all_seqs.keys())[:40]
SUBSET = {k: _all_seqs[k] for k in KEYS}

VERSIONS = ["1", "2", "3"]
BATCH_SIZES = [32, 64, 128, 256, 512]

# "same" allowing only floating-point noise; a genuine path divergence would be
# orders of magnitude larger than this.
TOL = 1e-4


def _predict(version, **kwargs):
    return meta.predict_disorder(SUBSET, version=version, device="cpu",
                                 round_values=False, return_numpy=True,
                                 show_progress_bar=False, **kwargs)


# canonical reference: the standard pack-n-pad batch prediction at batch_size 512
_REFERENCE = {
    v: {k: np.asarray(out[1]) for k, out in
        _predict(v, force_disable_batch=False, disable_pack_n_pad=False, batch_size=512).items()}
    for v in VERSIONS
}


def _assert_matches_reference(version, out, label):
    ref = _REFERENCE[version]
    for k in KEYS:
        assert np.allclose(out[k][1], ref[k], atol=TOL), (
            f"v{version} [{label}]: prediction for {k!r} diverges from the reference "
            f"(max abs diff {np.max(np.abs(np.asarray(out[k][1]) - ref[k])):.3g}). "
            f"Batching must not change predictions -- investigate!"
        )


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("batch_size", BATCH_SIZES)
@pytest.mark.parametrize("force_disable_batch", [False, True])
@pytest.mark.parametrize("disable_pack_n_pad", [False, True])
def test_all_batch_configs_match_reference(version, batch_size, force_disable_batch, disable_pack_n_pad):
    """Every combination of batch_size (32..512), force_disable_batch and
    disable_pack_n_pad must produce the same predictions as the reference. These
    exercise the pack-n-pad, size-collect and per-sequence paths; any divergence
    beyond floating-point noise is a real bug."""
    out = _predict(version, force_disable_batch=force_disable_batch,
                   disable_pack_n_pad=disable_pack_n_pad, batch_size=batch_size)
    _assert_matches_reference(
        version, out,
        f"bs={batch_size} force_disable_batch={force_disable_batch} "
        f"disable_pack_n_pad={disable_pack_n_pad}")
