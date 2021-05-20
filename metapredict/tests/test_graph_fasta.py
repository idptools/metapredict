import os
import pytest
import protfasta

import metapredict as meta
from metapredict.meta import MetapredictError

current_filepath = os.getcwd()
fasta_filepath = "{}/input_data/three_seqs.fasta".format(current_filepath)



def test_graph_fasta_png():

    # can make PNGs
    meta.graph_disorder_fasta(fasta_filepath, output_dir='output/')

    assert os.path.isfile('output/Q8N6T3.png') is True
    assert os.path.isfile('output/p53.png') is True
    assert os.path.isfile('output/sp_P0DMV8_HS71.png') is True


def test_graph_fasta_png_idx():

    # can make PNGs
    meta.graph_disorder_fasta(fasta_filepath, output_dir='output/', indexed_filenames=True)

    assert os.path.isfile('output/1_Q8N6T3.png') is True
    assert os.path.isfile('output/2_p53.png') is True
    assert os.path.isfile('output/3_sp_P0DMV8_HS71.png') is True



def test_graph_fasta_jpg():

    # can make jpgs
    meta.graph_disorder_fasta(fasta_filepath, output_dir='output', output_filetype='ps')

    assert os.path.isfile('output/Q8N6T3.ps') is True
    assert os.path.isfile('output/p53.ps') is True
    assert os.path.isfile('output/sp_P0DMV8_HS71.ps') is True



def test_graph_fasta_pdf():

    # can make PNGs
    meta.graph_disorder_fasta(fasta_filepath, output_dir='output/', output_filetype='pdf')

    assert os.path.isfile('output/Q8N6T3.pdf') is True
    assert os.path.isfile('output/p53.pdf') is True
    assert os.path.isfile('output/sp_P0DMV8_HS71.pdf') is True
