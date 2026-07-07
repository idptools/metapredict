'''
Testing to make sure that metapredict can use the GPU and the CPU
for predicting pLDDT and disorder for all current versions of metapredict.

It's a really simple test that tries out various permutations of disorder
prediction and pLDDT prediction on CPU and GPU. It also makes sure results
on CPU match those from GPU. 
'''

import metapredict as meta
import protfasta
import os
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
import numpy as np
import pytest
from . import local_data
try:
    import torch
    cuda_available = torch.cuda.is_available()
except ImportError:
    cuda_available = False

try:
    # torch.backends.mps only exists on recent torch builds
    mps_available = torch.backends.mps.is_available()
except (NameError, AttributeError):
    mps_available = False


# get some sequences to test out
current_filepath = os.getcwd()
onehundred_seqs = "{}/input_data/test_seqs_100.fasta".format(current_filepath)
uniprot_fasta = "{}/input_data/testing.fasta".format(current_filepath)

# read in sequences
sequences = protfasta.read_fasta(onehundred_seqs, invalid_sequence_action='convert')

# tests below

def test_disorder_v1_cpu(sequences=sequences):
    version='v1'
    device='cpu'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

def test_disorder_v2_cpu(sequences=sequences):
    version='v2'
    device='cpu'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

def test_disorder_v3_cpu(sequences=sequences):
    version='v3'
    device='cpu'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_v3_gpu(sequences=sequences):
    version='v3'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

def test_pLDDT_v1_cpu(sequences=sequences):
    version='v1'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

def test_pLDDT_v2_cpu(sequences=sequences):
    version='v2'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_pLDDT_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_pLDDT_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

def test_force_disable_batch_disorder_v1_cpu(sequences=sequences):
    version='v1'
    device='cpu'
    print(f'Running metapredict version {version} on {device}, no batch prediction\n')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

def test_force_disable_batch_disorder_v2_cpu(sequences=sequences):
    version='v2'
    device='cpu'
    print(f'Running metapredict version {version} on {device}, no batch prediction\n')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

def test_force_disable_batch_disorder_v3_cpu(sequences=sequences):
    version='v3'
    device='cpu'
    print(f'Running metapredict version {version} on {device}, no batch prediction\n')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_force_disable_batch_disorder_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n, no batch prediction')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_force_disable_batch_disorder_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n, no batch prediction')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_force_disable_batch_disorder_v3_gpu(sequences=sequences):
    version='v3'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n, no batch prediction')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

def test_force_disable_batch_pLDDT_v1_cpu(sequences=sequences):
    version='v1'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}, no batch prediction\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, force_disable_batch=True)

def test_force_disable_batch_pLDDT_v2_cpu(sequences=sequences):
    version='v2'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}, no batch prediction\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, force_disable_batch=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_force_disable_batch_pLDDT_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}, no batch prediction\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, force_disable_batch=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_force_disable_batch_pLDDT_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}, no batch prediction\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, force_disable_batch=True)


def test_disable_pack_n_pad_disorder_v1_cpu(sequences=sequences):
    version='v1'
    device='cpu'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

def test_disable_pack_n_pad_disorder_v2_cpu(sequences=sequences):
    version='v2'
    device='cpu'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

def test_disable_pack_n_pad_disorder_v3_cpu(sequences=sequences):
    version='v3'
    device='cpu'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disable_pack_n_pad_disorder_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disable_pack_n_pad_disorder_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disable_pack_n_pad_disorder_v3_gpu(sequences=sequences):
    version='v3'
    device='cuda'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

def test_disable_pack_n_pad_pLDDT_v1_cpu(sequences=sequences):
    version='v1'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}, no pack-n-pad\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, disable_pack_n_pad=True)

def test_disable_pack_n_pad_pLDDT_v2_cpu(sequences=sequences):
    version='v2'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}, no pack-n-pad\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, disable_pack_n_pad=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disable_pack_n_pad_pLDDT_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}, no pack-n-pad\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, disable_pack_n_pad=True)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disable_pack_n_pad_pLDDT_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}, no pack-n-pad\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, disable_pack_n_pad=True)

