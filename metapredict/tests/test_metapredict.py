"""
Unit and regression test for the metapredict package.

This is extremely underdone at this point... Sorry about that :'(
"""

# Import package, test suite, and other packages as needed
import metapredict
from metapredict import meta
import metapredict.backend.uniprot_predictions
from metapredict.backend.uniprot_predictions import fetch_sequence
import pytest
import sys
import os
from . import local_data


current_filepath = os.getcwd()
fasta_filepath = "{}/input_data/testing.fasta".format(current_filepath)

def test_metapredict_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "metapredict" in sys.modules


# test the legacy metapredict predictor
def test_legacy_metapredict_predictor():
    # testing with normalization
    assert meta.predict_disorder('AERDEDNRSKEKKRNKKTNGAGDEHRDKPWSNNSTHPTHRKNEGPMHGDP', legacy=True) == local_data.S0
    # testing without normalization
    assert meta.predict_disorder('AERDEDNRSKEKKRNKKTNGAGDEHRDKPWSNNSTHPTHRKNEGPMHGDP', normalized=False, legacy=True) == local_data.S1
# test the new metapredict predictor
def test_metapredict_predictor():
    # testing with normalization
    assert meta.predict_disorder('RDCAPNNGKKMDNQQHGDVSNQSDNRDSVQQQPPQMAGSQERQKSTESQQSPRSKENKQQAGHSHPESMPRSMSEKEPEMQHDESTGMQNHNRGMQSQDP') == local_data.S2
    # testing without normalization
    assert meta.predict_disorder('RDCAPNNGKKMDNQQHGDVSNQSDNRDSVQQQPPQMAGSQERQKSTESQQSPRSKENKQQAGHSHPESMPRSMSEKEPEMQHDESTGMQNHNRGMQSQDP', normalized=False) == local_data.S3


def test_metapredict_functions():
    # make sure the disorder domains prediction works
    testseq = 'MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY'
    DisObj = meta.predict_disorder_domains(testseq, return_numpy=False)
    assert DisObj.disorder == local_data.S4
    
    # pytest doesn't like the np.array, so just goign to check the sum of the disorder instead.
    assert round(sum(DisObj.disorder)) == 32
    # test boundaries functionality
    assert DisObj.disordered_domain_boundaries[0] == [0, 19]
    assert DisObj.folded_domain_boundaries[0] == [19, 104]
    # test domain sequence functionality
    assert DisObj.disordered_domains == ['MKAPSNGFLPSSNEGEKKP']
    assert DisObj.folded_domains == ['INSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY']
    # test return sequence functionality
    assert DisObj.sequence == 'MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPPVGSLVVYFPQGHSEQVAASMQKQTDFIPNYPNLPSKLICLLHSVTLHADTETDEVYAQMTLQPVNKY'

    # make sure the uniprot preidction works
    assert meta.predict_disorder_uniprot('Q8N6T3') == local_data.disorder_Q8N6T3
    # make sure the uniprot predictions with legacy predictor works
    assert meta.predict_disorder_uniprot('Q8N6T3', legacy=True) == local_data.disorder_Q8N6T3_legacy
    # make sure fetching uniprot sequence works
    ARFGAP1 = 'MASPRTRKVLKEVRVQDENNVCFECGAFNPQWVSVTYGIWICLECSGRHRGLGVHLSFVRSVTMDKWKDIELEKMKAGGNAKFREFLESQEDYDPCWSLQEKYNSRAAALFRDKVVALAEGREWSLESSPAQNWTPPQPRTLPSMVHRVSGQPQSVTASSDKAFEDWLNDDLGSYQGAQGNRYVGFGNTPPPQKKEDDFLNNAMSSLYSGWSSFTTGASRFASAAKEGATKFGSQASQKASELGHSLNENVLKPAQEKVKEGKIFDDVSSGVSQLASKVQGVGSKGWRDVTTFFSGKAEGPLDSPSEGHSYQNSGLDHFQNSNIDQSFWETFGSAEPTKTRKSPSSDSWTCADTSTERRSSDSWEVWGSASTNRNSNSDGGEGGEGTKKAVPPAVPTDDGWDNQNW'
    assert fetch_sequence('Q8N6T3') == ARFGAP1
    # make sure percent disorder predictions work

    expected = {0.05 : 87.4,
                0.1 : 82.5,
                0.2 : 74.9,
                0.3 : 63.5}

    # test out percent disorder using the legacy predictor
    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh, legacy=True), 1) == expected[thresh]

    expected = {0.05 : 90.1,
                0.1 : 81.8,
                0.2 : 76.1,
                0.3 : 73.6}

    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh), 1) == expected[thresh]
             

    # expected thresholds change a tad when disorder_domains used
    expected = {0.05 : 90.1,
                0.1 : 88.2,
                0.2 : 76.6,
                0.3 : 70.7}
    
    for thresh in [0.05, 0.1, 0.2, 0.3]:
        assert round(meta.percent_disorder(ARFGAP1, disorder_threshold=thresh, mode='disorder_domains'), 1) == expected[thresh]

    
    # make sure fasta stuff works for legacy
    assert meta.predict_disorder_fasta(fasta_filepath, legacy=True) == {'Q8N6T3': local_data.disorder_Q8N6T3_legacy}

    # make sure fasta stuff works for new predictor
    assert meta.predict_disorder_fasta(fasta_filepath, legacy=False) == {'Q8N6T3': local_data.disorder_Q8N6T3}





