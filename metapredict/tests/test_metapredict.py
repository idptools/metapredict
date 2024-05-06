"""
Unit and regression test for the metapredict package.

This is extremely underdone at this point... Sorry about that :'(
"""

# Import package, test suite, and other packages as needed
import metapredict
from metapredict import meta
from getSequence import getseq as fetch_sequence
import pytest
import sys
import os
from . import local_data
import random
import string
import numpy as np

import protfasta

from metapredict.metapredict_exceptions import MetapredictError


current_filepath = os.getcwd()
fasta_filepath = "{}/input_data/testing.fasta".format(current_filepath)

onehundred_seqs = "{}/input_data/test_seqs_100.fasta".format(current_filepath)

# updated scores to be v3. 
onehundred_scores = "{}/input_data/test_scores_100_v3.npy".format(current_filepath)


def test_metapredict_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "metapredict" in sys.modules



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
        Returns true if all elements are less than 1e-3, else 
        returns False
    
    """
    
    return np.allclose(np.array(s1), np.array(s2), atol=1e-3)
    
    

# test the legacy metapredict predictor
def test_legacy_metapredict_predictor():
    # testing with normalization
    assert score_compare(meta.predict_disorder('AERDEDNRSKEKKRNKKTNGAGDEHRDKPWSNNSTHPTHRKNEGPMHGDP', version=1), local_data.S0) == True
    # testing without normalization
    assert score_compare(meta.predict_disorder('AERDEDNRSKEKKRNKKTNGAGDEHRDKPWSNNSTHPTHRKNEGPMHGDP', normalized=False, version=1), local_data.S1) == True

    with pytest.raises(MetapredictError):
        meta.predict_disorder('')


# test the new metapredict predictor
def test_metapredict_predictor():
    # testing with normalization
    assert score_compare(meta.predict_disorder('RDCAPNNGKKMDNQQHGDVSNQSDNRDSVQQQPPQMAGSQERQKSTESQQSPRSKENKQQAGHSHPESMPRSMSEKEPEMQHDESTGMQNHNRGMQSQDP'), local_data.S2)==True
    # testing without normalization
    assert score_compare(meta.predict_disorder('RDCAPNNGKKMDNQQHGDVSNQSDNRDSVQQQPPQMAGSQERQKSTESQQSPRSKENKQQAGHSHPESMPRSMSEKEPEMQHDESTGMQNHNRGMQSQDP', normalized=False), local_data.S3)==True


def test_metapredict_functions():
    # make sure the disorder domains prediction works
    testseq = 'MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY'
    DisObj = meta.predict_disorder_domains(testseq, return_numpy=False)
    assert score_compare(DisObj.disorder, local_data.S4)==True
    
    # pytest doesn't like the np.array, so just goign to check the sum of the disorder instead.
    assert round(sum(DisObj.disorder)) == 32
    # test boundaries functionality
    # updated for v3
    assert DisObj.disordered_domain_boundaries[0] == [0, 22]
    # updated for v3
    assert DisObj.folded_domain_boundaries[0] == [22, 104]
    # test domain sequence functionality
    assert DisObj.disordered_domains == ['MKAPSNGFLPSSNEGEKKPINS']
    assert DisObj.folded_domains == ['QLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY']
    # test return sequence functionality
    assert DisObj.sequence == 'MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY'

    # make sure the uniprot preidction works
    assert score_compare(meta.predict_disorder_uniprot('Q8N6T3'), local_data.disorder_Q8N6T3)==True
    # make sure the uniprot predictions with legacy predictor works
    assert score_compare(meta.predict_disorder_uniprot('Q8N6T3', version=1), local_data.disorder_Q8N6T3_legacy)==True
    # make sure fetching uniprot sequence works
    ARFGAP1 = 'MASPRTRKVLKEVRVQDENNVCFECGAFNPQWVSVTYGIWICLECSGRHRGLGVHLSFVRSVTMDKWKDIELEKMKAGGNAKFREFLESQEDYDPCWSLQEKYNSRAAALFRDKVVALAEGREWSLESSPAQNWTPPQPRTLPSMVHRVSGQPQSVTASSDKAFEDWLNDDLGSYQGAQGNRYVGFGNTPPPQKKEDDFLNNAMSSLYSGWSSFTTGASRFASAAKEGATKFGSQASQKASELGHSLNENVLKPAQEKVKEGKIFDDVSSGVSQLASKVQGVGSKGWRDVTTFFSGKAEGPLDSPSEGHSYQNSGLDHFQNSNIDQSFWETFGSAEPTKTRKSPSSDSWTCADTSTERRSSDSWEVWGSASTNRNSNSDGGEGGEGTKKAVPPAVPTDDGWDNQNW'
    # updated to use getSequence functionality
    assert fetch_sequence('Q8N6T3')[1] == ARFGAP1
    # make sure percent disorder predictions work

    expected = {0.05 : 87.4,
                0.1 : 82.5,
                0.2 : 74.9,
                0.3 : 63.5}

    # test out percent disorder using the legacy predictor
    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh, version=1), 1) == expected[thresh]

    expected = {0.05 : 90.1,
                0.1 : 81.8,
                0.2 : 76.1,
                0.3 : 73.6}

    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh, version=2), 1) == expected[thresh]
             

    expected = {0.05 : 94.3,
                0.1 : 87.9,
                0.2 : 76.4,
                0.3 : 74.6}

    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh, version=3), 1) == expected[thresh]
            

    # expected thresholds change a tad when disorder_domains used
    expected = {0.05 : 90.1,
                0.1 : 88.2,
                0.2 : 76.6,
                0.3 : 70.7}
    
    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh, mode='disorder_domains', version=2), 1) == expected[thresh]


    # expected thresholds change a tad when disorder_domains used
    expected = {0.05 : 100.0,
                0.1 : 88.4,
                0.2 : 76.4,
                0.3 : 74.6}
    
    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh, mode='disorder_domains', version=3), 1) == expected[thresh]

    
    # make sure fasta stuff works for legacy
    # updated May 2023 to deal with the fact that predict_disorder_fasta now returns a dictionary where values are np.ndarrays
    # updated 2024 to change legacy=False to version = 1
    assert np.allclose(meta.predict_disorder_fasta(fasta_filepath, version=1)['Q8N6T3'][1], np.array(local_data.disorder_Q8N6T3_legacy, dtype=np.float32))

    # make sure FASTA stuff works for non-legacy predictions
    # updated May 2023 to deal with the fact that predict_disorder_fasta now returns a dictionary where values are np.ndarrays
    # updated 2024 to change legacy=False to version = 2
    assert np.allclose(meta.predict_disorder_fasta(fasta_filepath, version=2)['Q8N6T3'][1], np.array(local_data.disorder_Q8N6T3_2, dtype=np.float32))


    # added 2024 to change for v3
    assert np.allclose(meta.predict_disorder_fasta(fasta_filepath, version=3)['Q8N6T3'][1], np.array(local_data.disorder_Q8N6T3_3, dtype=np.float32))


def test_predict_disorder_fail():

    # make sure we get gracefull fail on empty string
    with pytest.raises(MetapredictError):
        DisObj = meta.predict_disorder('')


def test_predict_all_fail():

    # make sure we get gracefull fail on empty string
    with pytest.raises(MetapredictError):
        DisObj = meta.predict_all('')



def test_predict_pLDDT_fail():

    # make sure we get gracefull fail on empty string
    with pytest.raises(MetapredictError):
        DisObj = meta.predict_pLDDT('')

    
def test_predict_disorder_return_numpy():
    testseq = 'MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY'

    x = meta.predict_disorder(testseq, return_numpy=True)
    assert isinstance(x,np.ndarray)

    x = meta.predict_disorder(testseq, return_numpy=True, version=1)
    assert isinstance(x,np.ndarray)

    x = meta.predict_disorder(testseq, return_numpy=True, version=1, normalized=False)
    assert isinstance(x,np.ndarray)

    x = meta.predict_disorder(testseq, return_numpy=True, version=2, normalized=False)
    assert isinstance(x,np.ndarray)

    x = meta.predict_disorder(testseq, return_numpy=True, version=3, normalized=False)
    assert isinstance(x,np.ndarray)

def test_predict_pLDDT():
    testseq = 'MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY'

    x = meta.predict_pLDDT(testseq, return_numpy=True)
    assert isinstance(x,np.ndarray)

    x = meta.predict_pLDDT(testseq, return_numpy=True)
    assert isinstance(x,np.ndarray)

    x = meta.predict_pLDDT(testseq, return_numpy=True,  normalized=False)
    assert isinstance(x,np.ndarray)



def test_predict_disorder_domains_fail():

    testseq = 'MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY'

    # make sure we get gracefull fail on empty string
    with pytest.raises(MetapredictError):
        DisObj = meta.predict_disorder_domains('', return_numpy=False)

    # make sure we get gracefull fail on empty string
    with pytest.raises(MetapredictError):
        DisObj = meta.predict_disorder_domains(testseq, return_numpy=False, disorder_threshold=2)



def test_predict_disorder_domains_random_seqs():

    N = 200
    n_seqs = 500

    for i in range(n_seqs):
        local_seq = ''.join(random.choices(['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'], k=N))
        DisObj = meta.predict_disorder_domains(local_seq, return_numpy=False, disorder_threshold=1)        

        # check no residues are in any IDR
        assert len(DisObj.disordered_domains) == 0
        assert meta.percent_disorder(local_seq, mode='disorder_domains', disorder_threshold=1) == 0


    for i in range(n_seqs):
        local_seq = ''.join(random.choices(['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'], k=N))
        DisObj = meta.predict_disorder_domains(local_seq, return_numpy=False, disorder_threshold=0)

        # technically we can have non-IDRs with a threshold of 0 if there is a region where disorder score is
        # literally 0
        if len(DisObj.disordered_domains[0]) != N:
            print(f'If this fails we have a weird bug; sequence: {local_seq}')
            assert np.sum(np.array(DisObj.disorder) > 0) < N
        else:
            # check all residues are in one IDR
            assert len(DisObj.disordered_domains[0]) == N

            assert meta.percent_disorder(local_seq, mode='disorder_domains', disorder_threshold=0) == 100


def test_percent_disorder_fail():

    # make sure we get gracefull fail on empty string
    with pytest.raises(MetapredictError):
        DisObj = meta.percent_disorder('')


def test_big_test():
    """
    Big tests that compares previously computed disordered scores for 100 sequences
    with the current testable version. This is the most robust test to ensure that
    the current version reproduces scores of other versions of metapredict

    ## update may 2023
    Note; we had to pull the atol down to 0.0001 for Py310 which probably reflects
    some changes under the hood in how floats are dealt with in the C/python/Cython
    exchange and/or in PyTorch. This is not an issue, but we're just documenting it
    in case this comes up in the future
    

    """

    scores = np.load(onehundred_scores, allow_pickle=True).tolist()
    seqs = protfasta.read_fasta(onehundred_seqs)

    for idx, k in enumerate(seqs):
        local_score = meta.predict_disorder(seqs[k])
        assert np.allclose(scores[idx], meta.predict_disorder(seqs[k], return_numpy=True), atol=0.0001)



    