# Import package, test suite, and other packages as needed
import metapredict
from metapredict import meta

import numpy as np

from metapredict.backend.cython.domain_definition import build_domains_from_values 
from metapredict.backend.domain_definition import __build_domains_from_values as  domain_definition


import pytest

from . import build_seq

def test_domain_decomposition():
    """
    Function whose sole perpose is to make sure that the cython and 
    python implementations for the domain decomposition code return 
    the same thing.

    """

    for _ in range(50):
        s = build_seq()
    
        disorder = meta.predict_disorder(s, return_numpy=True).astype(np.double)
    
        for thresh in [0, 0.1, 0.2, 0.5, 0.9, 1.0]:
            cyth = build_domains_from_values(disorder, thresh)
            pyth = domain_definition(disorder, thresh)
        
            for x in range(len(cyth[0])):

                
                if cyth[0][x] != pyth[0][x]:
                    print(f"Threshold used: {thresh}")
                    print(s)
                    assert cyth[0][x] == pyth[0][x]
                

            for x in range(len(cyth[1])):
                if cyth[1][x] != pyth[1][x]:
                    print(f"Threshold used: {thresh}")
                    print(s)
                    assert cyth[1][x] == pyth[1][x]
    
