import os
import numpy as np
import pytest
import protfasta

import metapredict as meta
from metapredict.meta import MetapredictError

current_filepath = os.getcwd()
fasta_filepath = "{}/input_data/three_seqs.fasta".format(current_filepath)



def test_predict_disorder_fasta():

    # can make PNGs
    x = meta.predict_disorder_fasta(fasta_filepath)

    assert len(x) == 3

    
    expected = {'Q8N6T3':170.995, 'p53':172.965, 'sp|P0DMV8|HS71A_HUMAN Heat shock 70 kDa protein 1A OS=Homo sapiens OX=9606 GN=HSPA1A PE=1 SV=1':100.18199999999999}
    
    for n in expected:
        assert np.isclose(np.sum(x[n]),expected[n])


def test_predict_disorder_fasta_write():

    # can make PNGs    
    meta.predict_disorder_fasta(fasta_filepath, output_file='output/test.csv')
    assert os.path.isfile('output/test.csv') is True
