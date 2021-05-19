import os
import pytest
import protfasta

import metapredict as meta
from metapredict.meta import MetapredictError

current_filepath = os.getcwd()
fasta_filepath = "{}/input_data/testing.fasta".format(current_filepath)
test_sequence = protfasta.read_fasta(fasta_filepath)['Q8N6T3']


def test_graph_disorder_png():

    # can make PNGs
    fn='demo1.png'
    full_fn = 'output/%s'%(fn)
    meta.graph_disorder(test_sequence, output_file=full_fn)
    assert os.path.isfile(full_fn) is True


    full_fn = 'output/demo1_custom_title.png'
    meta.graph_disorder(test_sequence, output_file=full_fn, title='Custom title')

    full_fn = 'output/demo1_disorder_thresh0p5.png'
    meta.graph_disorder(test_sequence, output_file=full_fn, disorder_threshold=0.5)

    full_fn = 'output/demo1_shaded_1_20.png'
    meta.graph_disorder(test_sequence, output_file=full_fn, shaded_regions=[[1,20]])

    full_fn = 'output/demo1_shaded_1_20_80_200.png'
    meta.graph_disorder(test_sequence, output_file=full_fn, shaded_regions=[[1,20], [80,200]])

    full_fn = 'output/demo1_shaded_1_20_80_200_yellow.png'
    meta.graph_disorder(test_sequence, output_file=full_fn, shaded_regions=[[1,20], [80,200]], shaded_region_color='yellow')

    full_fn = 'output/demo1_dpi_500.png'
    meta.graph_disorder(test_sequence, output_file=full_fn, DPI=500)


    with pytest.raises(MetapredictError):
        full_fn = 'output/demo1_disorder_thresh0p5.png'
        meta.graph_disorder(test_sequence, output_file=full_fn, disorder_threshold=2)

    with pytest.raises(MetapredictError):
        full_fn = 'output/demo1_disorder_thresh0p5.png'
        meta.graph_disorder(test_sequence, output_file=full_fn, disorder_threshold=-2)

    # invalid format on shaded_regions
    with pytest.raises(MetapredictError):
        full_fn = 'output/demo1_disorder_thresh0p5.png'
        meta.graph_disorder(test_sequence, output_file=full_fn, shaded_regions=[1,20])

    # shaded extends too low
    with pytest.raises(MetapredictError):
        full_fn = 'output/demo1_disorder_thresh0p5.png'
        meta.graph_disorder(test_sequence, output_file=full_fn, shaded_regions=[-5,20])

    # shaded extends too high
    with pytest.raises(MetapredictError):
        full_fn = 'output/demo1_disorder_thresh0p5.png'
        meta.graph_disorder(test_sequence, output_file=full_fn, shaded_regions=[1,20000])



def test_graph_disorder_other_output_formats():

    # can make PNGs
    fn='demo1.pdf'
    full_fn = 'output/%s'%(fn)
    meta.graph_disorder(test_sequence, output_file=full_fn)
    assert os.path.isfile(full_fn) is True


    fn='demo1.ps'
    full_fn = 'output/%s'%(fn)
    meta.graph_disorder(test_sequence, output_file=full_fn)
    assert os.path.isfile(full_fn) is True
