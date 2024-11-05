# Import package, test suite, and other packages as needed

from . import local_data
import numpy as np
import os

from metapredict.metapredict_exceptions import MetapredictError
from metapredict.backend import predictor
import protfasta

from packaging import version
import torch

import metapredict as meta


current_filepath = os.getcwd()
fasta_filepath = "{}/input_data/testing.fasta".format(current_filepath)

onehundred_seqs = "{}/input_data/test_seqs_100.fasta".format(current_filepath)
# updated to test_scores_100_v3.npy because V3 is now default network. 
onehundred_scores = "{}/input_data/test_scores_100_v3.npy".format(current_filepath)


from . import build_seq

def score_compare(s1, s2):
    """
    Function which compares two lists/arrays with an error-tollerance
    of 1e-3. Used for comparing disorder profiles

    Parameters
    ------------
    s1 : list/np.array
        Numerical vector/array/list 1

    s2 : list/np.array
        Numerical vector/array/list 2

    Returns
    ----------
    Bool
        Returns true if all elements are less than 3e-3, else 
        returns False
    
    """
    
    return np.allclose(np.array(s1), np.array(s2), atol=0.003)
    
    


def test_size_filter():
    """
    Function that tests the size_filter function in batch_predict
    """
    in_seqs = ['A','AA','AAA','A','AAAAAA']
    out = predictor.size_filter(in_seqs)
    assert len(out[1]) == 2
    assert len(out[2]) == 1
    assert len(out[3]) == 1
    assert len(out[6]) == 1

## test the new metapredict predictor
def test_metapredict_predictor():
    """
    Simple one -off test make sure we predict disorder scores that 

    """

    seq = 'RDCAPNNGKKMDNQQHGDVSNQSDNRDSVQQQPPQMAGSQERQKSTESQQSPRSKENKQQAGHSHPESMPRSMSEKEPEMQHDESTGMQNHNRGMQSQDP'
    assert score_compare(meta.predict_disorder(seq), local_data.S2)==True

    test = {'test':seq}
    
    out = meta.predict_disorder_batch(test)

    # using a tolerance of 1e-3 because batch works on single and on double
    # precision, but if no pair of residues is different than 1e-4 these are
    # functionally identical
    #assert np.allclose(out['test'][1], np.array(local_data.S2), atol=1e-3)
    #assert np.allclose(out['test'][1], np.array(meta.predict_disorder(seq)), atol=1e-3)
    assert score_compare(out['test'][1], local_data.S2)
    assert score_compare(out['test'][1], meta.predict_disorder(seq))


def test_batch_prediction():

    nseqs=100
    
    seqs = {}
    for idx, _ in enumerate(range(nseqs)):
        s = build_seq()
        seqs[idx] = s

    # get predictions
    preds = meta.predict_disorder_batch(seqs)
    
    for s in seqs:
        single = meta.predict_disorder(seqs[s])
        assert score_compare(np.array(preds[s][1]), single)
    

def test_batch_idrs():

    seqs = {}
    for idx, _ in enumerate(range(100)):
        s = build_seq()
        seqs[idx] = s

    # predictions
    preds = meta.predict_disorder_batch(seqs, return_domains=True)
    
    for s in seqs:
        single = meta.predict_disorder_domains(seqs[s])

        p = preds[s]
        for idx in range(len(p.disordered_domains)):
            assert p.disordered_domains[idx] == single.disordered_domains[idx]
            assert p.disordered_domain_boundaries[idx] == single.disordered_domain_boundaries[idx] 

        for idx in range(len(p.folded_domains)):
            assert p.folded_domains[idx] == single.folded_domains[idx]
            assert p.folded_domain_boundaries[idx] == single.folded_domain_boundaries[idx]
            





def test_big_test_batch():
    """
    Big tests that compares previously computed disordered scores for 100 sequences
    with the current testable version. This is the most robust test to ensure that
    the current version reproduces scores of other versions of metapredict

    """
    scores = np.load(onehundred_scores, allow_pickle=True).tolist()
    seqs = protfasta.read_fasta(onehundred_seqs)



    batch_predictions = meta.predict_disorder_batch(seqs)

    for idx, k in enumerate(seqs):
        assert np.allclose(scores[idx], batch_predictions[k][1], atol=0.003)



            
