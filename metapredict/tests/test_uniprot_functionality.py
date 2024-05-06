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

    # checks that when we pull p53 we get 393 residues of sweet,
    # sweet disorder prediction
    assert len(meta.predict_disorder_uniprot(P53_UID)) == 393

    # check summed disorder is right
    assert np.isclose(np.sum(meta.predict_disorder_uniprot(P53_UID, version=2)),181.7708, 0.0001)

    # check legacy disorder is right
    assert np.isclose(np.sum(meta.predict_disorder_uniprot(P53_UID, version=1)),  172.9651, 0.0001)

    # check summed disorder is right when we don't normalize (these are not magic values,
    # just the expected 'truth' for the 1.0 release
    assert np.isclose(np.sum(meta.predict_disorder_uniprot(P53_UID, normalized=False, version=1)),173.5245, 0.0001)


# ....................................................................................
#
def test_graph_disorder_uniprot_():
    # probably should have some tests here...?
    # ... yeah... we probably should. I'm on hour 4 of updating
    # everything from v2 to v3 though, so today is not that day.
    pass
    


# ....................................................................................
#
def test_predict_disorder_domains_uniprot_():

    # checks that when we pull p53 we get 393 residues of sweet,
    # sweet disorder prediction

    dis_domains = meta.predict_disorder_domains_uniprot(P53_UID, version=2) 
    assert len(dis_domains.sequence) == 393
    assert np.isclose(np.sum(dis_domains.disorder), 181.7708, 0.001)

    # did we find 2 IDRs
    assert len(dis_domains.disordered_domains) == 2

    # get IDRs
    IDRs = dis_domains.disordered_domains
    #get idr boundaries
    disorder_boundaries = dis_domains.disordered_domain_boundaries

    # IDR1
    assert IDRs[0] == 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQK'
    assert disorder_boundaries[0][0] == 0
    assert disorder_boundaries[0][1] == 101

    # IDR2
    assert IDRs[1] == 'DRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD'
    assert disorder_boundaries[1][0] == 280
    assert disorder_boundaries[1][1] == 393

    # get folded domains and sequence
    folded_seq = dis_domains.folded_domains
    # get folded boundaries
    folded_boundaries = dis_domains.folded_domain_boundaries


    # FD1
    assert folded_seq[0] == 'TYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGR'
    assert folded_boundaries[0][0] == 101
    assert folded_boundaries[0][1] == 280

