

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

    assert disorder[0] == 0.989

    assert len(meta.predict_disorder_domains_from_external_scores(disorder)) == 3


    idrs = meta.predict_disorder_domains_from_external_scores(disorder)
    assert len(idrs[1]) == 3

    assert idrs[1][0][0] == 0
    assert idrs[1][0][1] == 103

    assert idrs[1][1][0] == 290
    assert idrs[1][1][1] == 327

    assert idrs[1][2][0] == 349
    assert idrs[1][2][1] == 393

    
    with pytest.raises(MetapredictError):
        meta.predict_disorder_domains_from_external_scores(disorder, sequence='')

    with pytest.raises(MetapredictError):
        meta.predict_disorder_domains_from_external_scores(disorder, sequence=20)
        
    idrs = meta.predict_disorder_domains_from_external_scores(disorder, sequence=local_sequence)
    assert idrs[1][0][2] == 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTY'


    idrs = meta.predict_disorder_domains_from_external_scores(disorder, disorder_threshold=1, sequence=local_sequence)
    assert len(idrs[1]) == 1
    assert idrs[1][0][2] == 'ELPPGSTKRALPNNTSSSPQPKK'


    idrs = meta.predict_disorder_domains_from_external_scores(disorder, disorder_threshold=0, sequence=local_sequence)
    assert len(idrs[1]) == 1
    assert idrs[1][0][2] == local_sequence
