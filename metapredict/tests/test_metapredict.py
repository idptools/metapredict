"""
Unit and regression test for the metapredict package.

This is extremely underdone at this point... Sorry about that :'(
"""

# Import package, test suite, and other packages as needed
import metapredict
from metapredict import meta
import pytest
import sys

def test_metapredict_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "metapredict" in sys.modules

def test_metapredict_predictor():
    #testing with normalization
    assert meta.predict_disorder('AERDEDNRSKEKKRNKKTNGAGDEHRDKPWSNNSTHPTHRKNEGPMHGDP') == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.998, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.938]
    # testing without normalization
    assert meta.predict_disorder('AERDEDNRSKEKKRNKKTNGAGDEHRDKPWSNNSTHPTHRKNEGPMHGDP', normalized=False) == [1.055, 1.097, 1.062, 1.087, 1.068, 1.078, 1.089, 1.04, 1.032, 1.025, 1.006, 1.002, 1.007, 0.998, 1.033, 1.032, 1.039, 1.045, 1.061, 1.088, 1.093, 1.092, 1.096, 1.077, 1.058, 1.033, 1.034, 1.019, 1.057, 1.1, 1.05, 1.074, 1.083, 1.078, 1.103, 1.084, 1.052, 1.047, 1.044, 1.065, 1.082, 1.071, 1.119, 1.126, 1.043, 1.13, 1.208, 1.152, 1.155, 0.938]