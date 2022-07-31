

import metapredict as meta
from metapredict.metapredict_exceptions import MetapredictError

import pytest
import sys
import os


current_filepath = os.getcwd()
odinpred_file = "{}/input_data/DisorderPredictionssp_P04637_P53_HUMANC.txt".format(current_filepath)



def test_predict_disordered_domains_external_scores_basic():
    
    # read the file into Python
    with open(odinpred_file, 'r') as fh:
        content = fh.readlines()

    disorder = [float(x.strip().split()[3]) for x in content[1:]]
    local_sequence = "".join([x.strip().split()[0] for x in content[1:]])

    # make sure first disorder score is as expected
    assert disorder[0] == 0.989

    # get the IDRs from DisorderObject
    DisObj = meta.predict_disorder_domains_from_external_scores(disorder, sequence = local_sequence)

    # get idrs from DisorderedObject
    idrs = DisObj.disordered_domains

    # make sure there are 3 IDRs
    assert len(idrs) == 3

    # make sure IDR boundaries are as expected.
    idr_boundaries = DisObj.disordered_domain_boundaries

    assert idr_boundaries[0][0] == 0
    assert idr_boundaries[0][1] == 103

    assert idr_boundaries[1][0] == 290
    assert idr_boundaries[1][1] == 327

    assert idr_boundaries[2][0] == 349
    assert idr_boundaries[2][1] == 393

    # check the IDR sequence is as expected at first IDR
    assert idrs[0] == 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTY'


    # check that passing a disorder threshold of 1 we get no IDRs 
    DisObj_cutoff_1 = meta.predict_disorder_domains_from_external_scores(disorder, disorder_threshold=1, sequence=local_sequence)
    assert len(DisObj_cutoff_1.disordered_domains) == 0


    # check that making threshold = 0 makes all seqs IDRs
    DisObj_cutoff_0 = meta.predict_disorder_domains_from_external_scores(disorder, disorder_threshold=0, sequence=local_sequence)


    assert len(DisObj_cutoff_0.disordered_domains) == 1
    assert DisObj_cutoff_0.disordered_domains[0]==local_sequence





def test_predict_disordered_domains_external_scores_failsafe():
    """
    Tests that things fail gracefully

    """

    # read the file into Python
    with open(odinpred_file, 'r') as fh:
        content = fh.readlines()

    disorder = [float(x.strip().split()[3]) for x in content[1:]]
    local_sequence = "".join([x.strip().split()[0] for x in content[1:]])


    with pytest.raises(MetapredictError):
        meta.predict_disorder_domains_from_external_scores(disorder, sequence='')

    with pytest.raises(MetapredictError):
        meta.predict_disorder_domains_from_external_scores(disorder, sequence=20)

    # check it handles an empty disorder list/vector
    with pytest.raises(MetapredictError):
        meta.predict_disorder_domains_from_external_scores([], sequence=20)
    
