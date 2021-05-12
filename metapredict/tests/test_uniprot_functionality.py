"""
Unit and regression test for the metapredict package.

This is extremely underdone at this point... Sorry about that :'(
"""

# Import package, test suite, and other packages as needed
from metapredict import meta
from metapredict.metapredict_exceptions import MetapredictError
import pytest
import sys
import os
import numpy as np


current_filepath = os.getcwd()
fasta_filepath = "{}/testing.fasta".format(current_filepath)

P53_UID = 'P04637'

def test_metapredict_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "metapredict" in sys.modules


# ....................................................................................
#
def test_predict_disorder_uniprot():

    # checks that this fails when an invalid uniprot accession is passed
    with pytest.raises(MetapredictError):
        meta.predict_disorder_uniprot('aaaa')


    # checks that when we pull p53 we get 393 residues of sweet,
    # sweet disorder prediction
    assert len(meta.predict_disorder_uniprot(P53_UID)) == 393

    # check summed disorder is right
    assert np.sum(meta.predict_disorder_uniprot(P53_UID)) == 172.965


    # check summed disorder is right when we don't normalize (these are not magic values,
    # just the expected 'truth' for the 1.0 release
    assert np.sum(meta.predict_disorder_uniprot(P53_UID,normalized=False)) == 173.524


# ....................................................................................
#
def test_graph_disorder_uniprot_():

    # checks that this fails when an invalid uniprot accession is passed
    with pytest.raises(MetapredictError):
        meta.graph_disorder_uniprot('aaaa')


    # probably should have some tests here...?


# ....................................................................................
#
def test_predict_disorder_domains_uniprot_():

    # checks that this fails when an invalid uniprot accession is passed
    with pytest.raises(MetapredictError):
        meta.predict_disorder_domains_uniprot('aaaa')


    # checks that when we pull p53 we get 393 residues of sweet,
    # sweet disorder prediction

    dis_domains = meta.predict_disorder_domains_uniprot(P53_UID) 
    assert len(dis_domains[0]) == 393
    assert len(dis_domains[1]) == 393
    assert np.sum(dis_domains[0]) == 172.965
    assert np.sum(dis_domains[1]) == 173.04537763974946

    # did we find 2 IDRs
    assert len(dis_domains[2]) == 2

    # IDR1
    assert dis_domains[2][0][2] == 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKT'
    assert dis_domains[2][0][0] == 0
    assert dis_domains[2][0][1] == 102

    # IDR2
    assert dis_domains[2][1][2] == 'PGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD'
    assert dis_domains[2][1][0] == 277
    assert dis_domains[2][1][1] == 393

    # FD1
    assert dis_domains[3][0][2] == 'YQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCAC'
    assert dis_domains[3][0][0] == 102
    assert dis_domains[3][0][1] == 277

