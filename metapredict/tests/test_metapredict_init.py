"""
Unit and regression test for the metapredict package.

This is extremely underdone at this point... Sorry about that :'(
"""

# Import package, test suite, and other packages as needed
import metapredict
import sys


def test_metapredict_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "metapredict" in sys.modules

def test_print_performance():
    """Sample test, will always pass so long as import statement worked"""
    metapredict.print_performance()
    metapredict.print_performance(seq_len=30)
    metapredict.print_performance(seq_len=30, num_seqs=50)
    metapredict.print_performance(num_seqs=50, variable_length=True)
    metapredict.print_performance(num_seqs=50, disable_batch=True)


def test_print_performance_backend():    
    metapredict.print_performance_backend()
    metapredict.print_performance_backend(seq_len=30)
    metapredict.print_performance_backend(seq_len=30, num_seqs=50)
    metapredict.print_performance_backend(num_seqs=50, variable_length=True)
    metapredict.print_performance_backend(num_seqs=50, disable_batch=True)


def test_print_legacy_network_version():
    """Sample test, will always pass so long as import statement worked"""

    assert 'V1' == metapredict.print_metapredict_legacy_network_version()
    assert 'V3' == metapredict.print_metapredict_network_version()


    
