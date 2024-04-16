'''
function to make sure that metapredict can use the GPU and the CPU
for predicting pLDDT and disorder for all current versions of metapredict.
'''

import metapredict as meta
import protfasta
import os
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks


# get some sequences to test out
current_filepath = os.getcwd()
onehundred_seqs = "{}/input_data/test_seqs_100.fasta".format(current_filepath)

# read in sequences 
sequences = protfasta.read_fasta(onehundred_seqs, invalid_sequence_action='convert')

# test all versions of metapredict
for version in metapredict_networks:
    print(f'Running metapredict version {version} on CPU\n')
    meta.predict_disorder(sequences, version=version, device='cpu')
    print(f'Running metapredict version {version} on GPU')
    meta.predict_disorder(sequences, version=version, device='cuda')

for version in pplddt_networks:
    print(f'Running pLDDT prediction version {version} on CPU\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device='cpu')
    print(f'Running pLDDT prediction version {version} on GPU\n')
    meta.predict_pLDDT(sequences, pLDDT_version=version, device='cuda')

print('finished!')