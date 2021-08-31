##
## metapredict
## A protein disorder predictor based on a BRNN (IDP-Parrot) trained on the consensus disorder values from 
## 8 disorder predictors from 12 proteomes.
##

# import user-facing functions
from .meta import *
from metapredict.backend.meta_predict_disorder import get_metapredict_network_version


import os
import sys


# To crash on LIBOMP error set this to False
IGNORE_LIBOMP_ERROR = True


# ------------------------------------------------------------
#
# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions


# Handle omplib error 
if IGNORE_LIBOMP_ERROR:
    if sys.platform == 'darwin':
        os.environ['KMP_DUPLICATE_LIB_OK']='True'


# Standardized function to check performance
def print_performance(seq_len=500, num_seqs=100, verbose=True):
    """
    Function that lets you test metapredicts performance on your local hardware.

    Parameters
    --------------
    seqlen : int 
        Length of each random sequence to be tested. Default = 500.

    num_seqs : int
        Number of sequences to compute over. Default = 100.

    verbose : bool
        Flag which, if true, means the function prints a summary when finished. If 
        false simply returns an integer

    Returns
    ---------------
    int
        Returns the nearest number of sequences-per-second metapredict is currently
        predicting. For ref, on a spring 2020 MBP this value was ~10,000 sequences per
        second.

    """

    # this is a bit bad but, only import random is this FX is called
    import random
    import time
    VALID_AMINO_ACIDS = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']

    def genseq(n):
        """
        Function that generates a random 
        """    
        return "".join([random.choice(VALID_AMINO_ACIDS) for i in range(n)])

    seqs = []
    for i in range(num_seqs):
        seqs.append(genseq(seq_len))

    start = time.time()
    for i in seqs:
        predict_disorder(i)

    end = time.time()
    r_per_second = (seq_len*num_seqs)/(end - start)

    if verbose:
        print('Predicting %i residues per second!'%(r_per_second))

    return r_per_second
    
def print_metapredict_network_version():
    """
    Function that returns a string with the current trained network version
    used in disorder prediction. This is useful to know if updated versions
    of the network are provided, which will always accompany a version bump
    so prior versions of the code will always be available.

    Returns
    ---------
    str 
        Returns a string in the format v<version information>
    
    """

    return get_metapredict_network_version()
