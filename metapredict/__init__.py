##
## metapredict
## A protein disorder predictor based on a BRNN (IDP-Parrot) trained on the consensus disorder values from 
## 8 disorder predictors from 12 proteomes.
##

# import user-facing functions
from .meta import *
from metapredict.backend.meta_predict_disorder import get_metapredict_legacy_network_version
from metapredict.backend.metameta_hybrid_predict import get_metapredict_network_version



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
def print_performance(seq_len=500, num_seqs=100, verbose=True, batch=True, legacy=False, batch_mode=None, variable_length=False):
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

    batch : bool
        Flag which, if set to true, means we use batch mode, else we use serial mode.

    legacy : bool
        Flag which determines if legacy (v1) or updated (v2) metapredict networks
        are used.

    batch_mode : int
        Flag which defines which batch_mode algorithm to use for batched predictions.
        Default = None which means the mode is dynamically picked. Can also be 1 or 2.

    variable_length : bool
        Flag which, if provided, means sequences vary between 20 and seq_len length.

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
        if variable_length:
            local_n = random.randint(20,seq_len)
        else:
            local_n = n
        return "".join([random.choice(VALID_AMINO_ACIDS) for i in range(local_n)])

    seqs = []
    n_res = 0
    for i in range(num_seqs):
        s = genseq(seq_len)
        seqs.append(s)
        n_res = n_res + len(s)

    start = time.time()

    if batch:
        predict_disorder_batch(seqs, batch_mode=batch_mode)

    else:
        for i in seqs:
            predict_disorder(i, legacy=legacy)

    end = time.time()
    r_per_second = (n_res)/(end - start)

    if verbose:
        print(f'Predicting {r_per_second:f} residues per second!')

    return r_per_second
    
def print_metapredict_legacy_network_version():
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

    return get_metapredict_legacy_network_version()


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
