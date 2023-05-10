
# Import package, test suite, and other packages as needed
from . import local_data
import numpy as np
import os

from metapredict.metapredict_exceptions import MetapredictError
from metapredict.backend import batch_predict
import protfasta


import metapredict as meta


current_filepath = os.getcwd()
fasta_filepath = "{}/input_data/testing.fasta".format(current_filepath)

from . import build_seq


def test_size_filter():
    in_seqs = ['A','AA','AAA','A','AAAAAA']
    out = batch_predict.size_filter(in_seqs)
    assert len(out[1]) == 2
    assert len(out[2]) == 1
    assert len(out[3]) == 1
    assert len(out[6]) == 1

## test the new metapredict predictor
def test_metapredict_predictor():

    seq = 'RDCAPNNGKKMDNQQHGDVSNQSDNRDSVQQQPPQMAGSQERQKSTESQQSPRSKENKQQAGHSHPESMPRSMSEKEPEMQHDESTGMQNHNRGMQSQDP'
    assert meta.predict_disorder(seq) == local_data.S2

    test = {'test':seq}
    
    out = batch_predict.batch_predict(test)

    # using a tolerance of 1e-5 because batch works on single and on double
    # precision, but if no pair of residues is different than 1e-4 these are
    # functionally identical
    assert np.max(np.array(out['test'][1]) - np.array(local_data.S2)) < 1e-3

    assert np.max(np.array(out['test'][1]) - np.array(meta.predict_disorder(seq))) < 1e-3


def test_batch_prediction():

    seqs = {}
    for idx, _ in enumerate(range(1)):
        s = build_seq()
        seqs[idx] = s
        
    preds = batch_predict.batch_predict(seqs)
    for s in seqs:
        single = meta.predict_disorder(seqs[s])
        
        assert np.max(np.array(preds[s][1]) - np.array(single)) < 1e-3
        

def test_batch_idrs():

    seqs = {}
    for idx, _ in enumerate(range(10)):
        s = build_seq()
        seqs[idx] = s
        
    preds = batch_predict.batch_predict(seqs, return_domains=True)
    for s in seqs:
        single = meta.predict_disorder_domains(seqs[s])

        p = preds[s]