def close_enough(val1, val2, allowed_error=0.001):
    # function to see if val1 and val2 are within some allowed error amount
    # values are occassionally 0.001 off, so going to allow up to that. 
    if abs(val1-val2)<allowed_error:
        return True
    else:
        return False

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_v1_cpu_vs_gpu(sequences=sequences):
    version='v1'
    print(f'Running metapredict version {version}, comparing CPU vs GPU scores.\n')
    cpu_scores=meta.predict_disorder(sequences, version=version, device='cpu', round_values=False)
    gpu_scores=meta.predict_disorder(sequences, version=version, device='cuda', round_values=False)
    # test each score
    for seq_name in cpu_scores:
        cur_cpu_scores = cpu_scores[seq_name][1]
        cur_gpu_scores = gpu_scores[seq_name][1]
        for i in range(len(cur_cpu_scores)):
            assert close_enough(cur_cpu_scores[i], cur_gpu_scores[i])==True

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_v2_cpu_vs_gpu(sequences=sequences):
    version='v2'
    print(f'Running metapredict version {version}, comparing CPU vs GPU scores.\n')
    cpu_scores=meta.predict_disorder(sequences, version=version, device='cpu', round_values=False)
    gpu_scores=meta.predict_disorder(sequences, version=version, device='cuda', round_values=False)
    # test each score
    for seq_name in cpu_scores:
        cur_cpu_scores = cpu_scores[seq_name][1]
        cur_gpu_scores = gpu_scores[seq_name][1]
        for i in range(len(cur_cpu_scores)):
            assert close_enough(cur_cpu_scores[i], cur_gpu_scores[i])==True

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_v3_cpu_vs_gpu(sequences=sequences):
    version='v3'
    print(f'Running metapredict version {version}, comparing CPU vs GPU scores.\n')
    cpu_scores=meta.predict_disorder(sequences, version=version, device='cpu', round_values=False)
    gpu_scores=meta.predict_disorder(sequences, version=version, device='cuda', round_values=False)
    # test each score
    for seq_name in cpu_scores:
        cur_cpu_scores = cpu_scores[seq_name][1]
        cur_gpu_scores = gpu_scores[seq_name][1]
        for i in range(len(cur_cpu_scores)):
            assert close_enough(cur_cpu_scores[i], cur_gpu_scores[i])==True

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_pLDDT_v1_cpu_vs_gpu(sequences=sequences):
    version='v1'
    print(f'Running pLDDT prediction version {version}, comparing CPU vs GPU scores.\n')
    cpu_scores=meta.predict_pLDDT(sequences, pLDDT_version=version, device='cpu', round_values=False)
    gpu_scores=meta.predict_pLDDT(sequences, pLDDT_version=version, device='cuda', round_values=False)
    # test each score
    for seq_name in cpu_scores:
        cur_cpu_scores = cpu_scores[seq_name][1]
        cur_gpu_scores = gpu_scores[seq_name][1]
        for i in range(len(cur_cpu_scores)):
            # plddt V1 scores are 100x bigger than plldt V2 (which are trained on plddt / 100)
            # so we want to use 0.1 here instead of 0.001
            assert close_enough(cur_cpu_scores[i], cur_gpu_scores[i], allowed_error=0.1)==True

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_pLDDT_v2_cpu_vs_gpu(sequences=sequences):
    version='v2'
    print(f'Running pLDDT prediction version {version}, comparing CPU vs GPU scores.\n')
    cpu_scores=meta.predict_pLDDT(sequences, pLDDT_version=version, device='cpu', round_values=False)
    gpu_scores=meta.predict_pLDDT(sequences, pLDDT_version=version, device='cuda', round_values=False)
    # test each score
    for seq_name in cpu_scores:
        cur_cpu_scores = cpu_scores[seq_name][1]
        cur_gpu_scores = gpu_scores[seq_name][1]
        for i in range(len(cur_cpu_scores)):
            assert close_enough(cur_cpu_scores[i], cur_gpu_scores[i])==True

def test_single_sequence_disorder_v1_cpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v1'
    device='cpu'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

def test_single_sequence_disorder_v2_cpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v2'
    device='cpu'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

def test_single_sequence_disorder_v3_cpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v3'
    device='cpu'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_single_sequence_disorder_v1_gpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v1'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_single_sequence_disorder_v2_gpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v2'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_single_sequence_disorder_v3_gpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v3'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

def test_single_sequence_pLDDT_v1_cpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v1'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

def test_single_sequence_pLDDT_v2_cpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v2'
    device='cpu'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_single_sequence_pLDDT_v1_gpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v1'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_single_sequence_pLDDT_v2_gpu(sequences='GSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGSGS'):
    version='v2'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

# ----------------------------------------------------------------------------
# Reference-value tests on GPU (CUDA and MPS).
#
# The CPU-side test in test_metapredict.py pins device='cpu' and asserts an
# exact np.allclose (rtol=1e-5) match against the reference scores stored in
# local_data.py. Those references were generated on CPU; cuDNN LSTM and MPS
# LSTM diverge from CPU by ~1e-4, which trips the strict comparison. Here we
# run the same predictions on the GPU backend(s) and assert they match the
# CPU references at atol=1e-3 — the same domain-appropriate tolerance used
# by score_compare() elsewhere in the suite. This catches model regressions
# or precision issues on the GPU code path without depending on hardware-
# specific reference captures.
# ----------------------------------------------------------------------------

_GPU_REF_TOL = 1e-3

_disorder_refs = {
    1: local_data.disorder_Q8N6T3_legacy,
    2: local_data.disorder_Q8N6T3_2,
    3: local_data.disorder_Q8N6T3_3,
}


def _assert_matches_reference(version, device):
    scores = meta.predict_disorder_fasta(uniprot_fasta, version=version, device=device)['Q8N6T3'][1]
    ref = np.array(_disorder_refs[version], dtype=np.float32)
    assert np.allclose(scores, ref, atol=_GPU_REF_TOL), \
        f"v{version} on {device}: max abs diff {np.max(np.abs(scores - ref)):.4g} exceeds {_GPU_REF_TOL}"


