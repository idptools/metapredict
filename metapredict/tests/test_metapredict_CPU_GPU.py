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


# get some sequences to test out
current_filepath = os.getcwd()
onehundred_seqs = "{}/input_data/test_seqs_100.fasta".format(current_filepath)

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

def test_disorder_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

def test_disorder_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n')
    meta.predict_disorder(sequences, version=version, device=device)

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

def test_pLDDT_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device)

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

def test_force_disable_batch_disorder_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n, no batch prediction')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

def test_force_disable_batch_disorder_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running metapredict version {version} on {device}\n, no batch prediction')
    meta.predict_disorder(sequences, version=version, device=device, force_disable_batch=True)

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

def test_force_disable_batch_pLDDT_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}, no batch prediction\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, force_disable_batch=True)

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

def test_disable_pack_n_pad_disorder_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

def test_disable_pack_n_pad_disorder_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running metapredict version {version} on {device}, no pack-n-pad\n')
    meta.predict_disorder(sequences, version=version, device=device, disable_pack_n_pad=True)

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

def test_disable_pack_n_pad_pLDDT_v1_gpu(sequences=sequences):
    version='v1'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}, no pack-n-pad\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, disable_pack_n_pad=True)

def test_disable_pack_n_pad_pLDDT_v2_gpu(sequences=sequences):
    version='v2'
    device='cuda'
    print(f'Running pLDDT prediction version {version} on {device}, no pack-n-pad\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device=device, disable_pack_n_pad=True)


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
            assert np.round(cur_cpu_scores[i], 3)==np.round(cur_gpu_scores[i], 3)

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
            assert np.round(cur_cpu_scores[i], 3)==np.round(cur_gpu_scores[i], 3)

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
            assert np.round(cur_cpu_scores[i], 3)==np.round(cur_gpu_scores[i], 3)

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
            assert np.round(cur_cpu_scores[i], 3)==np.round(cur_gpu_scores[i], 3)

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
            assert np.round(cur_cpu_scores[i], 3)==np.round(cur_gpu_scores[i], 3)