@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_reference_v1_cuda():
    _assert_matches_reference(1, 'cuda')


@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_reference_v2_cuda():
    _assert_matches_reference(2, 'cuda')


@pytest.mark.skipif(not cuda_available, reason="CUDA is not available.")
def test_disorder_reference_v3_cuda():
    _assert_matches_reference(3, 'cuda')


@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_disorder_reference_v1_mps():
    _assert_matches_reference(1, 'mps')


@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_disorder_reference_v2_mps():
    _assert_matches_reference(2, 'mps')


@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_disorder_reference_v3_mps():
    _assert_matches_reference(3, 'mps')


# ----------------------------------------------------------------------------
# CPU-vs-MPS parity tests.
#
# The existing CPU-vs-CUDA parity tests (`test_disorder_v{1,2,3}_cpu_vs_gpu`,
# `test_pLDDT_v{1,2}_cpu_vs_gpu`) verify CUDA outputs stay within ~1e-3 of
# CPU. These are the MPS mirror — same tolerance, using the same
# `close_enough` helper so any drift beyond the accepted precision loss is
# caught on the Mac too. cuDNN and MPS LSTM both diverge from CPU by ~1e-4,
# so atol=1e-3 comfortably absorbs the expected numerical delta.
# ----------------------------------------------------------------------------

@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_disorder_v1_cpu_vs_mps(sequences=sequences):
    version = 'v1'
    print(f'Running metapredict version {version}, comparing CPU vs MPS scores.\n')
    cpu_scores = meta.predict_disorder(sequences, version=version, device='cpu', round_values=False)
    mps_scores = meta.predict_disorder(sequences, version=version, device='mps', round_values=False)
    for seq_name in cpu_scores:
        cur_cpu = cpu_scores[seq_name][1]
        cur_mps = mps_scores[seq_name][1]
        for i in range(len(cur_cpu)):
            assert close_enough(cur_cpu[i], cur_mps[i]) == True


@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_disorder_v2_cpu_vs_mps(sequences=sequences):
    version = 'v2'
    print(f'Running metapredict version {version}, comparing CPU vs MPS scores.\n')
    cpu_scores = meta.predict_disorder(sequences, version=version, device='cpu', round_values=False)
    mps_scores = meta.predict_disorder(sequences, version=version, device='mps', round_values=False)
    for seq_name in cpu_scores:
        cur_cpu = cpu_scores[seq_name][1]
        cur_mps = mps_scores[seq_name][1]
        for i in range(len(cur_cpu)):
            assert close_enough(cur_cpu[i], cur_mps[i]) == True


@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_disorder_v3_cpu_vs_mps(sequences=sequences):
    version = 'v3'
    print(f'Running metapredict version {version}, comparing CPU vs MPS scores.\n')
    cpu_scores = meta.predict_disorder(sequences, version=version, device='cpu', round_values=False)
    mps_scores = meta.predict_disorder(sequences, version=version, device='mps', round_values=False)
    for seq_name in cpu_scores:
        cur_cpu = cpu_scores[seq_name][1]
        cur_mps = mps_scores[seq_name][1]
        for i in range(len(cur_cpu)):
            assert close_enough(cur_cpu[i], cur_mps[i]) == True


@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_pLDDT_v1_cpu_vs_mps(sequences=sequences):
    version = 'v1'
    print(f'Running pLDDT prediction version {version}, comparing CPU vs MPS scores.\n')
    cpu_scores = meta.predict_pLDDT(sequences, pLDDT_version=version, device='cpu', round_values=False)
    mps_scores = meta.predict_pLDDT(sequences, pLDDT_version=version, device='mps', round_values=False)
    for seq_name in cpu_scores:
        cur_cpu = cpu_scores[seq_name][1]
        cur_mps = mps_scores[seq_name][1]
        for i in range(len(cur_cpu)):
            # pLDDT v1 scores are ~100x larger than v2, so use a matching
            # tolerance (0.1 vs 0.001) — mirrors the CUDA-side test above.
            assert close_enough(cur_cpu[i], cur_mps[i], allowed_error=0.1) == True


@pytest.mark.skipif(not mps_available, reason="MPS is not available.")
def test_pLDDT_v2_cpu_vs_mps(sequences=sequences):
    version = 'v2'
    print(f'Running pLDDT prediction version {version}, comparing CPU vs MPS scores.\n')
    cpu_scores = meta.predict_pLDDT(sequences, pLDDT_version=version, device='cpu', round_values=False)
    mps_scores = meta.predict_pLDDT(sequences, pLDDT_version=version, device='mps', round_values=False)
    for seq_name in cpu_scores:
        cur_cpu = cpu_scores[seq_name][1]
        cur_mps = mps_scores[seq_name][1]
        for i in range(len(cur_cpu)):
            assert close_enough(cur_cpu[i], cur_mps[i]) == True


test_single_sequence_disorder_v3_gpu()